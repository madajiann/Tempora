package main

type requiredDesktopAsset struct {
	group    string
	key      string
	filename string
}

var (
	requiredDesktopUpdaterAssets = []requiredDesktopAsset{
		{group: "platforms", key: "darwin-arm64", filename: "Tempora-darwin-arm64.zip"},
		{group: "platforms", key: "darwin-amd64", filename: "Tempora-darwin-amd64.zip"},
		{group: "platforms", key: "windows-amd64", filename: "Tempora-windows-amd64-installer.exe"},
		{group: "platforms", key: "windows-arm64", filename: "Tempora-windows-arm64-installer.exe"},
		{group: "platforms", key: "linux-amd64", filename: "Tempora-linux-amd64.tar.gz"},
		{group: "native_packages", key: "linux-amd64", filename: "Tempora-linux-amd64.deb"},
	}
	legacyDesktopDownloadAssets = []requiredDesktopAsset{
		{group: "downloads", key: "Tempora-darwin-universal.dmg", filename: "Tempora-darwin-universal.dmg"},
		{group: "downloads", key: "Tempora-windows-amd64.zip", filename: "Tempora-windows-amd64.zip"},
	}
	requiredDesktopDownloadAssets = append(append([]requiredDesktopAsset(nil), legacyDesktopDownloadAssets...),
		requiredDesktopAsset{group: "downloads", key: "Tempora-darwin-arm64.dmg", filename: "Tempora-darwin-arm64.dmg"},
		requiredDesktopAsset{group: "downloads", key: "Tempora-darwin-amd64.dmg", filename: "Tempora-darwin-amd64.dmg"},
	)
)
