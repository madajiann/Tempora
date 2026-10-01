package boot

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// TestResolveWorkspaceRootExplicitAndGitFallback proves the --dir contract:
// an explicit workspace root is honored even inside a git repository, while an
// empty root still falls back to the nearest git root from the working directory.
func TestResolveWorkspaceRootExplicitAndGitFallback(t *testing.T) {
	repo := robustTempDir(t)
	if err := os.Mkdir(filepath.Join(repo, ".git"), 0o755); err != nil {
		t.Fatal(err)
	}
	sub := filepath.Join(repo, "a", "b")
	if err := os.MkdirAll(sub, 0o755); err != nil {
		t.Fatal(err)
	}

	// Explicit --dir pins the workspace root, not the git root of the repo.
	if got := resolveWorkspaceRoot(sub); got != sub {
		t.Fatalf("resolveWorkspaceRoot(%q) = %q, want the explicit dir", sub, got)
	}

	// No explicit root: fall back to the nearest git root from the CWD.
	t.Chdir(sub)
	got := resolveWorkspaceRoot("")
	wantRoot, err := filepath.EvalSymlinks(repo)
	if err != nil {
		t.Fatal(err)
	}
	gotResolved, err := filepath.EvalSymlinks(got)
	if err != nil {
		t.Fatalf("resolveWorkspaceRoot(%q) returned unusable path %q: %v", "", got, err)
	}
	if gotResolved != wantRoot {
		t.Fatalf("resolveWorkspaceRoot(\"\") = %q, want git root %q", got, repo)
	}
}

func TestResolveWorkspaceRootFallsBackFromSystemDir(t *testing.T) {
	sysRoot := os.Getenv("SystemRoot")
	if sysRoot == "" {
		t.Skip("no SystemRoot on this platform")
	}
	dir := filepath.Join(sysRoot, "System32")
	if !inSystemRoot(dir) {
		t.Fatalf("inSystemRoot(%q) = false, want true", dir)
	}
	if inSystemRoot(t.TempDir()) {
		t.Fatalf("inSystemRoot(tempdir) = true, want false")
	}
	// 模拟内核被落在 System32 的场景：显式空 → 应回退到主目录而不是系统目录
	old, err := os.Getwd()
	if err != nil {
		t.Fatal(err)
	}
	defer os.Chdir(old)
	if err := os.Chdir(dir); err != nil {
		t.Skipf("cannot chdir into %s: %v", dir, err)
	}
	got := resolveWorkspaceRoot("")
	if strings.EqualFold(got, dir) {
		t.Fatalf("resolveWorkspaceRoot() = %q, want home fallback", got)
	}
	home, _ := os.UserHomeDir()
	if home != "" && !strings.EqualFold(got, home) {
		t.Fatalf("resolveWorkspaceRoot() = %q, want %q", got, home)
	}
}

// TestResolveWorkspaceRootFallsBackFromOwnInstallDir covers the Explorer
// double-click launch: the process cwd lands on the binary's own folder (the
// install tree), which must fall back to the home directory instead of
// registering the install dir as the default workspace.
func TestResolveWorkspaceRootFallsBackFromOwnInstallDir(t *testing.T) {
	exe, err := os.Executable()
	if err != nil {
		t.Skip("no executable path")
	}
	exeDir := filepath.Dir(exe)
	if !inOwnInstallTree(exeDir) {
		t.Fatalf("inOwnInstallTree(%q) = false, want true", exeDir)
	}
	if inOwnInstallTree(t.TempDir()) {
		t.Fatal("inOwnInstallTree(tempdir) = true, want false")
	}
	if inOwnInstallTree(filepath.Join(filepath.Dir(exeDir), "elsewhere")) {
		t.Fatal("a sibling of the exe dir is not part of the install tree")
	}
	// 内核被双击启动：cwd = 安装目录 → 应回退主目录
	old, err := os.Getwd()
	if err != nil {
		t.Fatal(err)
	}
	defer os.Chdir(old)
	if err := os.Chdir(exeDir); err != nil {
		t.Skipf("cannot chdir into %s: %v", exeDir, err)
	}
	got := resolveWorkspaceRoot("")
	if strings.EqualFold(got, exeDir) {
		t.Fatalf("resolveWorkspaceRoot() = %q, want home fallback", got)
	}
}
