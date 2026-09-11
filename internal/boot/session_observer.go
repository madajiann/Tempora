package boot

import (
	"tempora/internal/agent"
	"tempora/internal/history"
)

func newObservedSession(systemPrompt string) *agent.Session {
	session := agent.NewSession(systemPrompt)
	session.SetPersistObserver(history.PersistObserver())
	return session
}
