package cli

import "tempora/internal/event"

func (s *metricsSink) RuntimeStateChanged(snapshot event.RuntimeStateSnapshot) {
	if s != nil {
		event.PublishRuntimeState(s.inner, snapshot)
	}
}
