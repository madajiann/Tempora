// Ported from DeepSeek-Reasonix (MIT) — upstream PR #14086.
package sessionstore

import (
	"path/filepath"
	"testing"

	"tempora/internal/state/sessionv4/v4fixture"
)

func TestV4ConversationsWithoutAListingCacheAreReplayedOnce(t *testing.T) {
	f := v4fixture.New(t)
	var dirs []string
	for i := range 3 {
		dir := f.Session(dirID(i), 3)
		f.Batch(dir, v4fixture.Ended, v4fixture.Event{Kind: "message/complete", Payload: v4fixture.Msg("a", "user", "hello")})
		dirs = append(dirs, dir)
	}
	sessions := filepath.Join(filepath.Dir(f.Root), "sessions")
	rows, err := ListSessions(sessions)
	if err != nil {
		t.Fatal(err)
	}
	if len(rows) != len(dirs) {
		t.Fatalf("rows=%d want %d", len(rows), len(dirs))
	}
	previews := map[string]string{}
	for _, row := range rows {
		if row.Preview != "hello" {
			t.Fatalf("%s previews %q", row.Path, row.Preview)
		}
		previews[row.Path] = row.Preview
	}
	if entries := len(loadV4Listings(sessions).Entries); entries != len(dirs) {
		t.Fatalf("persisted entries = %d, want %d", entries, len(dirs))
	}
}

func dirID(i int) string {
	const hexdigits = "0123456789abcdef"
	out := make([]byte, 32)
	for j := range out {
		out[j] = hexdigits[(i+j)%16]
	}
	return string(out)
}
