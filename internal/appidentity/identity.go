package appidentity

const (
	// AppUserModelID belongs to Desktop, independently of installed Studio versions.
	// Keep it stable across upgrades and aligned with the Electron shell.
	AppUserModelID = "io.tempora.desktop"
	DisplayName    = "Tempora"

	// Old Desktop and Wails Studio shared this ID; ownership must precede migration.
	legacyAppUserModelID      = "Tempora"
	studioAppUserModelID      = "io.tempora.studio"
	legacyTauriAppUserModelID = "dev.tempora.desktop"
)
