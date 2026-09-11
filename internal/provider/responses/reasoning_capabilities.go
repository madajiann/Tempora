package responses

import "tempora/internal/provider"

func (c *client) ReasoningReplayCapabilities() provider.ReasoningReplayCapabilities {
	fallback := ""
	if c.AllowsEmptyReasoningFallback() {
		fallback = "omit-item"
	}
	return provider.ReasoningReplayCapabilities{Format: "responses-items", EmptyFallback: fallback}
}
