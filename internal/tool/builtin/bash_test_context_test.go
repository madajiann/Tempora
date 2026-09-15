package builtin

import (
	"context"

	"tempora/internal/sandbox"
)

func fullAccessBashTestContext(ctx context.Context) context.Context {
	return sandbox.WithPermissionPreset(ctx, "danger-full-access")
}
