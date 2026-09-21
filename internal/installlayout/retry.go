package installlayout

import (
	"os"
	"time"
)

const transientRetryAttempts = 15

// transientRetryDelay is a test seam; production backs off linearly to
// about forty seconds. The old ~11s budget lost two real activation races
// to Defender holding a freshly extracted 155MB staging directory
// (update-helper.log 2026-09-19 11:08/11:32: rename .staging -> versions:
// Access is denied, succeeded only on a manual third attempt). AV holds on
// large fresh payloads routinely exceed 11s; 42s rides them out.
var transientRetryDelay = time.Sleep

// retryTransient repeats op while it fails with a Windows sharing, lock, or
// access-denied error. Antivirus and indexers hold freshly written files for
// moments, and MoveFileEx/DeleteFile report that instead of waiting.
func retryTransient(op func() error) error {
	var err error
	for attempt := 1; attempt <= transientRetryAttempts; attempt++ {
		err = op()
		if err == nil || !transientFileError(err) || attempt == transientRetryAttempts {
			return err
		}
		transientRetryDelay(time.Duration(attempt) * 400 * time.Millisecond)
	}
	return err
}

func renameRetry(oldPath, newPath string) error {
	return retryTransient(func() error { return os.Rename(oldPath, newPath) })
}

func removeRetry(path string) error {
	return retryTransient(func() error { return os.Remove(path) })
}

func removeAllRetry(path string) error {
	return retryTransient(func() error { return os.RemoveAll(path) })
}
