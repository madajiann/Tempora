package main

import (
	"os"
	"strings"
	"testing"
)

func TestInstallerCommandLineUsesVisibleUpdateModeAndKeepsDFlagLast(t *testing.T) {
	got := installerCommandLine(`C:\Temp\Tempora Installer.exe`, `D:\Tools\Tempora App`)
	want := `"C:\Temp\Tempora Installer.exe" /TEMPORAUPDATE=1 /TEMPORASTAGE=1 /D=D:\Tools\Tempora App`
	if got != want {
		t.Fatalf("installerCommandLine = %q, want %q", got, want)
	}
	if strings.Contains(got, " /S") {
		t.Fatalf("auto-update must expose progress instead of using silent mode, got %q", got)
	}
	if !strings.HasSuffix(got, `/D=D:\Tools\Tempora App`) {
		t.Fatalf("/D= must be the final unquoted NSIS token, got %q", got)
	}
}

func TestWindowsUpdateHandoffArgsCarryParentInstallAndRelaunch(t *testing.T) {
	got := windowsUpdateHandoffArgs(
		4242,
		`C:\Users\Jane Doe\AppData\Local\Tempora\updates\Tempora-windows-amd64-installer.exe`,
		strings.Repeat("a", 64),
		`D:\Tools\Tempora App`,
		`D:\Tools\Tempora App\tempora-desktop.exe`,
		"v1.6.0",
		"2026-07-29T00:00:00Z",
		"transaction-1",
	)
	want := []string{
		"--parent-pid", "4242",
		"--installer", `C:\Users\Jane Doe\AppData\Local\Tempora\updates\Tempora-windows-amd64-installer.exe`,
		"--installer-sha256", strings.Repeat("a", 64),
		"--to-version", "v1.6.0",
		"--created-at", "2026-07-29T00:00:00Z",
		"--transaction-id", "transaction-1",
		"--install-dir", `D:\Tools\Tempora App`,
		"--relaunch", `D:\Tools\Tempora App\tempora-desktop.exe`,
	}
	if strings.Join(got, "\x00") != strings.Join(want, "\x00") {
		t.Fatalf("args = %#v, want %#v", got, want)
	}
}

func TestWindowsVersionedUpdateHandoffArgsDoNotRequireLegacyPendingIdentity(t *testing.T) {
	got := windowsVersionedUpdateHandoffArgs(
		4242,
		`C:\Temp\Tempora-installer.exe`,
		strings.Repeat("b", 64),
		`D:\Tools\Tempora`,
		`D:\Tools\Tempora\tempora-launcher.exe`,
		"v1.20.0",
	)
	want := []string{
		"--parent-pid", "4242",
		"--installer", `C:\Temp\Tempora-installer.exe`,
		"--installer-sha256", strings.Repeat("b", 64),
		"--to-version", "v1.20.0",
		"--install-layout", "versioned-v1",
		"--install-dir", `D:\Tools\Tempora`,
		"--relaunch", `D:\Tools\Tempora\tempora-launcher.exe`,
	}
	if strings.Join(got, "\x00") != strings.Join(want, "\x00") {
		t.Fatalf("args = %#v, want %#v", got, want)
	}
	for _, legacy := range []string{"--created-at", "--transaction-id"} {
		if strings.Contains(strings.Join(got, " "), legacy) {
			t.Fatalf("versioned handoff must not carry legacy field %s", legacy)
		}
	}
}

func TestWindowsInstallerScriptWaitsBeforeCopyingExecutable(t *testing.T) {
	data, err := os.ReadFile("build/windows/installer/project.nsi")
	if err != nil {
		t.Fatal(err)
	}
	script := string(data)
	for _, want := range []string{
		`!define TEMPORA_LEGACY_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\Tempora"`,
		`!define TEMPORA_LEGACY_PRODUCT_KEY "Software\tempora\Tempora"`,
		`!define TEMPORA_UPDATE_HELPER "tempora-update-helper.exe"`,
		`!define TEMPORA_GUARD "tempora-guard.exe"`,
		`!define TEMPORA_LAUNCHER "tempora-launcher.exe"`,
		`!define TEMPORA_CLI "tempora-cli.exe"`,
		`!define TEMPORA_PORTABLE_ENTRY "Tempora.exe"`,
		`!define TEMPORA_LAYOUT_INSTALLER "tempora-layout-installer.exe"`,
		`!define TEMPORA_PAYLOAD_MANIFEST "tempora-payload.json"`,
		`!define TEMPORA_PAYLOAD_SIGNATURE "tempora-payload.json.minisig"`,
		"Var TemporaUpdateMode",
		"Var TemporaStageMode",
		`${GetOptions} $R0 "/TEMPORAUPDATE=" $R1`,
		`${GetOptions} $R0 "/TEMPORASTAGE=" $R2`,
		"Function tempora.skipSetupPageForUpdate",
		"Function tempora.showUpdateProgress",
		`!define MUI_PAGE_CUSTOMFUNCTION_PRE tempora.skipFinishPageForUpdate`,
		"Function tempora.skipFinishPageForUpdate",
		`StrCmp $TemporaUpdateMode "1" 0 tempora_show_finish_page`,
		"SetAutoClose true",
		"BringToFront",
		`LangString temporaUpdateTitle ${LANG_ENGLISH} "Updating Tempora"`,
		`LangString temporaUpdateTitle ${LANG_SIMPCHINESE} "正在更新 Tempora"`,
		`LangString temporaUpdateTitle ${LANG_TRADCHINESE} "正在更新 Tempora"`,
		`LangString temporaUpdateSubtitle ${LANG_ENGLISH} "Installing the verified update. Tempora will restart automatically."`,
		`LangString temporaUpdateSubtitle ${LANG_SIMPCHINESE} "正在安装已验证的更新，完成后 Tempora 将自动重启。"`,
		`LangString temporaUpdateSubtitle ${LANG_TRADCHINESE} "正在安裝已驗證的更新，完成後 Tempora 將自動重新啟動。"`,
		"Function tempora.waitForExecutableUnlock",
		`FileOpen $1 "$INSTDIR\${PRODUCT_EXECUTABLE}" a`,
		`FileOpen $1 "$INSTDIR\versions\${TEMPORA_VERSION_TAG}\${PRODUCT_EXECUTABLE}" a`,
		`FileOpen $1 "$INSTDIR\${TEMPORA_GUARD}" a`,
		`FileOpen $1 "$INSTDIR\${TEMPORA_LAUNCHER}" a`,
		`FileOpen $1 "$INSTDIR\${TEMPORA_CLI}" a`,
		`FileOpen $1 "$INSTDIR\${TEMPORA_PORTABLE_ENTRY}" a`,
		"SetErrorLevel 1618",
		"Call tempora.waitForExecutableUnlock",
		`File "/oname=${TEMPORA_UPDATE_HELPER}" "${TEMPORA_UPDATE_HELPER}"`,
		`File "/oname=${TEMPORA_CLI}" "${TEMPORA_CLI}"`,
		`File "/oname=${TEMPORA_LAYOUT_INSTALLER}" "${TEMPORA_GUARD}"`,
		`nsExec::ExecToLog /OEM`,
		`Tempora layout activator output:`,
		`--activate-staging "$R9" --no-relaunch`,
		`LangString temporaActivateBusy ${LANG_ENGLISH}`,
		`LangString temporaActivateBusy ${LANG_SIMPCHINESE}`,
		`LangString temporaActivateBusy ${LANG_TRADCHINESE}`,
		`LangString temporaActivateLocked ${LANG_ENGLISH}`,
		`LangString temporaActivateLocked ${LANG_SIMPCHINESE}`,
		`LangString temporaActivateLocked ${LANG_TRADCHINESE}`,
		`MessageBox MB_ICONEXCLAMATION|MB_RETRYCANCEL "$(temporaActivateBusy)" IDRETRY tempora_layout_activate`,
		`MessageBox MB_ICONEXCLAMATION|MB_RETRYCANCEL "$(temporaActivateLocked)" IDRETRY tempora_layout_activate`,
		`File "/oname=${TEMPORA_PAYLOAD_MANIFEST}" "${TEMPORA_PAYLOAD_MANIFEST}"`,
		`File "/oname=${TEMPORA_PAYLOAD_SIGNATURE}" "${TEMPORA_PAYLOAD_SIGNATURE}"`,
		`Delete "$INSTDIR\${TEMPORA_UPDATE_HELPER}"`,
		`Delete "$INSTDIR\${TEMPORA_CLI}"`,
		`DeleteRegValue HKCU "${TEMPORA_LEGACY_PRODUCT_KEY}" ""`,
		`!insertmacro tempora.deleteLegacyInstallerStateIfOwned`,
	} {
		if !strings.Contains(script, want) {
			t.Fatalf("project.nsi missing %q", want)
		}
	}
	finishPageHook := strings.Index(script, "!define MUI_PAGE_CUSTOMFUNCTION_PRE tempora.skipFinishPageForUpdate")
	finishPage := strings.Index(script, "!insertmacro MUI_PAGE_FINISH")
	if finishPageHook < 0 || finishPage < 0 || finishPageHook > finishPage {
		t.Fatalf("update-only finish page hook must be attached to MUI_PAGE_FINISH (hook=%d page=%d)", finishPageHook, finishPage)
	}
	activation := script[strings.Index(script, "Tempora layout activator output:"):]
	retryPrompt := strings.Index(activation, `IDRETRY tempora_layout_activate`)
	discardStaging := strings.Index(activation, `RMDir /r "$R9"`)
	silentAbort := strings.Index(activation, "IfSilent tempora_activation_failed 0")
	if retryPrompt < 0 || discardStaging < 0 || retryPrompt > discardStaging || silentAbort < 0 || silentAbort > retryPrompt {
		t.Fatalf("activation failure must offer Retry before discarding the staged files, and silent installs must skip the prompt (retry=%d discard=%d silent=%d)", retryPrompt, discardStaging, silentAbort)
	}
	if levelBeforePrompt := strings.Index(activation, "SetErrorLevel"); levelBeforePrompt < retryPrompt {
		t.Fatalf("SetErrorLevel must follow the Retry prompt so a successful retry exits 0 (level=%d retry=%d)", levelBeforePrompt, retryPrompt)
	}
	wait := strings.Index(script, "Call tempora.waitForExecutableUnlock")
	copyFiles := strings.Index(script, "tempora_normal_install:")
	if wait < 0 || copyFiles < 0 || wait > copyFiles {
		t.Fatalf("installer must wait for the running exe to unlock before the normal-install payload extraction (wait=%d copy=%d)", wait, copyFiles)
	}
	stageBranch := strings.Index(script, "StrCmp $TemporaStageMode \"1\" tempora_stage_payload")
	if stageBranch < 0 || stageBranch > copyFiles {
		t.Fatalf("staging mode must bypass live executable unlock before payload extraction (branch=%d copy=%d)", stageBranch, copyFiles)
	}
	if !strings.Contains(script, "Goto tempora_section_done") {
		t.Fatal("staging mode must skip registry, shortcuts, associations, and uninstaller")
	}
	if strings.Contains(script, `FileOpen $0 "$INSTDIR\current.json" w`) {
		t.Fatal("normal installer must delegate the current.json commit to the atomic Go activator")
	}
	writeCurrent := strings.Index(script, `!insertmacro tempora.writeUninstaller`)
	deleteLegacy := strings.Index(script, `!insertmacro tempora.deleteLegacyInstallerStateIfOwned`)
	if writeCurrent < 0 || deleteLegacy < 0 || writeCurrent > deleteLegacy {
		t.Fatalf("installer must write the current uninstall entry before reconciling owned legacy state (write=%d delete=%d)", writeCurrent, deleteLegacy)
	}
	legacyMacro := script[strings.Index(script, `!macro tempora.deleteLegacyInstallerStateIfOwned`):strings.Index(script, `!macro tempora.deleteUninstaller`)]
	deleteLegacyLocation := strings.Index(legacyMacro, `DeleteRegValue HKCU "${TEMPORA_LEGACY_PRODUCT_KEY}" ""`)
	deleteLegacyAlias := strings.Index(legacyMacro, `DeleteRegKey HKCU "${TEMPORA_LEGACY_UNINST_KEY}"`)
	if deleteLegacyLocation < 0 || deleteLegacyAlias < 0 || deleteLegacyLocation > deleteLegacyAlias {
		t.Fatalf("installer must clear the same-root Tauri install-location breadcrumb before deleting its uninstall alias (location=%d alias=%d)", deleteLegacyLocation, deleteLegacyAlias)
	}
	metadataBranch := strings.Index(script, `tempora_stage_payload:`)
	metadataFile := strings.Index(script, `File "/oname=${TEMPORA_PAYLOAD_MANIFEST}"`)
	normalInstall := strings.Index(script, `tempora_normal_install:`)
	if metadataBranch < 0 || metadataFile < 0 || normalInstall < 0 || metadataBranch > metadataFile || metadataFile > normalInstall {
		t.Fatalf("payload manifest must be extracted only in staging mode (branch=%d file=%d)", metadataBranch, metadataFile)
	}
}

func TestWindowsInstallerUsesPreviousDirectoryAsManualInstallDefault(t *testing.T) {
	data, err := os.ReadFile("build/windows/installer/project.nsi")
	if err != nil {
		t.Fatal(err)
	}
	script := string(data)
	for _, want := range []string{
		`InstallDirRegKey HKCU "${UNINST_KEY}" "InstallLocation"`,
		`InstallDir "${TEMPORA_DEFAULT_INSTALLDIR}"`,
		`!insertmacro MUI_PAGE_DIRECTORY`,
		`!define MUI_PAGE_CUSTOMFUNCTION_PRE tempora.skipSetupPageForUpdate`,
		`StrCmp $TemporaUpdateMode "1" 0 tempora_show_setup_page`,
	} {
		if !strings.Contains(script, want) {
			t.Fatalf("project.nsi missing manual-install path contract %q", want)
		}
	}
	page := strings.Index(script, "!insertmacro MUI_PAGE_DIRECTORY")
	pageHook := strings.Index(script, "!define MUI_PAGE_CUSTOMFUNCTION_PRE tempora.skipSetupPageForUpdate\n!insertmacro MUI_PAGE_DIRECTORY")
	if page < 0 || pageHook < 0 || pageHook > page {
		t.Fatal("directory selection page must remain available for manual installs")
	}
	if strings.Contains(script, `StrCpy $TemporaUpdateMode "1"
	Goto tempora_show_setup_page`) {
		t.Fatal("automatic updates must not reopen the manual directory selection page")
	}
}

func TestDesktopBuildScriptCompilesAndPackagesWindowsUpdateHelper(t *testing.T) {
	data, err := os.ReadFile("../scripts/desktop-build.sh")
	if err != nil {
		t.Fatal(err)
	}
	script := string(data)
	for _, want := range []string{
		`UPDATE_HELPER="tempora-update-helper.exe"`,
		`go build -trimpath -o "$windows_resource_tool" ./cmd/windows-resource`,
		`GOOS=windows GOARCH="$arch" go build`,
		`./cmd/update-helper`,
		`"$installer_dir/$UPDATE_HELPER"`,
		`stamp_windows_executable "$installer_dir/$UPDATE_HELPER" "Tempora Update Helper"`,
		`for name in "$BINNAME.exe" "$GUARDNAME.exe" "$LAUNCHERNAME.exe" "$UPDATE_HELPER" "$WINDOWS_CLINAME.exe" "tempora-uninstall.exe"; do`,
		`cp "$installer_dir/$name" "$payload_dir/$name"`,
	} {
		if !strings.Contains(script, want) {
			t.Fatalf("desktop-build.sh missing %q", want)
		}
	}

	packageData, err := os.ReadFile("../scripts/package-windows-desktop.sh")
	if err != nil {
		t.Fatal(err)
	}
	packager := string(packageData)
	for _, want := range []string{
		`cp "$PAYLOAD/$UPDATE_HELPER" "$INSTALLER_DIR/$UPDATE_HELPER"`,
		`cp "$PAYLOAD/$UPDATE_HELPER" "$portable_staging/versions/$version_label/$UPDATE_HELPER"`,
		`"$ROOT/scripts/verify-windows-portable.sh" "$portable_staging"`,
	} {
		if !strings.Contains(packager, want) {
			t.Fatalf("package-windows-desktop.sh missing %q", want)
		}
	}
}

func TestWindowsUpdateRequiresObservedHelperHandoff(t *testing.T) {
	data, err := os.ReadFile("updater_windows.go")
	if err != nil {
		t.Fatal(err)
	}
	source := string(data)
	if !strings.Contains(source, "return startWindowsUpdateHelper(") {
		t.Fatal("Windows update handoff does not require the observed helper path")
	}
	if strings.Contains(source, "return installerCommand(installerPath, installDir).Start()") {
		t.Fatal("Windows update silently falls back to an unobserved installer")
	}
	if !strings.Contains(source, "cmd := proc.Command(helperPath") || strings.Contains(source, "proc.VisibleCommand(helperPath") {
		t.Fatal("Windows handoff helper should stay hidden while NSIS shows update progress")
	}
	helperData, err := os.ReadFile("cmd/update-helper/main_windows.go")
	if err != nil {
		t.Fatal(err)
	}
	helperSource := string(helperData)
	if !strings.Contains(helperSource, "reconcileWindowsUninstallRegistrationFn(installDir, toVersion)") {
		t.Fatal("versioned Windows activation must refresh its managed uninstall registration")
	}
	if strings.Contains(helperSource, "installerCommandLine(installer, installDir), HideWindow: true") {
		t.Fatal("update helper still hides the NSIS progress window")
	}
}
