// Ported from DeepSeek-Reasonix (MIT) — upstream PR #14086.
package sessionstore

import (
	"os"
	"path/filepath"
	"testing"

	"tempora/internal/state/sessionv4/v4fixture"
)

func TestLegacyOnlyDirectoryPersistsListing(t *testing.T) {
	f := v4fixture.New(t)
	dir := f.Session("0123456789abcdef0123456789abcdef", 3)
	f.Batch(dir, v4fixture.Ended, v4fixture.Event{Kind: "message/complete", Payload: v4fixture.Msg("a", "user", "hello")})
	sessions := filepath.Join(filepath.Dir(f.Root), "sessions")
	rows, err := ListSessions(sessions)
	if err != nil || len(rows) != 1 {
		t.Fatalf("rows=%v err=%v", rows, err)
	}
	if _, err := os.Stat(filepath.Join(sessions, v4ListingName)); err != nil {
		t.Fatalf("cache not persisted: %v", err)
	}
}
