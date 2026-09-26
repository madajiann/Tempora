package serve

import (
	"testing"

	"tempora/internal/base/testenv"
)

func TestMain(m *testing.M) {
	testenv.RunWithIsolatedUserState(m)
}
