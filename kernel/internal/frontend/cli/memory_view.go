package cli

import (
	"time"

	"tempora/internal/session/control"
	"tempora/internal/state/memory"
)

func renderMemory(width int, set *memory.Set) string {
	return viewProtectLines(control.RenderMemorySummary(set, time.Now().UTC()), width)
}
