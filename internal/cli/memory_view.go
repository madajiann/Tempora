package cli

import (
	"time"

	"tempora/internal/control"
	"tempora/internal/memory"
)

func renderMemory(width int, set *memory.Set) string {
	return viewProtectLines(control.RenderMemorySummary(set, time.Now().UTC()), width)
}
