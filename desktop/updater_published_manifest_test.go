package main

// Release-gate test: validate a published latest.json through the exact code path
// the desktop updater uses at runtime (TEMPORA_MANIFEST_CHECK, default dist/latest.json);
// born from v0.1.2 shipping manifest URLs pinned to the wrong tag — fail the release, not users.

import (
	"encoding/json"
	"os"
	"testing"

	"tempora/desktop/internal/update"
)

func TestPublishedManifestPassesUpdaterValidation(t *testing.T) {
	path := os.Getenv("TEMPORA_MANIFEST_CHECK")
	if path == "" {
		path = "../dist/latest.json"
	}
	raw, err := os.ReadFile(path)
	if err != nil {
		t.Skipf("no published manifest at %s: %v", path, err)
	}
	var m update.Manifest
	if err := json.Unmarshal(raw, &m); err != nil {
		t.Fatalf("manifest does not parse: %v", err)
	}
	if err := validateDesktopManifest("stable", &m); err != nil {
		t.Fatalf("published manifest FAILS updater validation (users would see update errors): %v", err)
	}
	// Also confirm every base implied by the manifest version is reachable for
	// at least the primary platform asset (mirror first, then GitHub).
	base, err := validateManifestAsset("stable", m.Version, "Tempora-windows-amd64-installer.exe", m.Platforms["windows-amd64"], m.Downloads == nil)
	if err != nil {
		t.Fatalf("windows-amd64 installer asset rejected: %v", err)
	}
	t.Logf("manifest OK; primary asset base: %s", base)
}
