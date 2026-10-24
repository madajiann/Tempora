// Ported from DeepSeek-Reasonix (MIT) — upstream PR #14086.
package historycatalog

import (
	"context"

	"tempora/internal/base/backgroundwork"
)

// scheduler is the queue every catalog write goes through, so an interactive
// read is never starved by a rebuild that is already running.
func (c *Catalog) scheduler() *backgroundwork.Scheduler {
	if c.opts.Work != nil {
		return c.opts.Work
	}
	return backgroundwork.Shared
}

// indexPath schedules one source. A source indexed outside a scan is
// incremental work and may run between rebuilds; a source indexed as part of a
// scan belongs to that scan's generation.
func (c *Catalog) indexPath(ctx context.Context, root Root, path string, generation int64, appendFrom int) error {
	priority := backgroundwork.Rebuild
	if generation == 0 {
		priority = backgroundwork.Incremental
	}
	return c.scheduler().Do(ctx, priority, func(job context.Context) error {
		return c.indexPathOnce(job, root, path, generation, appendFrom)
	})
}

// indexPending drains one queued source. It reports whether it took one, so
// the worker can keep draining the backlog before it starts a scan.
func (c *Catalog) indexPending(ctx context.Context, scanning Root, generation int64) bool {
	select {
	case path := <-c.queue:
		c.mu.Lock()
		queued, ok := c.paths[path]
		delete(c.paths, path)
		c.mu.Unlock()
		if !ok {
			return true
		}
		if queued.root.Path != scanning.Path {
			generation = 0
		}
		_ = c.scheduler().Do(ctx, backgroundwork.Incremental, func(job context.Context) error {
			return c.indexPathOnce(job, queued.root, path, generation, queued.appendFrom)
		})
		return true
	default:
		return false
	}
}

func (c *Catalog) ensureTokenizerVersion(ctx context.Context) error {
	return c.scheduler().Do(ctx, backgroundwork.Rebuild, c.ensureTokenizerVersionOnce)
}

// sourceReadError records a source that could not be read. A canceled read is
// not a corrupt source: the file was fine, the reader gave up.
func (c *Catalog) sourceReadError(ctx context.Context, root Root, path string, generation int64, contentFingerprint, metaFingerprint string, err error) error {
	if ctx.Err() != nil {
		return ctx.Err()
	}
	_, _ = c.db.ExecContext(ctx, `INSERT INTO history_sources(path,root,source,scope,workspace_root,content_fingerprint,meta_fingerprint,health,last_error,seen_generation)
            VALUES(?,?,?,?,?,?,?,'corrupt',?,?) ON CONFLICT(path) DO UPDATE SET health='corrupt',last_error=excluded.last_error,
            content_fingerprint=excluded.content_fingerprint,meta_fingerprint=excluded.meta_fingerprint,seen_generation=excluded.seen_generation`,
		path, root.Path, root.Source, root.Scope, root.WorkspaceRoot, contentFingerprint, metaFingerprint, err.Error(), generation)
	c.setError(err)
	return err
}
