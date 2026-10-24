// Ported from DeepSeek-Reasonix (MIT) — upstream PR #14086.
package serve

import (
	"log/slog"
	"path/filepath"

	"tempora/internal/state/sessionstore"
)

// hubLegacyListings is the hub's handle on the background listing service:
// one shared service per process, subscribed once, released when the hub goes.
type hubLegacyListings struct {
	service     *sessionstore.LegacyListings
	release     func()
	unsubscribe func()
}

func (h *Hub) legacyListings() *sessionstore.LegacyListings {
	h.mu.Lock()
	defer h.mu.Unlock()
	if h.legacy == nil {
		service, release := sessionstore.AcquireLegacyListings()
		h.legacy = &hubLegacyListings{service: service, release: release, unsubscribe: service.Subscribe(h.treeChanged)}
	}
	return h.legacy.service
}

func (h *Hub) closeLegacyListings() {
	h.mu.Lock()
	legacy := h.legacy
	h.legacy = nil
	h.mu.Unlock()
	if legacy != nil {
		legacy.unsubscribe()
		legacy.release()
	}
}

// combineListingStatus folds one folder's coverage into the folder's own, so a
// window that reads several folders sees the worst state among them.
func combineListingStatus(a *sessionstore.ListingStatus, b sessionstore.ListingStatus) {
	a.ListingRevision += b.ListingRevision
	a.CountsComplete = a.CountsComplete && b.CountsComplete
	a.PendingMetadata += b.PendingMetadata
	a.FailedMetadata += b.FailedMetadata
	priority := map[string]int{"ready": 0, "indexing": 1, "discovering": 2, "degraded": 3}
	if priority[b.ListingState] > priority[a.ListingState] {
		a.ListingState = b.ListingState
	}
}

// listTreeSessions answers one folder's rows. Without a status the listing is
// the complete one; with one the rows come from the native list plus whatever
// the background service has found so far.
func (h *Hub) listTreeSessions(dir string, status *sessionstore.ListingStatus, retry bool) []sessionstore.SessionInfo {
	if status == nil {
		infos, _ := sessionstore.ListSessions(dir)
		return infos
	}
	infos, err := sessionstore.ListNativeSessions(dir)
	if retry {
		h.legacyListings().Retry(dir)
	}
	legacy, progress := h.legacyListings().Snapshot(dir)
	if err != nil {
		progress.ListingState, progress.CountsComplete = "degraded", false
	}
	combineListingStatus(status, progress)
	present := make(map[string]bool, len(infos))
	for _, native := range infos {
		present[native.Path] = true
	}
	for _, row := range legacy {
		if !present[row.Path] {
			infos = append(infos, row)
		}
	}
	return infos
}

// prioritizeTreeRows names the rows the reader is looking at, so their
// summaries are read before the rest of the backlog.
func (h *Hub) prioritizeTreeRows(dir string, rows []treeSession) {
	paths := []string{}
	for _, row := range rows {
		if filepath.Dir(row.Path) == dir {
			paths = append(paths, row.Path)
		}
	}
	h.legacyListings().Prioritize(dir, paths)
}

func listingStatusFor(progressive bool) *sessionstore.ListingStatus {
	if !progressive {
		return nil
	}
	return &sessionstore.ListingStatus{ListingState: "ready", CountsComplete: true}
}

// treeChanged is the background listing saying it learned something. The
// sidebar reads the tree when it is asked to, so this only records that the
// answer is due to change.
func (h *Hub) treeChanged() {
	slog.Debug("serve: legacy listing changed")
}
