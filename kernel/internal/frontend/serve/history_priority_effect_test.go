// Ported from DeepSeek-Reasonix (MIT) — upstream PR #14086.
package serve

import (
	"context"
	"errors"
	"net/http"
	"net/http/httptest"
	"path/filepath"
	"testing"

	"tempora/internal/base/backgroundwork"
	"tempora/internal/base/testenv"
	"tempora/internal/contract/config"
	"tempora/internal/contract/event"
	"tempora/internal/contract/provider"
	"tempora/internal/contract/tool"
	"tempora/internal/runtime/agent"
	"tempora/internal/state/sessionstore"
	"tempora/internal/session/control"
)

// idleProvider is a model that never says anything: this test is about which
// work is given way to, not about what the model answers.
type idleProvider struct{}

func (*idleProvider) Name() string { return "idle" }

func (*idleProvider) Stream(context.Context, provider.Request) (<-chan provider.Chunk, error) {
	ch := make(chan provider.Chunk, 1)
	ch <- provider.Chunk{Type: provider.ChunkDone}
	close(ch)
	return ch, nil
}

// A projection running in the background gives way to what a person is waiting
// for. Reading the tree does not: a refresh of the sidebar must not cancel the
// work that is filling it in.
func TestResumePreemptsProjectionButTreeRefreshDoesNot(t *testing.T) {
	dir := testenv.TempDir(t)
	path := filepath.Join(dir, "history.jsonl")
	session := sessionstore.NewSession("system")
	session.Add(provider.Message{Role: provider.RoleUser, Content: "saved history"})
	if err := session.Save(path); err != nil {
		t.Fatal(err)
	}
	bc := NewBroadcaster()
	executor := agent.New(&idleProvider{}, tool.NewRegistry(), sessionstore.NewSession(""), agent.Options{MaxSteps: 1}, event.Discard)
	ctrl := control.New(control.Options{Sink: bc, SessionDir: dir, Executor: executor})
	srv := New(ctrl, bc, config.ServeConfig{})
	h := NewHub(HubOptions{})
	rt, err := h.Adopt(srv, bc)
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(h.Shutdown)

	job, release, err := backgroundwork.Shared.Acquire(context.Background(), backgroundwork.Rebuild)
	if err != nil {
		t.Fatal(err)
	}
	defer release()
	h.tree(httptest.NewRecorder(), httptest.NewRequest(http.MethodGet, "/tree?progressive=1", nil))
	if job.Err() != nil {
		t.Fatal("tree refresh preempted its producer")
	}
	if _, err := rt.Server.resumeInto(path); err != nil {
		t.Fatal(err)
	}
	if !errors.Is(context.Cause(job), backgroundwork.ErrPreempted) {
		t.Fatalf("cause=%v", context.Cause(job))
	}
	if got := rt.Server.Controller().History(); len(got) < 2 || got[len(got)-1].Content != "saved history" {
		t.Fatalf("history=%v", got)
	}
	release()

	mux := http.NewServeMux()
	rt.Server.registerHistoryRoutes(mux)
	w := httptest.NewRecorder()
	mux.ServeHTTP(w, httptest.NewRequest(http.MethodGet, "/history", nil))
	if w.Code != http.StatusOK {
		t.Fatalf("status=%d", w.Code)
	}
}
