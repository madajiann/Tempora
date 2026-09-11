package sessiontemp

import "tempora/internal/filelock"

func tryLockForTest(path string) (func(), error) {
	return filelock.Acquire(nilContext(), path)
}
