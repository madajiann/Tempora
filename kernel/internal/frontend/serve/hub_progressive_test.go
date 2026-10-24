// Ported from DeepSeek-Reasonix (MIT) — upstream PR #14086.
package serve

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"path/filepath"
	"testing"
	"time"

	"tempora/internal/state/sessionv4/v4fixture"
)

// The sidebar asks for the tree before every old conversation has been read.
// The rows it has found come back at once, with the state of the listing beside
// them, and the summaries still being read arrive in a later read.
func TestProgressiveTreePublishesLegacyRowsAndFinalCounts(t *testing.T) {
	t.Setenv("TEMPORA_HOME", t.TempDir())
	root := t.TempDir()
	rememberWorkspace(root)
	f := v4fixture.New(t)
	f.Root = filepath.Join(filepath.Dir(SessionDirFor(root)), "sessions-v4")
	for i := range 3 {
		dir := f.Session(fmt.Sprintf("%032x", i+1), 3)
		f.Batch(dir, v4fixture.Ended, v4fixture.Event{Kind: "message/complete", Payload: v4fixture.Msg("a", "user", "find me")})
	}
	h := NewHub(HubOptions{})
	t.Cleanup(h.Shutdown)
	changed := make(chan struct{}, 1)
	stop := h.legacyListings().Subscribe(func() {
		select {
		case changed <- struct{}{}:
		default:
		}
	})
	defer stop()
	deadline := time.NewTimer(15 * time.Second)
	defer deadline.Stop()
	for {
		w := httptest.NewRecorder()
		h.tree(w, httptest.NewRequest(http.MethodGet, "/tree?progressive=1", nil))
		var workspaces []treeWorkspace
		if err := json.Unmarshal(w.Body.Bytes(), &workspaces); err != nil {
			t.Fatal(err)
		}
		if len(workspaces) != 1 {
			t.Fatalf("workspaces=%+v", workspaces)
		}
		ws := workspaces[0]
		if ws.CountsComplete == nil {
			t.Fatal("missing coverage")
		}
		if *ws.CountsComplete {
			if len(ws.Sessions) != 3 {
				t.Fatalf("workspace=%+v", ws)
			}
			for _, row := range ws.Sessions {
				if row.CountsKnown == nil || !*row.CountsKnown {
					t.Fatalf("unknown final count: %+v", row)
				}
				if row.MetadataState != "ready" {
					t.Fatalf("metadata state=%q", row.MetadataState)
				}
				if row.Title != "find me" {
					t.Fatalf("title=%q", row.Title)
				}
			}
			break
		}
		select {
		case <-changed:
		case <-deadline.C:
			t.Fatalf("did not settle: %+v", ws)
		}
	}
	// The plain tree keeps the old contract: no coverage fields at all.
	w := httptest.NewRecorder()
	h.tree(w, httptest.NewRequest(http.MethodGet, "/tree", nil))
	var old []treeWorkspace
	if err := json.Unmarshal(w.Body.Bytes(), &old); err != nil {
		t.Fatal(err)
	}
	if old[0].CountsComplete != nil {
		t.Fatalf("legacy contract=%+v", old[0])
	}
	if len(old[0].Sessions) != 3 {
		t.Fatalf("legacy contract missed the rows: %+v", old[0])
	}
}
