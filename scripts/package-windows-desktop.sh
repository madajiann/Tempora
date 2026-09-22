#!/usr/bin/env bash
# Rebuild the Windows portable archive and NSIS installer from one canonical
# payload directory: the flat Go executables plus the Electron app/ tree. The
# release workflow calls this once with unsigned files after compilation, then
# again with Authenticode-signed files returned by SignPath. Re-running makensis
# after payload signing is what makes the installed executables signed too;
# signing only the finished NSIS file signs the container, not the files that
# Defender scans after installation.
set -euo pipefail

arch="${1:?usage: package-windows-desktop.sh <amd64|arm64> <payload-dir>}"
payload_input="${2:?usage: package-windows-desktop.sh <amd64|arm64> <payload-dir>}"

case "$arch" in
amd64 | arm64) ;;
*)
	echo "unsupported Windows architecture: $arch" >&2
	exit 1
	;;
esac

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# On MSYS/Git Bash, native tools (node, makensis, go) must receive Windows
# style paths; MSYS path conversion can be disabled by the host environment.
unset MSYS2_ARG_CONV_EXCL
case "$(uname -s 2>/dev/null || printf '%s' unknown)" in
	MINGW* | MSYS* | CYGWIN*)
		ROOT="$(cd "$ROOT" && pwd -W)"
		;;
esac
DESKTOP="$ROOT/desktop"
INSTALLER_DIR="$DESKTOP/build/windows/installer"
BIN_DIR="$DESKTOP/build/bin"
DIST="$ROOT/dist"
APPNAME="Tempora"
BINNAME="tempora-desktop"
GUARDNAME="tempora-guard"
LAUNCHERNAME="tempora-launcher"
UPDATE_HELPER="tempora-update-helper.exe"
WINDOWS_CLINAME="tempora-cli"
WINDOWS_CLI_ENTRY="tempora-cli-launcher.exe"
SIGNING_LIST="signing-files.txt"
PAYLOAD_MANIFEST="tempora-payload.json"
PAYLOAD_SIGNATURE="$PAYLOAD_MANIFEST.minisig"

[ -d "$payload_input" ] || { echo "Windows payload directory is missing: $payload_input" >&2; exit 1; }
PAYLOAD="$(cd "$payload_input" && pwd)"
case "$(uname -s 2>/dev/null || printf '%s' unknown)" in
	MINGW* | MSYS* | CYGWIN*)
		PAYLOAD="$(cd "$PAYLOAD" && pwd -W)"
		;;
esac

required_payload=(
	"$BINNAME.exe"
	"$GUARDNAME.exe"
	"$LAUNCHERNAME.exe"
	"$UPDATE_HELPER"
	"$WINDOWS_CLINAME.exe"
	"tempora-uninstall.exe"
)
for name in "${required_payload[@]}"; do
	[ -s "$PAYLOAD/$name" ] || { echo "Windows payload file is missing or empty: $name" >&2; exit 1; }
done

payload_exe_count=$(find "$PAYLOAD" -maxdepth 1 -type f -iname '*.exe' | wc -l | tr -d '[:space:]')
[ "$payload_exe_count" = "${#required_payload[@]}" ] || {
	echo "Windows payload must contain exactly ${#required_payload[@]} flat executables, found $payload_exe_count" >&2
	exit 1
}

# The Electron tree is part of the release unit; signing-files.txt (written by
# desktop/packaging/signing-files.mjs) enumerates every PE file inside it, so
# --check fails closed when the tree and the signing list drift apart.
[ -s "$PAYLOAD/$SIGNING_LIST" ] || { echo "Windows payload signing list is missing: $SIGNING_LIST" >&2; exit 1; }
node "$DESKTOP/packaging/signing-files.mjs" "$PAYLOAD" --check

manifest_present=0
signature_present=0
[ -s "$PAYLOAD/$PAYLOAD_MANIFEST" ] && manifest_present=1
[ -s "$PAYLOAD/$PAYLOAD_SIGNATURE" ] && signature_present=1
if [ "$manifest_present" != "$signature_present" ]; then
	echo "Windows payload manifest and signature must be provided together" >&2
	exit 1
fi
if [ "${TEMPORA_REQUIRE_PAYLOAD_MANIFEST:-0}" = "1" ] && [ "$manifest_present" != "1" ]; then
	echo "signed Windows packaging requires $PAYLOAD_MANIFEST and $PAYLOAD_SIGNATURE" >&2
	exit 1
fi

# Replace every source consumed by project.nsi before compiling the installer.
# Copying preserves the Authenticode certificate table returned by SignPath.
cp "$PAYLOAD/$BINNAME.exe" "$INSTALLER_DIR/$BINNAME.exe"
cp "$PAYLOAD/$GUARDNAME.exe" "$INSTALLER_DIR/$GUARDNAME.exe"
cp "$PAYLOAD/$LAUNCHERNAME.exe" "$INSTALLER_DIR/$LAUNCHERNAME.exe"
cp "$PAYLOAD/$UPDATE_HELPER" "$INSTALLER_DIR/$UPDATE_HELPER"
cp "$PAYLOAD/$WINDOWS_CLINAME.exe" "$INSTALLER_DIR/$WINDOWS_CLINAME.exe"
rm -rf -- "$INSTALLER_DIR/app"
cp -R "$PAYLOAD/app" "$INSTALLER_DIR/app"
rm -f -- "$INSTALLER_DIR/$PAYLOAD_MANIFEST" "$INSTALLER_DIR/$PAYLOAD_SIGNATURE"
if [ "$manifest_present" = "1" ]; then
	cp "$PAYLOAD/$PAYLOAD_MANIFEST" "$INSTALLER_DIR/$PAYLOAD_MANIFEST"
	cp "$PAYLOAD/$PAYLOAD_SIGNATURE" "$INSTALLER_DIR/$PAYLOAD_SIGNATURE"
fi

[ -s "$INSTALLER_DIR/tempora_project.nsh" ] || {
	echo "tempora_project.nsh is missing; run desktop/packaging/package.mjs first" >&2
	exit 1
}

# Delete only generated installers so a stale first-pass package cannot be
# mistaken for the rebuilt payload-signed installer.
mkdir -p "$BIN_DIR"
find "$BIN_DIR" -maxdepth 1 -type f -name '*installer*.exe' -delete
binary_define="ARG_TEMPORA_AMD64_BINARY"
[ "$arch" = arm64 ] && binary_define="ARG_TEMPORA_ARM64_BINARY"
binary_path="$INSTALLER_DIR/$BINNAME.exe"
uninstaller_path="$PAYLOAD/tempora-uninstall.exe"
if command -v cygpath >/dev/null 2>&1; then
	binary_path="$(cygpath -w "$binary_path")"
	uninstaller_path="$(cygpath -w "$uninstaller_path")"
fi
(
	cd "$INSTALLER_DIR"
	makensis \
		"-D${binary_define}=${binary_path}" \
		"-DARG_TEMPORA_SIGNED_UNINSTALLER=${uninstaller_path}" \
		project.nsi
)

installer=$(find "$BIN_DIR" -maxdepth 1 -type f -name '*installer*.exe' -print -quit)
[ -n "$installer" ] && [ -s "$installer" ] || { echo "makensis did not produce a Windows installer" >&2; exit 1; }

mkdir -p "$DIST"
dist_installer="$DIST/${APPNAME}-windows-${arch}-installer.exe"
dist_portable="$DIST/${APPNAME}-windows-${arch}.zip"
cp "$installer" "$dist_installer"

# v0.1.4: pin the staging dir to the user-local temp directory (NTFS C:)
# instead of TMPDIR — TMPDIR once resolved to G:/tmp where files written
# from bash were not readable by native node right after (build lock).
tmp_base="${LOCALAPPDATA:-C:/Windows/Temp}"
tmp_base="${tmp_base//\\//}"
portable_staging=$(mktemp -d "$tmp_base/mktemp.XXXXXXXX")
cleanup() {
	case "$portable_staging" in
	"$tmp_base"/mktemp.* | /tmp/*) rm -rf -- "$portable_staging" ;;
	*) echo "refusing to clean unexpected portable staging directory: $portable_staging" >&2 ;;
	esac
}
trap cleanup EXIT

# versioned-v1 portable layout (no Guard, no flat desktop at InstallRoot); the
# Electron bundle is the app/ tree member of the active version directory.
version_label="${VERSION:-}"
if [ -z "$version_label" ] && [ -f "$INSTALLER_DIR/tempora_project.nsh" ]; then
	version_label=$(sed -n 's/^!define TEMPORA_VERSION_TAG "\(.*\)"$/\1/p' "$INSTALLER_DIR/tempora_project.nsh" | tr -d '\r' | head -n 1)
fi
version_label="${version_label:-0.0.0}"
case "$version_label" in
v*) ;;
*) version_label="v${version_label}" ;;
esac
mkdir -p "$portable_staging/versions/$version_label"
cp "$PAYLOAD/$BINNAME.exe" "$portable_staging/versions/$version_label/$BINNAME.exe"
cp "$PAYLOAD/$UPDATE_HELPER" "$portable_staging/versions/$version_label/$UPDATE_HELPER"
cp "$PAYLOAD/$WINDOWS_CLINAME.exe" "$portable_staging/versions/$version_label/$WINDOWS_CLINAME.exe"
cp -R "$PAYLOAD/app" "$portable_staging/versions/$version_label/app"
cp "$PAYLOAD/$LAUNCHERNAME.exe" "$portable_staging/$APPNAME.exe"
cli_entry="$PAYLOAD/app/resources/bin/$WINDOWS_CLI_ENTRY"
[ -s "$cli_entry" ] || { echo "Windows CLI entry is missing: $cli_entry" >&2; exit 1; }
cp "$cli_entry" "$portable_staging/$WINDOWS_CLINAME.exe"
cat >"$portable_staging/current.json" <<EOF
{
  "schemaVersion": 1,
  "activeVersion": "$version_label",
  "activeDir": "versions/$version_label"
}
EOF
"$ROOT/scripts/verify-windows-portable.sh" "$portable_staging" canonical "$PAYLOAD/$LAUNCHERNAME.exe"

# --- local-build AV-race hardening (v0.1.4) -----------------------------------
# Tencent PC Manager (QQPCMgr RTP) opens every freshly written PE file to scan
# it and holds that handle for seconds. The staged copies above are only
# milliseconds old when the archiver reads them, so the archiver loses the race
# ("the file is in use by another process") and Compress-Archive aborts without
# writing any archive at all -> verify.mjs then dies on a missing file. This is
# local-toolchain behaviour and does not affect CI. Two mitigations, both local:
#   1. warm_staged_binaries: probe-read every staged PE until the scanner has
#      released it, turning an unpredictable race into an explicit bounded wait.
#   2. archive with bounded retries and reject a truncated archive.
warm_staged_binaries() {
	local dir="$1" attempts="${2:-30}" delay="${3:-2}"
	local pending round f
	# C-style loop: no dependency on seq (Git Bash tooling is unreliable here).
	for ((round = 1; round <= attempts; round++)); do
		pending=0
		while IFS= read -r -d '' f; do
			# A failed probe read means a scanner still holds the file.
			if ! head -c 1 "$f" >/dev/null 2>&1; then
				pending=$((pending + 1))
			fi
		done < <(find "$dir" -type f \( -iname '*.exe' -o -iname '*.dll' -o -iname '*.node' \) -print0 2>/dev/null)
		if [ "$pending" = "0" ]; then
			[ "$round" != "1" ] && echo "==> staged binaries unlocked after $round probe round(s)" >&2
			return 0
		fi
		echo "==> $pending staged binaries still locked by a scanner; waiting ${delay}s (round $round/$attempts)" >&2
		sleep "$delay"
	done
	echo "==> staged binaries still locked after $((attempts * delay))s; the archive step may fail" >&2
	return 1
}

# A partially written archive lacks the end-of-central-directory record. Fails
# open: if the probe tools are unavailable, do not block a perfectly good file.
archive_looks_complete() {
	local hex
	command -v tail >/dev/null 2>&1 || return 0
	command -v od >/dev/null 2>&1 || return 0
	command -v tr >/dev/null 2>&1 || return 0
	# Assign first: piping straight into `grep -q` trips `set -o pipefail` via
	# SIGPIPE and would look like a truncated archive.
	hex=$(tail -c 64 "$1" 2>/dev/null | od -An -tx1 2>/dev/null | tr -d ' \n')
	case "$hex" in
	*504b0506*) return 0 ;;
	esac
	return 1
}

warm_staged_binaries "$portable_staging" || true

archive_attempts="${TEMPORA_ARCHIVE_ATTEMPTS:-4}"
archive_ok=0
if command -v powershell.exe >/dev/null 2>&1; then
	portable_staging_win="$portable_staging"
	dist_portable_win="$dist_portable"
	if command -v cygpath >/dev/null 2>&1; then
		portable_staging_win="$(cygpath -w "$portable_staging")"
		dist_portable_win="$(cygpath -w "$dist_portable")"
	fi
	for ((attempt = 1; attempt <= archive_attempts; attempt++)); do
		rm -f -- "$dist_portable"
		# The archiver reports non-terminating errors without a failing exit
		# status, so success is judged by the artifact, not the exit code.
		powershell.exe -NoProfile -Command \
			"Compress-Archive -CompressionLevel Optimal -Force -Path '$portable_staging_win\\*' -DestinationPath '$dist_portable_win'" || true
		if [ -s "$dist_portable" ] && archive_looks_complete "$dist_portable"; then
			archive_ok=1
			break
		fi
		echo "==> Compress-Archive attempt $attempt/$archive_attempts produced no usable archive; retrying after a settle wait" >&2
		warm_staged_binaries "$portable_staging" 5 2 || true
		sleep 8
	done
fi

if [ "$archive_ok" = "0" ] && command -v zip >/dev/null 2>&1; then
	# macOS/Linux cross-builds do not ship powershell.exe; the portable layout
	# is ordinary ZIP data, so use the host zip utility in that case. zip is
	# also the fallback when Compress-Archive keeps losing the AV race.
	# zip updates an existing archive and otherwise retains previous version
	# directories. Always assemble a fresh distributable from this payload.
	for ((attempt = 1; attempt <= archive_attempts; attempt++)); do
		rm -f -- "$dist_portable"
		(
			cd "$portable_staging"
			zip -q -9 -r "$dist_portable" .
		) || true
		if [ -s "$dist_portable" ] && archive_looks_complete "$dist_portable"; then
			archive_ok=1
			break
		fi
		echo "==> zip attempt $attempt/$archive_attempts produced no usable archive; retrying after a settle wait" >&2
		sleep 8
	done
fi

[ "$archive_ok" = "1" ] || {
	echo "failed to create the Windows portable archive: $dist_portable" >&2
	exit 1
}

# The second SignPath request signs the outer installer only after verifying
# these already-signed payload files (flat executables plus the app/ tree).
# Keeping one exact bundle makes the artifact configuration fail closed if a
# required installed executable is missing.
installer_bundle="$DESKTOP/build/windows/installer-signing-bundle"
rm -rf -- "$installer_bundle"
mkdir -p "$installer_bundle"
cp "$dist_installer" "$installer_bundle/"
for name in "${required_payload[@]}"; do
	cp "$PAYLOAD/$name" "$installer_bundle/$name"
done
cp -R "$PAYLOAD/app" "$installer_bundle/app"
cp "$PAYLOAD/$SIGNING_LIST" "$installer_bundle/$SIGNING_LIST"

echo "==> rebuilt Windows $arch installer and portable archive from $PAYLOAD"
