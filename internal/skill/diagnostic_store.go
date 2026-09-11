package skill

import (
	"io"

	"tempora/internal/config"
)

// DiagnosticStore applies the same discovery policy in both doctor entrypoints.
// It only reads skill sources; it never starts a session or an MCP server.
func DiagnosticStore(root, home, temporaHome string, cfg *config.Config) *Store {
	return New(Options{
		ProjectRoot: root, HomeDir: home, TemporaHomeDir: temporaHome,
		CustomPaths: cfg.SkillCustomPaths(), ExcludedPaths: cfg.SkillExcludedPaths(),
		PluginPaths: cfg.PluginPackageSkillOwners(), PluginAgentPaths: cfg.PluginPackageAgentOwners(),
		DisabledNames: cfg.DisabledSkillNames(), MaxDepth: cfg.SkillMaxDepth(),
		Stderr: io.Discard,
	})
}
