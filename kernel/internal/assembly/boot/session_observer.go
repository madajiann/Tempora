package boot

import (
	"tempora/internal/state/history"
	"tempora/internal/state/sessionstore"
)

func newObservedSession(systemPrompt string) *sessionstore.Session {
	session := sessionstore.NewSession(systemPrompt)
	session.SetPersistObserver(history.PersistObserver())
	return session
}
