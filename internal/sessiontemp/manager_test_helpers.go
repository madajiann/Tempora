package sessiontemp

import filelock "tempora/internal/identitylock"

func tryLockForTest(path string) (func(), error) {
	return filelock.Acquire(nilContext(), path)
}
