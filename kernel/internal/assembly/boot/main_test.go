package boot

import (
	"os"
	"testing"

	"tempora/internal/base/testenv"
)

func TestMain(m *testing.M) {
	if os.Getenv(fakeComputerHelperEnv) != "" {
		runFakeComputerHelper(os.Stdin, os.Stdout)
		return
	}
	testenv.RunWithIsolatedUserState(m)
}
