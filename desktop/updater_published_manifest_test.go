package main

// Release-gate test: validate a published latest.json with the exact same code
// path the desktop updater uses at runtime. Feed it a file path via
// TEMPORA_MANIFEST_CHECK (defaults to dist/latest.json if present).
// Run: go test ./ -run TestPublishedManifestPassesUpdaterValidation -v
//
// This exists because v0.1.2 shipped with asset URLs pinned to the
// desktop-v0.1.0 tag while the manifest version was v0.1.2; the updater's
// desktopAssetBases check rejected the whole manifest and every client showed
// "update: invalid stable version" with no version to update to. This test
// makes that class of mistake fail the release instead of the users.

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
