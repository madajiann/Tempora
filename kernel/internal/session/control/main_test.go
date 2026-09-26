package control

import (
	"os"
	"testing"

	"tempora/internal/base/testenv"

	"go.uber.org/goleak"
)

func TestMain(m *testing.M) {
	cleanupUserState, err := testenv.IsolateUserState()
	if err != nil {
		panic(err)
	}
	if os.Getenv("TEMPORA_CREDENTIALS_STORE") == "" {
		_ = os.Setenv("TEMPORA_CREDENTIALS_STORE", "file")
	}
	goleak.VerifyTestMain(m, goleak.Cleanup(func(exitCode int) {
		cleanupUserState()
		os.Exit(exitCode)
	}))
}
