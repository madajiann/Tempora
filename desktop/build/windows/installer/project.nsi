Unicode true

####
## Tempora per-user NSIS installer (Electron shell).
##
## This file is COMMITTED and fully self-contained: the Electron packaging
## script (desktop/packaging/package.mjs) generates tempora_project.nsh with
## the INFO_* identity defines, and every macro the old Wails template provided
## is inlined below. The customizations vs. a stock NSIS template:
##
##   1. REQUEST_EXECUTION_LEVEL "user" + InstallDir under $LOCALAPPDATA - install
##      without administrator rights. This lets the auto-updater re-run a freshly
##      downloaded installer in a visible progress-only mode with no UAC prompt.
##   2. Uninstall registry under HKCU (not HKLM) - a non-admin install cannot
##      write HKLM, so the uninstaller macros below use HKCU.
##   3. InstallDir is remembered across updates via InstallDirRegKey +
##      InstallLocation (HKCU\...\Uninstall\InstallLocation). When upgrading from
##      a build that did not write InstallLocation yet, .onInit falls back to the
##      old DisplayIcon path before using the default. Without this, every release
##      forces the user back to %LOCALAPPDATA%\Programs\Tempora even if they had
##      moved the install to a different drive (e.g. D:\Tools\Tempora); the
##      auto-updater would overwrite the wrong dir, leaving the old install
##      orphaned.
##   4. The payload is the flat Go executables plus the Electron app/ tree,
##      installed recursively with `File /r` into the versioned staging
##      directory that the signed Go activator publishes as versions/v<ver>/.
####

## Install per-user (no admin).
!define REQUEST_EXECUTION_LEVEL "user"

####
## Product identity (generated; provides INFO_* defines and TEMPORA_VERSION_TAG).
####
!if /FileExists "tempora_project.nsh"
!include "tempora_project.nsh"
!else
!error "tempora_project.nsh is missing; run desktop/packaging/package.mjs first"
!endif
!include "x64.nsh"
!include "WinVer.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"

# The build script writes this host-specific include before invoking makensis.
# Keep a Windows fallback so opening this script directly still behaves like a
# native Windows build.
!if /FileExists "tempora_host.nsh"
!include "tempora_host.nsh"
!endif
!ifndef TEMPORA_UNINST_FINALIZE
!define TEMPORA_UNINST_FINALIZE 'cmd.exe /C copy /Y "%1" "tempora-uninstall.exe" >NUL'
!endif

# The service executable stays the active version entry the thin launcher
# starts; it bootstraps app\Tempora.exe (Electron) and exits.
!define PRODUCT_EXECUTABLE "${INFO_PROJECTNAME}.exe"
!define TEMPORA_ELECTRON_EXECUTABLE "Tempora.exe"
!define UNINST_KEY_NAME "${INFO_COMPANYNAME}${INFO_PRODUCTNAME}"
!define UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${UNINST_KEY_NAME}"
RequestExecutionLevel "${REQUEST_EXECUTION_LEVEL}"

# Exactly one target architecture per installer, selected by the build script
# through the binary define it passes (values point at the staged service
# executable; only their presence selects the architecture).
!ifdef ARG_TEMPORA_AMD64_BINARY
!define ARCH "amd64"
!endif
!ifdef ARG_TEMPORA_ARM64_BINARY
!define ARCH "arm64"
!endif
!ifndef ARCH
!error "one of ARG_TEMPORA_AMD64_BINARY or ARG_TEMPORA_ARM64_BINARY is required; package-windows-desktop.sh passes it"
!endif

!macro tempora.checkArchitecture
    ${If} ${AtLeastWin10}
        !if "${ARCH}" == "amd64"
            ${if} ${IsNativeAMD64}
                Goto tempora_arch_ok
            ${EndIf}
        !else
            ${if} ${IsNativeARM64}
                Goto tempora_arch_ok
            ${EndIf}
        !endif

        IfSilent tempora_arch_silent tempora_arch_interactive
        tempora_arch_silent:
            SetErrorLevel 65
            Abort
        tempora_arch_interactive:
            MessageBox MB_OK "This product can't be installed on the current Windows architecture. Supports: ${ARCH}"
            Quit
    ${else}
        IfSilent tempora_win_silent tempora_win_interactive
        tempora_win_silent:
            SetErrorLevel 64
            Abort
        tempora_win_interactive:
            MessageBox MB_OK "This product is only supported on Windows 10 (Server 2016) and later."
            Quit
    ${EndIf}

    tempora_arch_ok:
!macroend

!macro tempora.setShellContext
    ${If} ${REQUEST_EXECUTION_LEVEL} == "admin"
        SetShellVarContext all
    ${else}
        SetShellVarContext current
    ${EndIf}
!macroend

# The release unit: the Go service executable plus the Electron app/ tree.
# package-windows-desktop.sh stages both next to this script before makensis.
!macro tempora.files
    File "/oname=${PRODUCT_EXECUTABLE}" "${PRODUCT_EXECUTABLE}"
    !if /FileExists "app\${TEMPORA_ELECTRON_EXECUTABLE}"
    File /r "app"
    !else
    !error "the Electron app tree is missing; run desktop/packaging/package.mjs first"
    !endif
!macroend

# Tempora registers no file associations or custom protocols; keep the hooks
# as no-ops so the install/uninstall flow keeps its shape.
!macro tempora.associateFiles
!macroend

!macro tempora.unassociateFiles
!macroend

!macro tempora.associateCustomProtocols
!macroend

!macro tempora.unassociateCustomProtocols
!macroend

# The version information for this two must consist of 4 parts
VIProductVersion "${INFO_PRODUCTVERSION}.0"
VIFileVersion    "${INFO_PRODUCTVERSION}.0"

VIAddVersionKey "CompanyName"     "${INFO_COMPANYNAME}"
VIAddVersionKey "FileDescription" "${INFO_PRODUCTNAME} Installer"
VIAddVersionKey "ProductVersion"  "${INFO_PRODUCTVERSION}"
VIAddVersionKey "FileVersion"     "${INFO_PRODUCTVERSION}"
VIAddVersionKey "LegalCopyright"  "${INFO_COPYRIGHT}"
VIAddVersionKey "ProductName"     "${INFO_PRODUCTNAME}"

# Enable HiDPI support. https://nsis.sourceforge.io/Reference/ManifestDPIAware
ManifestDPIAware true

!include "MUI.nsh"

!define MUI_ICON "..\icon.ico"
!define MUI_UNICON "..\icon.ico"
# !define MUI_WELCOMEFINISHPAGE_BITMAP "resources\leftimage.bmp" #Include this to add a bitmap on the left side of the Welcome Page. Must be a size of 164x314
!define MUI_FINISHPAGE_NOAUTOCLOSE # Wait on the INSTFILES page so the user can take a look into the details of the installation steps
!define MUI_ABORTWARNING # This will warn the user if they exit from the installer.

!define MUI_PAGE_CUSTOMFUNCTION_PRE tempora.skipSetupPageForUpdate
!insertmacro MUI_PAGE_WELCOME # Welcome to the installer page.
# !insertmacro MUI_PAGE_LICENSE "resources\eula.txt" # Adds a EULA page to the installer
!define MUI_PAGE_CUSTOMFUNCTION_PRE tempora.skipSetupPageForUpdate
!insertmacro MUI_PAGE_DIRECTORY # In which folder install page.
!define MUI_PAGE_CUSTOMFUNCTION_SHOW tempora.showUpdateProgress
!insertmacro MUI_PAGE_INSTFILES # Installing page.
!define MUI_PAGE_CUSTOMFUNCTION_PRE tempora.skipFinishPageForUpdate
!insertmacro MUI_PAGE_FINISH # Finished installation page.

!insertmacro MUI_UNPAGE_INSTFILES # Uinstalling page

!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "SimpChinese"
!insertmacro MUI_LANGUAGE "TradChinese"

LangString temporaUpdateTitle ${LANG_ENGLISH} "Updating Tempora"
LangString temporaUpdateTitle ${LANG_SIMPCHINESE} "正在更新 Tempora"
LangString temporaUpdateTitle ${LANG_TRADCHINESE} "正在更新 Tempora"
LangString temporaUpdateSubtitle ${LANG_ENGLISH} "Installing the verified update. Tempora will restart automatically."
LangString temporaUpdateSubtitle ${LANG_SIMPCHINESE} "正在安装已验证的更新，完成后 Tempora 将自动重启。"
LangString temporaUpdateSubtitle ${LANG_TRADCHINESE} "正在安裝已驗證的更新，完成後 Tempora 將自動重新啟動。"

LangString temporaActivating ${LANG_ENGLISH} "Verifying and publishing files (the progress bar pauses for 1-2 minutes; this is normal, please wait)..."
LangString temporaActivating ${LANG_SIMPCHINESE} "正在校验并提交安装文件（进度条会暂停 1-2 分钟，属正常现象，请勿关闭窗口）..."
LangString temporaActivating ${LANG_TRADCHINESE} "正在校驗並提交安裝文件（進度條會暫停 1-2 分鐘，屬正常現象，請勿關閉窗口）..."

LangString temporaActivateFailed ${LANG_ENGLISH} "Tempora could not activate the verified release. The previous version was left unchanged. Reason:"
LangString temporaActivateFailed ${LANG_SIMPCHINESE} "Tempora 激活安装内容失败，已保留原有版本不受影响。详细原因："
LangString temporaActivateFailed ${LANG_TRADCHINESE} "Tempora 激活安裝內容失敗，已保留原有版本不受影響。詳細原因："

## Preserve the first-pass generated uninstaller so the release workflow can
## Authenticode-sign it together with the other installed payload files.
## The second pass provides ARG_TEMPORA_SIGNED_UNINSTALLER and embeds that
## signed binary instead of generating another unsigned uninstaller.
!ifndef ARG_TEMPORA_SIGNED_UNINSTALLER
!uninstfinalize '${TEMPORA_UNINST_FINALIZE}'
!endif
#!finalize 'signtool --file "%1"'

Name "${INFO_PRODUCTNAME}"
OutFile "..\..\bin\${INFO_PROJECTNAME}-${ARCH}-installer.exe" # Name of the installer's file.
!define TEMPORA_DEFAULT_INSTALLDIR "$LOCALAPPDATA\Programs\${INFO_PRODUCTNAME}"
!define TEMPORA_UPDATE_HELPER "tempora-update-helper.exe"
!define TEMPORA_GUARD "tempora-guard.exe"
!define TEMPORA_LAUNCHER "tempora-launcher.exe"
!define TEMPORA_CLI "tempora-cli.exe"
!define TEMPORA_PORTABLE_ENTRY "Tempora.exe"
!define TEMPORA_LAYOUT_INSTALLER "tempora-layout-installer.exe"
!define TEMPORA_PAYLOAD_MANIFEST "tempora-payload.json"
!define TEMPORA_PAYLOAD_SIGNATURE "tempora-payload.json.minisig"
!define TEMPORA_LEGACY_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\Tempora"
!define TEMPORA_LEGACY_PRODUCT_KEY "Software\tempora\Tempora"
Var TemporaUpdateMode
Var TemporaStageMode
InstallDirRegKey HKCU "${UNINST_KEY}" "InstallLocation" # Reuse the previous install path on update; .onInit falls back to the default on first install.
InstallDir "${TEMPORA_DEFAULT_INSTALLDIR}" # Per-user install location (no admin rights required).
ShowInstDetails show # This will always show the installation details.

####
## Per-user uninstaller registry (HKCU). HKLM writes would fail without admin
## rights, so the uninstaller registration lives entirely under HKCU.
####
!macro tempora.writeUninstaller
    !ifdef ARG_TEMPORA_SIGNED_UNINSTALLER
    File "/oname=uninstall.exe" "${ARG_TEMPORA_SIGNED_UNINSTALLER}"
    !else
    WriteUninstaller "$INSTDIR\uninstall.exe"
    !endif

    WriteRegStr HKCU "${UNINST_KEY}" "Publisher" "${INFO_COMPANYNAME}"
    WriteRegStr HKCU "${UNINST_KEY}" "DisplayName" "${INFO_PRODUCTNAME}"
    WriteRegStr HKCU "${UNINST_KEY}" "DisplayVersion" "${INFO_PRODUCTVERSION}"
    !if /FileExists "${TEMPORA_LAUNCHER}"
    WriteRegStr HKCU "${UNINST_KEY}" "DisplayIcon" "$INSTDIR\${TEMPORA_LAUNCHER}"
    !else
    WriteRegStr HKCU "${UNINST_KEY}" "DisplayIcon" "$INSTDIR\${PRODUCT_EXECUTABLE}"
    !endif
    WriteRegStr HKCU "${UNINST_KEY}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
    WriteRegStr HKCU "${UNINST_KEY}" "QuietUninstallString" "$\"$INSTDIR\uninstall.exe$\" /S"
    # Persist the resolved install path so a subsequent update picks it up
    # via InstallDirRegKey above. Without this, every release would force the
    # user back to %LOCALAPPDATA%\Programs\Tempora even if they had moved
    # the install to a different drive (e.g. D:\Tools\Tempora). The auto-
    # updater trusts this persisted path, so it has to be present before the
    # visible progress-only re-install.
    WriteRegStr HKCU "${UNINST_KEY}" "InstallLocation" "$INSTDIR"

    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD HKCU "${UNINST_KEY}" "EstimatedSize" "$0"
!macroend

; Tauri 0.53 separately persisted $INSTDIR under its manufacturer/product key
; and restores that value before every later install. Clear only a same-root
; value so re-running 0.53 cannot overwrite the current uninstaller; preserve a
; genuinely separate legacy installation. If this cleanup fails, retain the old
; uninstall alias so a later update can retry the migration.
!macro tempora.deleteLegacyInstallerStateIfOwned
    StrCpy $1 "1"
    ClearErrors
    ReadRegStr $0 HKCU "${TEMPORA_LEGACY_PRODUCT_KEY}" ""
    ${If} $0 == "$INSTDIR"
        ClearErrors
        DeleteRegValue HKCU "${TEMPORA_LEGACY_PRODUCT_KEY}" ""
        ${If} ${Errors}
            StrCpy $1 "0"
        ${EndIf}
    ${ElseIf} $0 == "$\"$INSTDIR$\""
        ClearErrors
        DeleteRegValue HKCU "${TEMPORA_LEGACY_PRODUCT_KEY}" ""
        ${If} ${Errors}
            StrCpy $1 "0"
        ${EndIf}
    ${EndIf}

    ${If} $1 == "1"
        ClearErrors
        ReadRegStr $0 HKCU "${TEMPORA_LEGACY_UNINST_KEY}" "InstallLocation"
        ${If} $0 == "$INSTDIR"
            DeleteRegKey HKCU "${TEMPORA_LEGACY_UNINST_KEY}"
        ${ElseIf} $0 == "$\"$INSTDIR$\""
            DeleteRegKey HKCU "${TEMPORA_LEGACY_UNINST_KEY}"
        ${Else}
            ClearErrors
            ReadRegStr $0 HKCU "${TEMPORA_LEGACY_UNINST_KEY}" "UninstallString"
            ${If} $0 == "$INSTDIR\uninstall.exe"
                DeleteRegKey HKCU "${TEMPORA_LEGACY_UNINST_KEY}"
            ${ElseIf} $0 == "$\"$INSTDIR\uninstall.exe$\""
                DeleteRegKey HKCU "${TEMPORA_LEGACY_UNINST_KEY}"
            ${EndIf}
        ${EndIf}
    ${EndIf}
!macroend

!macro tempora.deleteUninstaller
    Delete "$INSTDIR\uninstall.exe"
    DeleteRegKey HKCU "${UNINST_KEY}"
!macroend

Function .onInit
   !insertmacro tempora.checkArchitecture

   ; The helper passes /TEMPORAUPDATE=1 and a final /D=<current directory>.
   ; This mode remains visible but skips every page that could change the
   ; destination, then closes automatically after the file copy so the helper
   ; can relaunch Tempora. A normal manual installer keeps the full wizard.
   StrCpy $TemporaUpdateMode "0"
   StrCpy $TemporaStageMode "0"
   ${GetParameters} $R0
   ClearErrors
   ${GetOptions} $R0 "/TEMPORAUPDATE=" $R1
   IfErrors tempora_update_mode_done
   StrCmp $R1 "1" 0 tempora_update_mode_done
   StrCpy $TemporaUpdateMode "1"

tempora_update_mode_done:
   ClearErrors
   ${GetOptions} $R0 "/TEMPORASTAGE=" $R2
   IfErrors tempora_stage_mode_done
   StrCmp $R2 "1" 0 tempora_stage_mode_done
   StrCpy $TemporaStageMode "1"

tempora_stage_mode_done:

   ; InstallDirRegKey leaves $INSTDIR empty when the InstallLocation value is
   ; missing. Older installers still wrote DisplayIcon, so use its parent folder
   ; as a compatibility bridge before falling back to the per-user default.
   StrCmp $INSTDIR "" 0 done
   ClearErrors
   ReadRegStr $0 HKCU "${UNINST_KEY}" "DisplayIcon"
   IfErrors legacy_location
   StrCmp $0 "" legacy_location
   ${GetParent} "$0" $INSTDIR
   StrCmp $INSTDIR "" legacy_location done

legacy_location:
   ; Tauri 0.53 used a different uninstall key and may have stored the selected
   ; directory with surrounding quotes (for example "D:\Tempora"). Reuse it
   ; only while its uninstaller still exists so a stale registry value cannot
   ; redirect the repair installer into an unrelated directory.
   ClearErrors
   ReadRegStr $0 HKCU "${TEMPORA_LEGACY_UNINST_KEY}" "InstallLocation"
   IfErrors legacy_uninstaller
   StrCmp $0 "" legacy_uninstaller
   StrCpy $1 $0 1
   StrCmp $1 "$\"" 0 legacy_location_ready
   StrCpy $1 $0 1 -1
   StrCmp $1 "$\"" 0 legacy_location_ready
   StrCpy $0 $0 -1 1

legacy_location_ready:
   IfFileExists "$0\uninstall.exe" 0 legacy_uninstaller
   StrCpy $INSTDIR $0
   Goto done

legacy_uninstaller:
   ClearErrors
   ReadRegStr $0 HKCU "${TEMPORA_LEGACY_UNINST_KEY}" "UninstallString"
   IfErrors fallback
   StrCmp $0 "" fallback
   StrCpy $1 $0 1
   StrCmp $1 "$\"" 0 legacy_uninstaller_ready
   StrCpy $1 $0 1 -1
   StrCmp $1 "$\"" 0 legacy_uninstaller_ready
   StrCpy $0 $0 -1 1

legacy_uninstaller_ready:
   IfFileExists "$0" 0 fallback
   ${GetParent} "$0" $INSTDIR
   StrCmp $INSTDIR "" fallback done

fallback:
   StrCpy $INSTDIR "${TEMPORA_DEFAULT_INSTALLDIR}"
done:
FunctionEnd

Function tempora.skipSetupPageForUpdate
   StrCmp $TemporaUpdateMode "1" 0 tempora_show_setup_page
   Abort

tempora_show_setup_page:
FunctionEnd

Function tempora.showUpdateProgress
   StrCmp $TemporaUpdateMode "1" 0 tempora_update_progress_done
   !insertmacro MUI_HEADER_TEXT "$(temporaUpdateTitle)" "$(temporaUpdateSubtitle)"
   SetDetailsView hide
   SetAutoClose true
   BringToFront

tempora_update_progress_done:
FunctionEnd

Function tempora.skipFinishPageForUpdate
   StrCmp $TemporaUpdateMode "1" 0 tempora_show_finish_page
   Abort

tempora_show_finish_page:
FunctionEnd

# Check every stable entry point before extracting a replacement.  A running
# shell may have already exited its Go service while still holding one of
# these files open; treating that as an installable state recreates the
# "installed but does not open" failure.  Silent installs fail closed.
Function tempora.waitForExecutableUnlock
   StrCpy $3 40
tempora_unlock_check:
   StrCpy $2 0
   IfFileExists "$INSTDIR\${PRODUCT_EXECUTABLE}" 0 tempora_unlock_versioned
   ClearErrors
   FileOpen $1 "$INSTDIR\${PRODUCT_EXECUTABLE}" a
   IfErrors tempora_unlock_stable_locked
   FileClose $1
   Goto tempora_unlock_versioned
tempora_unlock_stable_locked:
   StrCpy $2 1
tempora_unlock_versioned:
   IfFileExists "$INSTDIR\versions\v${INFO_PRODUCTVERSION}\${PRODUCT_EXECUTABLE}" 0 tempora_unlock_guard
   ClearErrors
   FileOpen $1 "$INSTDIR\versions\v${INFO_PRODUCTVERSION}\${PRODUCT_EXECUTABLE}" a
   IfErrors tempora_unlock_versioned_locked
   FileClose $1
   Goto tempora_unlock_guard
tempora_unlock_versioned_locked:
   StrCpy $2 1
tempora_unlock_guard:
   IfFileExists "$INSTDIR\${TEMPORA_GUARD}" 0 tempora_unlock_launcher
   ClearErrors
   FileOpen $1 "$INSTDIR\${TEMPORA_GUARD}" a
   IfErrors tempora_unlock_guard_locked
   FileClose $1
   Goto tempora_unlock_launcher
tempora_unlock_guard_locked:
   StrCpy $2 1
tempora_unlock_launcher:
   IfFileExists "$INSTDIR\${TEMPORA_LAUNCHER}" 0 tempora_unlock_cli
   ClearErrors
   FileOpen $1 "$INSTDIR\${TEMPORA_LAUNCHER}" a
   IfErrors tempora_unlock_launcher_locked
   FileClose $1
   Goto tempora_unlock_cli
tempora_unlock_launcher_locked:
   StrCpy $2 1
tempora_unlock_cli:
   IfFileExists "$INSTDIR\${TEMPORA_CLI}" 0 tempora_unlock_portable
   ClearErrors
   FileOpen $1 "$INSTDIR\${TEMPORA_CLI}" a
   IfErrors tempora_unlock_cli_locked
   FileClose $1
   Goto tempora_unlock_portable
tempora_unlock_cli_locked:
   StrCpy $2 1
tempora_unlock_portable:
   IfFileExists "$INSTDIR\${TEMPORA_PORTABLE_ENTRY}" 0 tempora_unlock_result
   ClearErrors
   FileOpen $1 "$INSTDIR\${TEMPORA_PORTABLE_ENTRY}" a
   IfErrors tempora_unlock_portable_locked
   FileClose $1
   Goto tempora_unlock_result
tempora_unlock_portable_locked:
   StrCpy $2 1
tempora_unlock_result:
   StrCmp $2 0 tempora_unlock_ok
   IntOp $3 $3 - 1
   IntCmp $3 0 tempora_unlock_failed tempora_unlock_retry tempora_unlock_retry
tempora_unlock_retry:
   Sleep 500
   Goto tempora_unlock_check
tempora_unlock_failed:
   SetErrorLevel 1618
   IfSilent tempora_unlock_abort tempora_unlock_prompt
tempora_unlock_prompt:
   MessageBox MB_ICONEXCLAMATION|MB_RETRYCANCEL "Tempora is still running. Close it and click Retry, or cancel this installation." IDRETRY tempora_unlock_check
tempora_unlock_abort:
   Abort
tempora_unlock_ok:
FunctionEnd


Section
    !insertmacro tempora.setShellContext

    ; /TEMPORASTAGE=1: flat executables plus the Electron app/ tree for
    ; 1.18–1.19.1 helpers (and the new helper's staging extract). Do not write
    ; shortcuts/uninstaller.
    ; Normal install: versioned-v1 layout under versions/v${INFO_PRODUCTVERSION}/
    ; with a permanent thin launcher at InstallRoot. Guard is only present in
    ; STAGE payloads (as the one-shot legacy migrator) and is not persisted on
    ; a normal install.
    StrCmp $TemporaStageMode "1" tempora_stage_payload
    ; The signed activator coordinates all installed versions before committing.
    Call tempora.waitForExecutableUnlock
    Goto tempora_normal_install

tempora_stage_payload:
    SetOutPath $INSTDIR
    !if /FileExists "${TEMPORA_PAYLOAD_MANIFEST}"
    File "/oname=${TEMPORA_PAYLOAD_MANIFEST}" "${TEMPORA_PAYLOAD_MANIFEST}"
    !endif
    !if /FileExists "${TEMPORA_PAYLOAD_SIGNATURE}"
    File "/oname=${TEMPORA_PAYLOAD_SIGNATURE}" "${TEMPORA_PAYLOAD_SIGNATURE}"
    !endif
    !insertmacro tempora.files
    !if /FileExists "${TEMPORA_UPDATE_HELPER}"
    File "/oname=${TEMPORA_UPDATE_HELPER}" "${TEMPORA_UPDATE_HELPER}"
    !endif
    !if /FileExists "${TEMPORA_GUARD}"
    File "/oname=${TEMPORA_GUARD}" "${TEMPORA_GUARD}"
    !endif
    !if /FileExists "${TEMPORA_LAUNCHER}"
    File "/oname=${TEMPORA_LAUNCHER}" "${TEMPORA_LAUNCHER}"
    !endif
    !if /FileExists "${TEMPORA_CLI}"
    File "/oname=${TEMPORA_CLI}" "${TEMPORA_CLI}"
    !endif
    Goto tempora_section_done

tempora_normal_install:
    ; Extract into an install-local temporary directory, then let the signed Go
    ; activator validate the complete release unit, transactionally publish the
    ; version/root entries, and strictly atomically replace current.json last.
    ; The normal/recovery installer therefore shares the same commit protocol as
    ; automatic updates instead of writing live files or current.json in place.
    System::Call 'kernel32::GetCurrentProcessId() i .R8'
    CreateDirectory "$INSTDIR\versions"
    StrCpy $R9 "$INSTDIR\versions\.installer-v${INFO_PRODUCTVERSION}-$R8"
    RMDir /r "$R9"
    CreateDirectory "$R9"
    SetOutPath "$R9"
    !insertmacro tempora.files
    !if /FileExists "${TEMPORA_UPDATE_HELPER}"
    File "/oname=${TEMPORA_UPDATE_HELPER}" "${TEMPORA_UPDATE_HELPER}"
    !else
    !warning "${TEMPORA_UPDATE_HELPER} was not found; Windows auto-update will fail safely until the helper is installed."
    !endif
    !if /FileExists "${TEMPORA_CLI}"
    File "/oname=${TEMPORA_CLI}" "${TEMPORA_CLI}"
    !else
    !warning "${TEMPORA_CLI} was not found; remote upload installation will be unavailable."
    !endif
    !if /FileExists "${TEMPORA_LAUNCHER}"
    File "/oname=${TEMPORA_LAUNCHER}" "${TEMPORA_LAUNCHER}"
    !endif

    SetOutPath "$PLUGINSDIR"
    !if /FileExists "${TEMPORA_GUARD}"
    File "/oname=${TEMPORA_LAYOUT_INSTALLER}" "${TEMPORA_GUARD}"
    !else
    !error "${TEMPORA_GUARD} was not found; normal installs require the signed layout activator."
    !endif
    DetailPrint "$(temporaActivating)"
    StrCpy $R7 ""
    IfSilent +2 0
    StrCpy $R7 "--interactive-recovery"
    nsExec::ExecToStack /OEM '"$PLUGINSDIR\${TEMPORA_LAYOUT_INSTALLER}" --install-root "$INSTDIR" --version "v${INFO_PRODUCTVERSION}" --activate-staging "$R9" --no-relaunch $R7'
    Pop $0
    Pop $R6
    StrCmp $0 "0" tempora_layout_activated
    ; Surface the real reason instead of a bare "aborted": details view,
    ; a persistent log file, and (interactive) a MessageBox with the text.
    DetailPrint "Tempora layout activation failed with exit code $0; the previous version remains active."
    StrCmp $R6 "" +2 0
    DetailPrint $R6
    ClearErrors
    FileOpen $R5 "$INSTDIR\tempora-install-error.log" w
    IfErrors tempora_errorlog_done
    FileWrite $R5 "exit code: $0$\r$\n"
    StrCmp $R6 "" tempora_errorlog_done
    FileWrite $R5 $R6
    FileWrite $R5 "$\r$\n"
    FileClose $R5
tempora_errorlog_done:
    RMDir /r "$R9"
    StrCmp $0 "1618" 0 +3
    SetErrorLevel 1618
    Goto tempora_activation_abort
    StrCmp $0 "1602" 0 +3
    SetErrorLevel 1602
    Goto tempora_activation_abort
    SetErrorLevel 1
tempora_activation_abort:
    IfSilent tempora_activation_abort_quiet
    MessageBox MB_ICONEXCLAMATION "$(temporaActivateFailed)$\n$\n$R6"
    IfFileExists "$INSTDIR\tempora-install-error.log" 0 +2
    Exec '"notepad.exe" "$INSTDIR\tempora-install-error.log"'
tempora_activation_abort_quiet:
    Abort "Tempora could not activate the verified release. The previous version was left unchanged."

tempora_layout_activated:
    RMDir /r "$R9"
    SetOutPath "$INSTDIR"

    ; Remove flat leftovers from prior 1.18–1.19 installs when overwriting.
    Delete "$INSTDIR\${PRODUCT_EXECUTABLE}"
    Delete "$INSTDIR\${TEMPORA_GUARD}"
    Delete "$INSTDIR\${TEMPORA_UPDATE_HELPER}"

    !if /FileExists "${TEMPORA_LAUNCHER}"
    ; Keep both target and icon on the stable launcher. Pointing IconLocation at
    ; versions\vX\tempora-desktop.exe leaves a blank shortcut as soon as version
    ; retention removes that directory after a later update.
    CreateShortcut "$SMPROGRAMS\${INFO_PRODUCTNAME}.lnk" "$INSTDIR\${TEMPORA_LAUNCHER}" "" "$INSTDIR\${TEMPORA_LAUNCHER}" 0
    CreateShortCut "$DESKTOP\${INFO_PRODUCTNAME}.lnk" "$INSTDIR\${TEMPORA_LAUNCHER}" "" "$INSTDIR\${TEMPORA_LAUNCHER}" 0
    ; Stamp the exact paths created in this shell context before the user can pin them.
    nsExec::ExecToLog /OEM '"$INSTDIR\${TEMPORA_LAUNCHER}" --repair-shortcuts "$SMPROGRAMS\${INFO_PRODUCTNAME}.lnk" "$DESKTOP\${INFO_PRODUCTNAME}.lnk"'
    Pop $0
    ${If} $0 != "0"
        DetailPrint "Warning: shortcut identity repair failed ($0); the next normal launch will retry."
    ${EndIf}
    !else
    CreateShortcut "$SMPROGRAMS\${INFO_PRODUCTNAME}.lnk" "$INSTDIR\versions\v${INFO_PRODUCTVERSION}\${PRODUCT_EXECUTABLE}"
    CreateShortCut "$DESKTOP\${INFO_PRODUCTNAME}.lnk" "$INSTDIR\versions\v${INFO_PRODUCTVERSION}\${PRODUCT_EXECUTABLE}"
    !endif

    !insertmacro tempora.associateFiles
    !insertmacro tempora.associateCustomProtocols
    !insertmacro tempora.writeUninstaller
    !insertmacro tempora.deleteLegacyInstallerStateIfOwned

tempora_section_done:
SectionEnd

Section "uninstall"
    !insertmacro tempora.setShellContext

    RMDir /r "$AppData\${PRODUCT_EXECUTABLE}" # Remove the legacy webview data directory

    ; Precision uninstall: flat leftovers, thin entry points, and version trees.
    Delete "$INSTDIR\${PRODUCT_EXECUTABLE}"
    Delete "$INSTDIR\${TEMPORA_UPDATE_HELPER}"
    Delete "$INSTDIR\${TEMPORA_GUARD}"
    Delete "$INSTDIR\${TEMPORA_LAUNCHER}"
    Delete "$INSTDIR\${TEMPORA_CLI}"
    Delete "$INSTDIR\${TEMPORA_PORTABLE_ENTRY}"
    Delete "$INSTDIR\current.json"
    RMDir /r "$INSTDIR\versions"

    Delete "$SMPROGRAMS\${INFO_PRODUCTNAME}.lnk"
    Delete "$DESKTOP\${INFO_PRODUCTNAME}.lnk"

    !insertmacro tempora.unassociateFiles
    !insertmacro tempora.unassociateCustomProtocols

    !insertmacro tempora.deleteUninstaller
    !insertmacro tempora.deleteLegacyInstallerStateIfOwned

    ; Only remove the installation directory if it is empty to prevent data loss
    RMDir $INSTDIR
SectionEnd
