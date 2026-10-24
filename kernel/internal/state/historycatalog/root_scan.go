// Ported from DeepSeek-Reasonix (MIT) — upstream PR #14086.
package historycatalog

import (
	"context"
	"errors"
	"os"
	"path/filepath"
	"runtime"
	"slices"

	"tempora/internal/base/backgroundwork"
	"tempora/internal/state/sessionstore"
	"tempora/internal/state/store"
)

// rootReconcileScan is one pass over a directory's transcripts. The scan keeps
// its generation across the yield points, so an interrupted scan can tell
// which sources it did reach.
type rootReconcileScan struct {
	root       Root
	paths      []string
	signature  string
	generation int64
	started    int64
	indexed    int
}

// reconcileRoot scans one directory. The scan is split so an interruption
// leaves the root in the scanning state and never marks an unvisited source
// missing: only a scan that reached its end may retire sources.
func (c *Catalog) reconcileRoot(ctx context.Context, root Root) error {
	var scan *rootReconcileScan
	err := c.scheduler().Do(ctx, backgroundwork.Rebuild, func(job context.Context) error {
		var err error
		scan, err = c.startRootScan(job, root)
		return err
	})
	if err != nil || scan == nil {
		return err
	}
	for i, path := range scan.paths {
		if err := ctx.Err(); err != nil {
			return err
		}
		c.indexPending(ctx, root, scan.generation)
		if err := c.indexPath(ctx, root, path, scan.generation, -1); err == nil {
			scan.indexed++
		}
		if (i+1)%32 == 0 {
			runtime.Gosched()
		}
	}
	if err := ctx.Err(); err != nil {
		return err
	}
	return c.scheduler().Do(ctx, backgroundwork.Rebuild, func(job context.Context) error { return c.finishRootScan(job, scan) })
}

func (c *Catalog) startRootScan(ctx context.Context, root Root) (*rootReconcileScan, error) {
	entries, err := os.ReadDir(root.Path)
	if err != nil && !errors.Is(err, os.ErrNotExist) {
		c.setError(err)
		return nil, err
	}
	paths := make([]string, 0, len(entries))
	for _, entry := range entries {
		if err := ctx.Err(); err != nil {
			return nil, err
		}
		if entry.IsDir() || !store.IsSessionTranscriptName(entry.Name()) ||
			store.IsSubagentTranscriptName(entry.Name()) {
			continue
		}
		path := filepath.Join(root.Path, entry.Name())
		if !root.Archive && !sessionstore.IsVisibleSession(path) {
			continue
		}
		paths = append(paths, path)
	}
	slices.Sort(paths)
	signature := historyRootSignature(paths)
	var previousSig, previousState string
	_ = c.db.QueryRowContext(ctx, `SELECT signature,state FROM history_roots WHERE path=?`, root.Path).Scan(&previousSig, &previousState)
	if previousState == "ready" && previousSig == signature && signature != "" {
		return nil, nil
	}
	now := c.opts.Now().UnixMilli()
	tx, err := c.db.BeginTx(ctx, nil)
	if err != nil {
		return nil, err
	}
	var generation int64
	if err := tx.QueryRowContext(ctx, `INSERT INTO history_roots(path,source,scope,workspace_root,signature,scan_generation,state,total)
        VALUES(?,?,?,?,?,1,'scanning',?) ON CONFLICT(path) DO UPDATE SET source=excluded.source,scope=excluded.scope,
        workspace_root=excluded.workspace_root,signature=excluded.signature,scan_generation=history_roots.scan_generation+1,state='scanning',error='',total=excluded.total
        RETURNING scan_generation`, root.Path, root.Source, root.Scope, root.WorkspaceRoot, signature, len(paths)).Scan(&generation); err != nil {
		_ = tx.Rollback()
		return nil, err
	}
	if err := tx.Commit(); err != nil {
		return nil, err
	}
	return &rootReconcileScan{root: root, paths: paths, signature: signature, generation: generation, started: now}, nil
}

// finishRootScan retires the sources a completed scan did not see. It runs
// only after every source of the scan has been visited.
func (c *Catalog) finishRootScan(ctx context.Context, scan *rootReconcileScan) error {
	root, generation, now, signature, indexed := scan.root, scan.generation, scan.started, scan.signature, scan.indexed
	tx, err := c.db.BeginTx(ctx, nil)
	if err != nil {
		return err
	}
	if _, err := tx.ExecContext(ctx, `UPDATE history_sources SET missing_since=CASE WHEN missing_since=0 THEN ? ELSE missing_since END,
        health='missing' WHERE root=? AND seen_generation<>?`, now, root.Path, generation); err != nil {
		_ = tx.Rollback()
		return err
	}
	cutoff := now - c.opts.MissingGrace.Milliseconds()
	if _, err := tx.ExecContext(ctx, `DELETE FROM history_fts WHERE rowid IN (
        SELECT d.id FROM history_documents d JOIN history_sources s ON s.path=d.source_path
        WHERE s.root=? AND s.seen_generation<>? AND s.missing_since>0 AND s.missing_since<=?
    )`, root.Path, generation, cutoff); err != nil {
		_ = tx.Rollback()
		return err
	}
	if _, err := tx.ExecContext(ctx, `DELETE FROM history_documents WHERE source_path IN (
        SELECT path FROM history_sources WHERE root=? AND seen_generation<>? AND missing_since>0 AND missing_since<=?
    )`, root.Path, generation, cutoff); err != nil {
		_ = tx.Rollback()
		return err
	}
	if _, err := tx.ExecContext(ctx, `DELETE FROM history_sources
        WHERE root=? AND seen_generation<>? AND missing_since>0 AND missing_since<=?`, root.Path, generation, cutoff); err != nil {
		_ = tx.Rollback()
		return err
	}
	if _, err := tx.ExecContext(ctx, `UPDATE history_roots SET state='ready',signature=?,indexed=?,completed_at=?,scan_cursor='' WHERE path=?`, signature, indexed, now, root.Path); err != nil {
		_ = tx.Rollback()
		return err
	}
	revision, err := bump(ctx, tx)
	if err != nil {
		_ = tx.Rollback()
		return err
	}
	if err := tx.Commit(); err != nil {
		return err
	}
	c.publish(revision, []string{root.Path}, "reconcile")
	return nil
}
