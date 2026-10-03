package sessionstore

import (
	"encoding/base64"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"tempora/internal/base/testenv"
	"tempora/internal/contract/provider"
	"tempora/internal/state/store"
)

// bigImage builds a data URL comfortably over the inline threshold.
func bigImage(fill byte, size int) string {
	payload := make([]byte, size)
	for i := range payload {
		payload[i] = fill
	}
	return "data:image/png;base64," + base64.StdEncoding.EncodeToString(payload)
}

func TestExternalizeAndInlineRoundTripsImages(t *testing.T) {
	dir := testenv.TempDir(t)
	path := filepath.Join(dir, "session.jsonl")
	image := bigImage(0x41, 64<<10)
	small := "data:image/png;base64," + base64.StdEncoding.EncodeToString([]byte("tiny"))

	msgs := []provider.Message{
		{Role: provider.RoleUser, Content: "look", Images: []string{image, small}},
		{Role: provider.RoleAssistant, Content: "ok"},
	}

	stored := externalizeSessionImages(path, msgs)
	if strings.Contains(stored[0].Images[0], "base64,") {
		t.Fatalf("large image stayed inline")
	}
	if stored[0].Images[1] != small {
		t.Fatalf("small image was externalized: %q", small)
	}
	if msgs[0].Images[0] != image {
		t.Fatalf("externalize mutated the caller's transcript")
	}

	// The blob must exist on disk under the content digest.
	ref, ok := sessionImageRefOf(stored[0].Images[0])
	if !ok {
		t.Fatalf("stored entry %q is not a blob reference", stored[0].Images[0])
	}
	if _, err := os.Stat(sessionBlobPath(sessionImageBlobDir(path), ref)); err != nil {
		t.Fatalf("blob missing for %s: %v", ref, err)
	}

	back := inlineSessionImages(path, stored)
	if len(back[0].Images) != 2 || back[0].Images[0] != image || back[0].Images[1] != small {
		t.Fatalf("inline did not restore the original images")
	}
}

func TestInlineDropsImageWhoseBlobIsMissing(t *testing.T) {
	dir := testenv.TempDir(t)
	path := filepath.Join(dir, "session.jsonl")
	image := bigImage(0x42, 32<<10)
	stored := externalizeSessionImages(path, []provider.Message{
		{Role: provider.RoleUser, Content: "look", Images: []string{image}},
	})
	blobs := sessionImageBlobDir(path)
	if err := os.RemoveAll(blobs); err != nil {
		t.Fatalf("remove blobs: %v", err)
	}
	back := inlineSessionImages(path, stored)
	if len(back[0].Images) != 0 {
		t.Fatalf("missing blob survived as %q", back[0].Images)
	}
	if back[0].Content != "look" {
		t.Fatalf("turn text lost alongside the image: %q", back[0].Content)
	}
}

func TestPruneKeepsOnlyReferencedBlobs(t *testing.T) {
	dir := testenv.TempDir(t)
	path := filepath.Join(dir, "session.jsonl")
	keep := bigImage(0x43, 32<<10)
	drop := bigImage(0x44, 32<<10)

	stored := externalizeSessionImages(path, []provider.Message{
		{Role: provider.RoleUser, Content: "a", Images: []string{keep, drop}},
	})
	blobs := sessionImageBlobDir(path)
	count := func() int {
		n := 0
		filepath.WalkDir(blobs, func(_ string, e os.DirEntry, err error) error {
			if err == nil && !e.IsDir() {
				n++
			}
			return nil
		})
		return n
	}
	if got := count(); got != 2 {
		t.Fatalf("blobs on disk = %d, want 2", got)
	}
	pruneSessionImageBlobs(path, []provider.Message{
		{Role: provider.RoleUser, Content: "a", Images: []string{stored[0].Images[0]}},
	})
	if got := count(); got != 1 {
		t.Fatalf("blobs after prune = %d, want 1", got)
	}
	if _, err := os.ReadFile(sessionBlobPath(blobs, mustRef(t, stored[0].Images[0]))); err != nil {
		t.Fatalf("referenced blob was pruned: %v", err)
	}
}

func mustRef(t *testing.T, image string) string {
	t.Helper()
	ref, ok := sessionImageRefOf(image)
	if !ok {
		t.Fatalf("%q is not a blob reference", image)
	}
	return ref
}

// TestSaveKeepsImagesOutOfTheEventLog pins the regression this file exists for:
// an image-heavy session must not push the event log toward the replay byte
// budget, and a saved image must come back byte-identical.
func TestSaveKeepsImagesOutOfTheEventLog(t *testing.T) {
	path := filepath.Join(testenv.TempDir(t), "session.jsonl")
	image := bigImage(0x45, 96<<10)

	s := NewSession("system")
	s.Add(provider.Message{Role: provider.RoleUser, Content: "describe this", Images: []string{image}})
	s.Add(provider.Message{Role: provider.RoleAssistant, Content: "a large PNG"})
	if err := s.SaveSnapshot(path); err != nil {
		t.Fatalf("SaveSnapshot: %v", err)
	}

	logBytes, err := os.ReadFile(store.SessionEventLog(path))
	if err != nil {
		t.Fatalf("read event log: %v", err)
	}
	if strings.Contains(string(logBytes), "base64,") {
		t.Fatalf("event log still carries an inline image payload (%d bytes)", len(logBytes))
	}
	if !strings.Contains(string(logBytes), sessionImageRefPrefix) {
		t.Fatalf("event log carries no blob reference")
	}
	if int64(len(logBytes)) > sessionEventReplayMaxBytes/4 {
		t.Fatalf("event log = %d bytes with one image; expected a small record", len(logBytes))
	}

	loaded, err := LoadSession(path)
	if err != nil {
		t.Fatalf("LoadSession: %v", err)
	}
	got := loaded.Snapshot()
	if len(got[1].Images) != 1 || got[1].Images[0] != image {
		t.Fatalf("reloaded images = %v, want the original data URL", got[1].Images)
	}

	// Re-saving an identical transcript must recognize it as up to date: the
	// digest is taken over the inlined transcript and must not drift when
	// images round-trip through the blob store.
	if err := loaded.SaveSnapshot(path); err != nil {
		t.Fatalf("second SaveSnapshot: %v", err)
	}
	again, err := LoadSession(path)
	if err != nil {
		t.Fatalf("LoadSession after resave: %v", err)
	}
	if len(again.Snapshot()) != len(got) {
		t.Fatalf("resave changed the transcript length: %d vs %d", len(again.Snapshot()), len(got))
	}
}

// TestSessionBlobDirIsRemovedWithTheSession guards the sweep: blobs outlive
// their transcript only if nobody lists the directory as a sidecar.
func TestSessionBlobDirIsRemovedWithTheSession(t *testing.T) {
	path := filepath.Join(testenv.TempDir(t), "session.jsonl")
	s := NewSession("system")
	s.Add(provider.Message{Role: provider.RoleUser, Content: "look", Images: []string{bigImage(0x46, 32<<10)}})
	if err := s.SaveSnapshot(path); err != nil {
		t.Fatalf("SaveSnapshot: %v", err)
	}
	if _, err := os.Stat(sessionImageBlobDir(path)); err != nil {
		t.Fatalf("blob dir missing after save: %v", err)
	}
	if err := store.RemoveSessionArtifacts(path); err != nil {
		t.Fatalf("RemoveSessionArtifacts: %v", err)
	}
	if _, err := os.Stat(sessionImageBlobDir(path)); !os.IsNotExist(err) {
		t.Fatalf("blob dir survived session deletion (err=%v)", err)
	}
}
