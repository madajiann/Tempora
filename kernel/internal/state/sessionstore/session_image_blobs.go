package sessionstore

import (
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"log/slog"
	"os"
	"path/filepath"
	"strings"

	"tempora/internal/base/fileutil"
	"tempora/internal/contract/provider"
	"tempora/internal/state/store"
)

// errBlobDigestMismatch means a blob file no longer hashes to the digest its
// reference promises: the sidecar was edited or truncated out of band.
var errBlobDigestMismatch = errors.New("session blob failed content-address verification")

// Session transcripts carry images inline as data URLs. A handful of
// screenshots is fine; a picture-heavy session writes every one of them into
// both the .jsonl anchor and — far worse — the append-only event log, which the
// replay reader refuses past sessionEventReplayMaxBytes. Once a log crosses
// that line the session can no longer be read back, so every later save fails
// and the conversation is stranded.
//
// These helpers lift image payloads out of the transcript into a
// content-addressed sidecar (<id>.blobs) and leave a short reference behind.
// The stored payload is the data URL verbatim, so a reference resolves back to
// the exact bytes that were inline and no media type or encoding has to be
// recorded separately.

const (
	// sessionImageRefPrefix marks an Images entry that is a blob reference
	// rather than a URL. No real URL or data URL can start with it.
	sessionImageRefPrefix = "tempora-blob:v1:"
	// sessionImageRefLen is len(sessionImageRefPrefix) plus the 64 hex digits
	// of a SHA-256 digest.
	sessionImageRefLen = len(sessionImageRefPrefix) + 64
	// sessionImageInlineLimit keeps small images inline. Externalizing a
	// one-kilobyte icon costs a file write and a read on every replay to save
	// nothing; the bytes that break the replay budget are orders of magnitude
	// larger.
	sessionImageInlineLimit = 8 << 10
)

// sessionImageBlobDir is the blob directory for a transcript.
func sessionImageBlobDir(sessionPath string) string {
	return store.SessionBlobDir(sessionPath)
}

// externalizeSessionImages returns msgs with inline image payloads replaced by
// blob references. The input is never mutated: callers keep the in-memory
// transcript with real data URLs and only the encoded bytes carry references.
//
// Failure is never fatal. A blob directory that cannot be written (read-only
// volume, disk full) leaves the image inline — the transcript stays correct and
// readable, it just keeps the old footprint for that one save.
func externalizeSessionImages(sessionPath string, msgs []provider.Message) []provider.Message {
	if len(msgs) == 0 {
		return msgs
	}
	dir := sessionImageBlobDir(sessionPath)
	if dir == "" {
		return msgs
	}
	// Long transcripts are saved constantly and almost never contain an image
	// big enough to externalize. Scan before copying so the common case costs
	// a walk over the Images slices and nothing more.
	if !hasSessionImage(msgs, sessionImageWorthExternalizing) {
		return msgs
	}
	changed := false
	out := make([]provider.Message, len(msgs))
	copy(out, msgs)
	for i := range out {
		if len(out[i].Images) == 0 {
			continue
		}
		images := make([]string, len(out[i].Images))
		copy(images, out[i].Images)
		for j, image := range images {
			if !sessionImageWorthExternalizing(image) {
				continue
			}
			ref, err := putSessionImageBlob(dir, image)
			if err != nil {
				slog.Warn("session: keeping image inline after blob store failure",
					"path", sessionPath, "err", err)
				continue
			}
			images[j] = ref
			changed = true
		}
		out[i].Images = images
	}
	if !changed {
		return msgs
	}
	return out
}

// inlineSessionImages is the inverse of externalizeSessionImages: every
// reference is resolved back to its data URL before the transcript is handed to
// a caller, so nothing outside this package ever sees a reference.
//
// A missing blob indicates the sidecar was lost (manual cleanup, partial
// restore) while the transcript survived. The entry is dropped rather than left
// as a reference a provider would reject; the rest of the turn still loads.
func inlineSessionImages(sessionPath string, msgs []provider.Message) []provider.Message {
	if len(msgs) == 0 {
		return msgs
	}
	dir := sessionImageBlobDir(sessionPath)
	if dir == "" {
		return msgs
	}
	if !hasSessionImage(msgs, isSessionImageRef) {
		return msgs
	}
	changed := false
	out := make([]provider.Message, len(msgs))
	copy(out, msgs)
	for i := range out {
		if len(out[i].Images) == 0 {
			continue
		}
		images := make([]string, 0, len(out[i].Images))
		msgChanged := false
		for _, image := range out[i].Images {
			ref, ok := sessionImageRefOf(image)
			if !ok {
				images = append(images, image)
				continue
			}
			data, err := getSessionImageBlob(dir, ref)
			if err != nil {
				slog.Warn("session: dropping image whose blob is missing",
					"path", sessionPath, "ref", ref, "err", err)
				msgChanged = true
				continue
			}
			images = append(images, string(data))
			msgChanged = true
		}
		if !msgChanged {
			continue
		}
		if len(images) == 0 {
			out[i].Images = nil
		} else {
			out[i].Images = images
		}
		changed = true
	}
	if !changed {
		return msgs
	}
	return out
}

// pruneSessionImageBlobs deletes blobs no longer referenced by msgs. Compaction
// is the only place that knows the full live set — the log it just wrote is the
// entire transcript — so rewinds and redactions do not leak their pictures
// forever. Best effort: a prune failure leaves stale files, never a broken
// transcript.
func pruneSessionImageBlobs(sessionPath string, msgs []provider.Message) {
	dir := sessionImageBlobDir(sessionPath)
	if dir == "" {
		return
	}
	live := make(map[string]struct{}, len(msgs))
	for _, m := range msgs {
		for _, image := range m.Images {
			if ref, ok := sessionImageRefOf(image); ok {
				live[ref] = struct{}{}
			}
		}
	}
	if err := pruneSessionBlobs(dir, live); err != nil {
		slog.Warn("session: blob prune failed", "path", sessionPath, "err", err)
	}
}

// hasSessionImage reports whether any Images entry in msgs satisfies match.
func hasSessionImage(msgs []provider.Message, match func(string) bool) bool {
	for _, m := range msgs {
		for _, image := range m.Images {
			if match(image) {
				return true
			}
		}
	}
	return false
}

func isSessionImageRef(image string) bool {
	_, ok := sessionImageRefOf(image)
	return ok
}

// sessionImageWorthExternalizing reports whether image is an inline data URL
// big enough to be worth lifting out of the transcript.
func sessionImageWorthExternalizing(image string) bool {
	if !strings.HasPrefix(image, "data:") {
		return false
	}
	if _, ok := sessionImageRefOf(image); ok {
		return false
	}
	return len(image) >= sessionImageInlineLimit
}

// sessionImageRefOf splits a blob reference into its digest.
func sessionImageRefOf(image string) (ref string, ok bool) {
	if len(image) != sessionImageRefLen || !strings.HasPrefix(image, sessionImageRefPrefix) {
		return "", false
	}
	ref = image[len(sessionImageRefPrefix):]
	for _, c := range ref {
		if (c < '0' || c > '9') && (c < 'a' || c > 'f') {
			return "", false
		}
	}
	return ref, true
}

func putSessionImageBlob(dir, payload string) (string, error) {
	sum := sha256.Sum256([]byte(payload))
	ref := hex.EncodeToString(sum[:])
	path := sessionBlobPath(dir, ref)
	if st, err := os.Stat(path); err == nil && st.Size() == int64(len(payload)) {
		return sessionImageRefPrefix + ref, nil
	}
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		return "", err
	}
	if err := fileutil.AtomicWriteFileStrict(path, []byte(payload), 0o600); err != nil {
		return "", err
	}
	return sessionImageRefPrefix + ref, nil
}

func getSessionImageBlob(dir, ref string) ([]byte, error) {
	data, err := os.ReadFile(sessionBlobPath(dir, ref))
	if err != nil {
		return nil, err
	}
	sum := sha256.Sum256(data)
	if hex.EncodeToString(sum[:]) != ref {
		return nil, errBlobDigestMismatch
	}
	return data, nil
}

// pruneSessionBlobs removes blobs outside live. Only leaf names that look like
// digests are considered, so fan-out directories and stray files are untouched.
func pruneSessionBlobs(dir string, live map[string]struct{}) error {
	return filepath.WalkDir(dir, func(path string, entry os.DirEntry, err error) error {
		if err != nil {
			if os.IsNotExist(err) {
				return nil
			}
			return err
		}
		if entry.IsDir() {
			return nil
		}
		ref := entry.Name()
		if _, ok := sessionImageRefOf(sessionImageRefPrefix + ref); !ok {
			return nil
		}
		if _, ok := live[ref]; ok {
			return nil
		}
		if err := os.Remove(path); err != nil && !os.IsNotExist(err) {
			return err
		}
		return nil
	})
}

// sessionBlobPath fans blobs out two levels so a session with thousands of
// images never leaves one unlistable directory.
func sessionBlobPath(dir, ref string) string {
	if len(ref) < 4 {
		return filepath.Join(dir, ref)
	}
	return filepath.Join(dir, ref[:2], ref[2:4], ref)
}
