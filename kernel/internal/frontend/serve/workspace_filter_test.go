package serve

import (
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"tempora/internal/base/testenv"
	"tempora/internal/contract/config"
)

// TestWorkspacesFiltersSystemAndInstallRoots proves the sidebar never shows a
// workspace that a stray launch path registered: a directory inside
// %SystemRoot% (run dialog / installer relaunch) and the kernel's own install
// tree (Explorer double-click) are dropped on read, the remembered file is
// rewritten without them, and rememberWorkspace refuses to put them back.
func TestWorkspacesFiltersSystemAndInstallRoots(t *testing.T) {
	t.Setenv("TEMPORA_HOME", testenv.TempDir(t))

	keep := testenv.TempDir(t)
	exe, err := os.Executable()
	if err != nil {
		t.Skip("no executable path")
	}
	// The test binary's directory stands in for an install tree: it "contains"
	// the running binary exactly like D:\Tempora contains tempora.exe.
	exeDir := filepath.Dir(exe)

	rememberWorkspace(keep)
	rememberWorkspace(exeDir) // must be refused

	got := Workspaces()
	if len(got) != 1 || got[0] != keep {
		t.Fatalf("Workspaces() = %v, want [%s]", got, keep)
	}

	// A persisted stray is pruned on read and the file is healed on disk.
	stray := filepath.Join(exeDir, "nested")
	if err := os.MkdirAll(stray, 0o755); err != nil {
		t.Fatal(err)
	}
	t.Cleanup(func() { os.RemoveAll(stray) })
	if err := os.WriteFile(workspacesPath(), []byte(`["`+strings.ReplaceAll(exeDir, `\`, `\\`)+`","`+strings.ReplaceAll(stray, `\`, `\\`)+`","`+strings.ReplaceAll(keep, `\`, `\\`)+`"]`), 0o644); err != nil {
		t.Fatal(err)
	}
	got = Workspaces()
	if len(got) != 1 || got[0] != keep {
		t.Fatalf("Workspaces() = %v, want [%s] after pruning", got, keep)
	}
	raw, err := os.ReadFile(workspacesPath())
	if err != nil {
		t.Fatal(err)
	}
	var persisted []string
	if err := json.Unmarshal(raw, &persisted); err != nil {
		t.Fatal(err)
	}
	for _, dir := range persisted {
		if strings.EqualFold(dir, exeDir) || strings.EqualFold(dir, stray) {
			t.Fatalf("persisted list still contains install-tree stray %s", dir)
		}
	}
	if config.MemoryUserDir() == "" {
		t.Fatal("state dir unresolved; the test proved nothing")
	}
}

// TestIllegitimateWorkspaceRootCoversSystemRoot checks the system-directory
// leg of the filter where %SystemRoot% exists (Windows CI and dev machines).
func TestIllegitimateWorkspaceRootCoversSystemRoot(t *testing.T) {
	sysRoot := os.Getenv("SystemRoot")
	if sysRoot == "" {
		t.Skip("no SystemRoot on this platform")
	}
	if !illegitimateWorkspaceRoot(filepath.Join(sysRoot, "System32")) {
		t.Fatal("System32 must be an illegitimate workspace root")
	}
	if illegitimateWorkspaceRoot(testenv.TempDir(t)) {
		t.Fatal("a temp project dir must stay legitimate")
	}
}
