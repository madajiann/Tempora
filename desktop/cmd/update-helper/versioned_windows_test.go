//go:build windows

package main

import (
	"os"
	"path/filepath"
	"testing"

	"tempora/internal/installlayout"
	"tempora/internal/repair"
)

func writeVersionedWindowsStaging(t *testing.T, dir, prefix, version string, names ...string) {
	t.Helper()
	if len(names) == 0 {
		names = []string{"tempora-desktop.exe", "tempora-cli.exe", "tempora-update-helper.exe", "tempora-launcher.exe"}
	}
	for _, name := range names {
		path := filepath.Join(dir, filepath.FromSlash(name))
		if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(path, []byte(prefix+name), 0o700); err != nil {
			t.Fatal(err)
		}
	}
	writeWindowsPayloadManifestForTest(t, dir, version)
}

func versionedWindowsTransaction(installDir, version, createdAt string) *repair.UpdateTransaction {
	return &repair.UpdateTransaction{
		SchemaVersion: 1,
		ToVersion:     version,
		TargetKind:    "file",
		TargetPath:    filepath.Join(installDir, "tempora-desktop.exe"),
		CreatedAt:     createdAt,
	}
}

func TestPreferVersionedWindowsActivation(t *testing.T) {
	staging := t.TempDir()
	if preferVersionedWindowsActivation(staging) {
		t.Fatal("empty staging must not prefer versioned")
	}
	for _, name := range []string{
		"tempora-desktop.exe",
		"tempora-cli.exe",
		"tempora-update-helper.exe",
		"tempora-launcher.exe",
	} {
		if err := os.WriteFile(filepath.Join(staging, name), []byte(name), 0o700); err != nil {
			t.Fatal(err)
		}
	}
	if !preferVersionedWindowsActivation(staging) {
		t.Fatal("complete staging must prefer versioned")
	}
}

func TestActivateVersionedWindowsFromStaging(t *testing.T) {
	acceptWindowsPayloadManifestForTest(t)
	installDir := t.TempDir()
	staging := t.TempDir()
	writeVersionedWindowsStaging(t, staging, "payload:", "v1.20.0",
		"tempora-desktop.exe",
		"tempora-cli.exe",
		"tempora-update-helper.exe",
		"tempora-launcher.exe",
		"tempora-guard.exe",
	)
	// Seed a flat desktop so cleanup is observable.
	if err := os.WriteFile(filepath.Join(installDir, "tempora-desktop.exe"), []byte("old"), 0o700); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(installDir, "tempora-guard.exe"), []byte("old-guard"), 0o700); err != nil {
		t.Fatal(err)
	}

	claimed := versionedWindowsTransaction(installDir, "v1.20.0", "2026-01-01T00:00:00Z")
	if err := activateVersionedWindowsFromStaging(claimed, staging); err != nil {
		t.Fatal(err)
	}
	if !installlayout.HasCurrent(installDir) {
		t.Fatal("current.json missing")
	}
	ptr, err := installlayout.ReadCurrent(installDir)
	if err != nil || ptr.ActiveVersion != "v1.20.0" {
		t.Fatalf("pointer=%+v err=%v", ptr, err)
	}
	desktop, err := installlayout.ActiveDesktopPath(installDir)
	if err != nil {
		t.Fatal(err)
	}
	raw, err := os.ReadFile(desktop)
	if err != nil || string(raw) != "payload:tempora-desktop.exe" {
		t.Fatalf("desktop payload = %q err=%v", raw, err)
	}
	for _, name := range []string{"tempora-launcher.exe", "Tempora.exe", "tempora-cli.exe"} {
		if _, err := os.Stat(filepath.Join(installDir, name)); err != nil {
			t.Fatalf("root entry %s: %v", name, err)
		}
	}
	if _, err := os.Stat(filepath.Join(installDir, "tempora-desktop.exe")); !os.IsNotExist(err) {
		t.Fatal("flat desktop should be removed")
	}
	if _, err := os.Stat(filepath.Join(installDir, "tempora-guard.exe")); !os.IsNotExist(err) {
		t.Fatal("flat guard should be removed")
	}
	if prefer := preferRelaunchPath("", installDir); filepath.Base(prefer) != "tempora-launcher.exe" {
		t.Fatalf("prefer relaunch = %s", prefer)
	}
}

func TestActivateVersionedWindowsFromStagingPublishesShellTree(t *testing.T) {
	acceptWindowsPayloadManifestForTest(t)
	installDir := t.TempDir()
	staging := t.TempDir()
	tree := []string{"app/Tempora.exe", "app/resources/app.asar", "app/locales/en-US.pak"}
	writeVersionedWindowsStaging(t, staging, "payload:", "v1.30.0", append([]string{
		"tempora-desktop.exe",
		"tempora-cli.exe",
		"tempora-update-helper.exe",
		"tempora-launcher.exe",
	}, tree...)...)
	if err := activateVersionedWindowsFromStaging(versionedWindowsTransaction(installDir, "v1.30.0", "2026-01-01T00:00:00Z"), staging); err != nil {
		t.Fatal(err)
	}
	versionDir := filepath.Join(installDir, installlayout.VersionsDirName, "v1.30.0")
	for _, name := range tree {
		raw, err := os.ReadFile(filepath.Join(versionDir, filepath.FromSlash(name)))
		if err != nil || string(raw) != "payload:"+name {
			t.Fatalf("tree member %s = %q err=%v", name, raw, err)
		}
	}
	if _, err := os.Stat(filepath.Join(installDir, "app")); !os.IsNotExist(err) {
		t.Fatalf("shell tree leaked into the install root: %v", err)
	}
}

func TestActivateVersionedWindowsFromStagingRejectsManifestDrift(t *testing.T) {
	acceptWindowsPayloadManifestForTest(t)
	installDir := t.TempDir()
	staging := t.TempDir()
	writeVersionedWindowsStaging(t, staging, "payload:", "v1.30.0",
		"tempora-desktop.exe",
		"tempora-cli.exe",
		"tempora-update-helper.exe",
		"tempora-launcher.exe",
		"app/Tempora.exe",
	)
	if err := os.WriteFile(filepath.Join(staging, "app", "Tempora.exe"), []byte("tampered"), 0o700); err != nil {
		t.Fatal(err)
	}
	if err := activateVersionedWindowsFromStaging(versionedWindowsTransaction(installDir, "v1.30.0", "2026-01-01T00:00:00Z"), staging); err == nil {
		t.Fatal("staged tree member that differs from the signed manifest was activated")
	}
	if installlayout.HasCurrent(installDir) {
		t.Fatal("current.json was written after a rejected payload")
	}
	if err := os.Remove(filepath.Join(staging, "tempora-payload.json")); err != nil {
		t.Fatal(err)
	}
	if err := activateVersionedWindowsFromStaging(versionedWindowsTransaction(installDir, "v1.30.0", "2026-01-01T00:00:00Z"), staging); err == nil {
		t.Fatal("staged payload without a signed manifest was activated")
	}
}

func TestPreferRelaunchPathIgnoresStaleVersionedDesktop(t *testing.T) {
	acceptWindowsPayloadManifestForTest(t)
	installDir := t.TempDir()
	oldSrc := t.TempDir()
	newSrc := t.TempDir()
	writeVersionedWindowsStaging(t, oldSrc, "old-", "v1.24.0")
	if err := activateVersionedWindowsFromStaging(versionedWindowsTransaction(installDir, "v1.24.0", "2026-01-01T00:00:00Z"), oldSrc); err != nil {
		t.Fatal(err)
	}
	oldDesktop, err := installlayout.ActiveDesktopPath(installDir)
	if err != nil {
		t.Fatal(err)
	}
	writeVersionedWindowsStaging(t, newSrc, "new-", "v1.24.1")
	if err := activateVersionedWindowsFromStaging(versionedWindowsTransaction(installDir, "v1.24.1", "2026-01-01T00:00:01Z"), newSrc); err != nil {
		t.Fatal(err)
	}
	if _, err := os.Stat(oldDesktop); err != nil {
		t.Fatalf("previous desktop should remain: %v", err)
	}
	got := preferRelaunchPath(oldDesktop, installDir)
	if filepath.Base(got) != "tempora-launcher.exe" {
		t.Fatalf("preferRelaunchPath(%s) = %s, want install-root launcher", oldDesktop, got)
	}
}

func TestInstallStagedWindowsReleaseUnitPrefersVersioned(t *testing.T) {
	acceptWindowsPayloadManifestForTest(t)
	installDir := t.TempDir()
	staging := t.TempDir()
	writeVersionedWindowsStaging(t, staging, "p:", "v1.20.0",
		"tempora-desktop.exe",
		"tempora-cli.exe",
		"tempora-update-helper.exe",
		"tempora-launcher.exe",
		"tempora-guard.exe",
	)
	// Minimal claimed unit (versioned path does not need full flat file list).
	claimed := versionedWindowsTransaction(installDir, "v1.20.0", "2026-01-01T00:00:00Z")
	started, receipts, err := installStagedWindowsReleaseUnit(claimed, staging)
	if err != nil {
		t.Fatal(err)
	}
	if !started || receipts != nil {
		t.Fatalf("started=%v receipts=%v want started with nil receipts", started, receipts)
	}
	if !installlayout.HasCurrent(installDir) {
		t.Fatal("versioned activation did not write current.json")
	}
}
