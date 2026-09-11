package boot

import (
	"tempora/internal/agent"
	"tempora/internal/tool"
)

func registerInteractiveAgentTools(reg *tool.Registry) {
	reg.Add(agent.NewAskTool())
}
