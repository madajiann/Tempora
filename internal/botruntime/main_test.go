package botruntime

import (
	"testing"

	"tempora/internal/testenv"
)

func TestMain(m *testing.M) {
	testenv.RunWithIsolatedUserState(m)
}
