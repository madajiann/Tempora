#!/usr/bin/env bash
# Build and package the Electron desktop app for one platform. Electron's
# Chromium shell cannot cross-compile the native targets from one host, so this
# runs on a native runner per target (see .github/workflows/release-desktop.yml)
# and is invoked once per matrix entry.
#
# Output lands in <repo>/dist/ with stable, platform-keyed names that
# desktop/cmd/sign's `manifest` subcommand maps back to update.PlatformKey:
#   macOS:   Tempora-darwin-<arm64|amd64>.zip           (ditto archive; updater channel)
#            Tempora-darwin-<arch>.dmg                  (drag-to-install; human download)
#   Windows: Tempora-windows-<arch>-installer.exe       (NSIS per-user installer; updater channel)
#            Tempora-windows-<arch>.zip                 (portable human download)
#   Linux:   Tempora-linux-<arch>.tar.gz                (desktop + guard + CLI + app/ tree; portable updater)
#            Tempora-linux-<arch>.deb                   (Debian/Ubuntu package; native updater)
#
# Usage: scripts/desktop-build.sh <os/arch> <version> [channel]
#   e.g. scripts/desktop-build.sh darwin/arm64 v1.1.0
#        scripts/desktop-build.sh darwin/arm64 v1.5.0-preview.42 preview
#
# Requirements:
#   - Go toolchain matching desktop/go.mod (>= 1.25; the `toolchain` directive
#     auto-downloads when GOTOOLCHAIN=auto)
#   - Node >= 24 and pnpm 10 (the same major versions used by CI and releases)
#   - A pnpm-installed desktop workspace (this script runs
#     `pnpm --dir desktop install --frozen-lockfile` when node_modules is absent)
set -euo pipefail

build_started_seconds=$SECONDS

PLATFORM="${1:?usage: desktop-build.sh <os/arch> <version> [channel]}"
VERSION="${2:?usage: desktop-build.sh <os/arch> <version> [channel]}"
CHANNEL="${3:-stable}"

os="${PLATFORM%/*}"
arch="${PLATFORM#*/}"

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APPNAME="Tempora"            # Electron productName -> Tempora.app / Tempora.exe
BINNAME="tempora-desktop"    # Go desktop service (and the active version entry the launcher starts)
CLINAME="tempora"            # bundled CLI sidecar used for remote serve upload
WINDOWS_CLINAME="tempora-cli" # Windows cannot store Tempora.exe and tempora.exe separately
WINDOWS_CLI_ENTRY="tempora-cli-launcher.exe"
GUARDNAME="tempora-guard"
LAUNCHERNAME="tempora-launcher"
windows_resource_tool_dir=""
windows_host_include=""

# On MSYS/Git Bash, native tools (go, makensis, cmd.exe) must receive Windows
# style paths; MSYS path conversion can be disabled by the host environment,
# so hand them native paths explicitly.
unset MSYS2_ARG_CONV_EXCL
case "$(uname -s 2>/dev/null || printf '%s' unknown)" in
	MINGW* | MSYS* | CYGWIN*)
		ROOT="$(cd "$ROOT" && pwd -W)"
		mktempd() {
			local t="${LOCALAPPDATA:-C:/Windows/Temp}"
			t="${t//\\//}"
			mktemp -d "$t/mktemp.XXXXXXXX"
		}
		;;
	*)
		mktempd() { mktemp -d; }
		;;
esac

# desktop/ is a nested Go module, so the Go toolchain cannot discover the
# repository VCS revision for the service binary. Link the same source identity
# into both Desktop and its CLI sidecar.
git_in_root() { (cd "$ROOT" && git "$@"); }
SOURCE_REVISION="$(git -C "$ROOT" rev-parse --verify HEAD)"
SOURCE_SHA="$SOURCE_REVISION"
if ! git -C "$ROOT" diff-index --quiet HEAD --; then
	SOURCE_REVISION="$SOURCE_REVISION+dirty"
fi
# Short commit + real UTC build clock for CLI `version --verbose/--json`.
GIT_COMMIT="$(cd "$ROOT" && git rev-parse --short=12 HEAD 2>/dev/null || echo unknown)"
BUILD_TIME_UTC="${TEMPORA_BUILD_TIME_UTC:-$(date -u +%Y-%m-%dT%H:%M:%SZ)}"
product_docs_ldflags="-X tempora/internal/productdocs.linkedVersion=$VERSION -X tempora/internal/productdocs.linkedRevision=$SOURCE_REVISION"
cli_identity_ldflags="-X main.version=$VERSION -X main.gitCommit=$GIT_COMMIT -X main.buildTimeUTC=$BUILD_TIME_UTC $product_docs_ldflags"

cleanup() {
	if [ -n "$windows_resource_tool_dir" ]; then
		rm -rf "$windows_resource_tool_dir"
	fi
	if [ -n "$windows_host_include" ]; then
		rm -f "$windows_host_include"
	fi
}
trap cleanup EXIT

cd "$ROOT/desktop"

# build_guard produces the one-shot legacy migrator still named tempora-guard
# in compatibility payloads for 1.18–1.19.1 updaters. Source is intentionally
# separate from the removed Guard recovery product.
build_guard() {
	echo "==> go build Tempora legacy migrator (compat name tempora-guard)"
	mkdir -p "$(dirname "$guard_out")"
	if [ "$arch" = universal ]; then
		guard_tmp=$(mktempd)
		(cd "$ROOT" && GOOS=darwin GOARCH=amd64 CGO_ENABLED=0 go build -trimpath -ldflags="-s -w -X main.version=$VERSION" -o "$guard_tmp/amd64" ./cmd/tempora-legacy-migrator)
		(cd "$ROOT" && GOOS=darwin GOARCH=arm64 CGO_ENABLED=0 go build -trimpath -ldflags="-s -w -X main.version=$VERSION" -o "$guard_tmp/arm64" ./cmd/tempora-legacy-migrator)
		lipo -create "$guard_tmp/amd64" "$guard_tmp/arm64" -output "$guard_out"
		rm -rf "$guard_tmp"
	else
		(cd "$ROOT" && GOOS="$os" GOARCH="$arch" CGO_ENABLED=0 go build -trimpath -ldflags="-s -w -X main.version=$VERSION" -o "$guard_out" ./cmd/tempora-legacy-migrator)
	fi
}

build_cli() {
	echo "==> go build Tempora CLI sidecar"
	mkdir -p "$(dirname "$cli_out")"
	if [ "$arch" = universal ]; then
		cli_tmp=$(mktempd)
		(cd "$ROOT" && GOOS=darwin GOARCH=amd64 CGO_ENABLED=0 go build -trimpath -ldflags="-s -w $cli_identity_ldflags" -o "$cli_tmp/amd64" ./cmd/tempora)
		(cd "$ROOT" && GOOS=darwin GOARCH=arm64 CGO_ENABLED=0 go build -trimpath -ldflags="-s -w $cli_identity_ldflags" -o "$cli_tmp/arm64" ./cmd/tempora)
		lipo -create "$cli_tmp/amd64" "$cli_tmp/arm64" -output "$cli_out"
		rm -rf "$cli_tmp"
	else
		(cd "$ROOT" && GOOS="$os" GOARCH="$arch" CGO_ENABLED=0 go build -trimpath -ldflags="-s -w $cli_identity_ldflags" -o "$cli_out" ./cmd/tempora)
	fi
}

stamp_windows_executable() {
	local target="$1"
	local description="$2"
	local internal_name="$3"
	local original_filename="$4"
	local _stamp_ok=false
	for _retry in 1 2 3 4 5; do
		if "$windows_resource_tool" \
			-exe "$target" \
			-icon "$ROOT/desktop/build/windows/icon.ico" \
			-version "$numver" \
			-description "$description" \
			-internal-name "$internal_name" \
			-original-filename "$original_filename"; then
			_stamp_ok=true
			break
		fi
		echo "resource stamp denied (attempt $_retry), retrying in 3s" >&2
		sleep 3
	done
	$_stamp_ok || return 1
}

# Stamp the Windows version resource from the tag. goversioninfo demands a
# strictly numeric X.X.X, so strip the leading "v" AND any prerelease suffix (a
# `-rc1` tag would otherwise abort the resource stamping). The full tag still
# rides in ldflags for the in-app version.
numver="${VERSION#v}"; numver="${numver%%-*}"

# Regenerate the desktop host contract and fail on drift: the packaged shell
# embeds desktopContract.json, so a stale frontend/src/generated would ship a
# shell/service protocol mismatch. CI's desktop-prepare job runs the same check.
# Build to a stable path instead of `go run`: MSYS/Defender hosts intermittently
# deny the unlink of go run's temp binary and abort the whole build.
echo "==> desktop host contract drift check"
contract_tool="$ROOT/desktop/build/bin/tempora-contract-tool.exe"
mkdir -p "$(dirname "$contract_tool")"
go build -trimpath -o "$contract_tool" .
"$contract_tool" -emit-contract frontend/src/generated || {
	# Defender/MSYS intermittently deny exec of a freshly written exe; retry.
	emit_ok=false
	for _retry in 1 2 3 4 5; do
		echo "contract tool exec denied (attempt $_retry), retrying in 3s" >&2
		sleep 3
		if "$contract_tool" -emit-contract frontend/src/generated; then emit_ok=true; break; fi
	done
	$emit_ok || exit 1
}
if ! git_in_root diff --exit-code -- desktop/frontend/src/generated >/dev/null; then
	echo "desktop contract is stale - run 'cd desktop && go run . -emit-contract frontend/src/generated' and commit" >&2
	git_in_root diff --stat -- desktop/frontend/src/generated >&2
	exit 1
fi

# The packaging script drives the frontend (build:electron) and shell builds
# through pnpm; make sure the workspace dependencies (Electron, the packager)
# are installed first. A warm store makes this a no-op.
if [ ! -d "$ROOT/desktop/node_modules/@electron/packager" ] || [ ! -d "$ROOT/desktop/electron/node_modules/electron" ]; then
	echo "==> pnpm install desktop workspace"
	pnpm --dir "$ROOT/desktop" install --frozen-lockfile
fi

# Service ldflags carry version + channel; the shell reads the same identity
# from resources/build.json written by package.mjs. macOS Developer ID builds
# enable the in-app self-update path.
service_ldflags="-X main.version=$VERSION -X main.channel=$CHANNEL $product_docs_ldflags"
[ "$os" = "darwin" ] && [ "${HAS_APPLE_CERT:-}" = "true" ] && service_ldflags="$service_ldflags -X main.macSelfUpdate=true"

# build_service compiles the Go desktop service (tempora-desktop). It stays
# the active version entry the thin launcher starts: without --host-rpc it
# bootstraps the Electron shell from app/ and exits; the shell then spawns it
# with --host-rpc as the service (see docs/DESKTOP_SHELL_MIGRATION.md phase E).
build_service() {
	echo "==> go build Tempora desktop service"
	mkdir -p "$(dirname "$service_out")"
	if [ "$arch" = universal ]; then
		service_tmp=$(mktempd)
		GOOS=darwin GOARCH=amd64 go build -trimpath -ldflags="-s -w $service_ldflags" -o "$service_tmp/amd64" .
		GOOS=darwin GOARCH=arm64 go build -trimpath -ldflags="-s -w $service_ldflags" -o "$service_tmp/arm64" .
		lipo -create "$service_tmp/amd64" "$service_tmp/arm64" -output "$service_out"
		rm -rf "$service_tmp"
	else
		GOOS="$os" GOARCH="$arch" go build -trimpath -ldflags="-s -w $service_ldflags" -o "$service_out" .
	fi
}

# package_shell runs @electron/packager via the packaging script and leaves the
# bundle at desktop/build/electron/<os>-<arch>/ (Tempora.app on macOS, app/
# elsewhere). It also builds the frontend (build:electron) with the channel
# threaded through TEMPORA_CHANNEL.
package_shell() {
	echo "==> package Electron shell ($PLATFORM)"
	TEMPORA_COMMIT="$GIT_COMMIT" TEMPORA_BUILD_TIME="$BUILD_TIME_UTC" \
		node "$ROOT/desktop/packaging/package.mjs" "$PLATFORM" "$VERSION" "$CHANNEL"
}

mkdir -p "$ROOT/dist"

case "$os" in
darwin)
	service_out="$ROOT/desktop/build/bin/$BINNAME"
	build_service
	cli_out="$ROOT/desktop/build/bin/$CLINAME"
	build_cli
	package_shell

	staging=$(mktempd)
	app="$staging/${APPNAME}.app"
	cp -R "build/electron/${os}-${arch}/${APPNAME}.app" "$app"
	# The bundle's main executable is Electron. Keep one Go service payload under
	# Resources and a relative compatibility symlink in MacOS for older launchers.
	bundle_executable=$(/usr/libexec/PlistBuddy -c "Print :CFBundleExecutable" "$app/Contents/Info.plist")
	[ "$bundle_executable" = "$APPNAME" ] || { echo "macOS bundle executable is $bundle_executable, want $APPNAME" >&2; exit 1; }
	mkdir -p "$app/Contents/Resources/service"
	cp "$service_out" "$app/Contents/Resources/service/$BINNAME"
	rm -f "$app/Contents/MacOS/$BINNAME"
	ln -s "../Resources/service/$BINNAME" "$app/Contents/MacOS/$BINNAME"
	[ "$(readlink "$app/Contents/MacOS/$BINNAME")" = "../Resources/service/$BINNAME" ] || { echo "macOS service compatibility link is invalid" >&2; exit 1; }
	[ -x "$app/Contents/MacOS/$BINNAME" ] || { echo "macOS service compatibility link is broken" >&2; exit 1; }
	# Contents/MacOS already holds the Electron executable "Tempora"; on
	# case-insensitive APFS a "tempora" sibling would overwrite it, so the
	# CLI sidecar ships next to the service copy the shell actually launches
	# (desktopCLIBinaryPath resolves it beside the running service).
	cp "$cli_out" "$app/Contents/Resources/service/$CLINAME"
	if [ -e "$app/Contents/MacOS/$GUARDNAME" ]; then
		echo "macOS bundle must not include $GUARDNAME" >&2
		exit 1
	fi
	darwin_icon="$ROOT/desktop/build/darwin/icon.icns"
	bundle_icon=$(/usr/libexec/PlistBuddy -c "Print :CFBundleIconFile" "$app/Contents/Info.plist" 2>/dev/null || true)
	case "$bundle_icon" in
	*.icns) ;;
	*) bundle_icon="$bundle_icon.icns" ;;
	esac
	[ -s "$app/Contents/Resources/$bundle_icon" ] || { echo "macOS bundle icon is missing: $bundle_icon" >&2; exit 1; }

	# Two signing paths, selected by HAS_APPLE_CERT (set by release-desktop.yml when
	# the APPLE_* secrets are present). With a real Developer ID cert + notarization
	# key we sign with a hardened runtime, notarize, and staple — a downloaded build
	# then opens with no Gatekeeper prompt. Without it we ad-hoc sign as before (still
	# un-notarized; users clear the quarantine attribute per desktop/README.md). The
	# fallback keeps fork/local builds working with no secrets configured.
	if [ "${HAS_APPLE_CERT:-}" = "true" ]; then
		identity="$(security find-identity -v -p codesigning | awk -F'"' '/Developer ID Application/{print $2; exit}')"
		[ -n "$identity" ] || { echo "HAS_APPLE_CERT=true but no 'Developer ID Application' identity found in the keychain" >&2; exit 1; }
		echo "==> codesign (Developer ID): $identity"
		node "$ROOT/desktop/packaging/sign-macos.mjs" "$app" "$identity"
		# notarytool wants an archive, not a bare bundle: zip the .app, submit, wait,
		# then staple the ticket back onto the bundle so it verifies offline.
		ditto -c -k --keepParent "$app" "$staging/notarize.zip"
		notary_diagnostics="${APPLE_NOTARIZATION_LOG_DIR:-$ROOT/desktop/build/notarization}"
		node "$ROOT/scripts/notarize-desktop.mjs" "$staging/notarize.zip" "$app" app "$notary_diagnostics"
	else
		# Ad-hoc cuts the "is damaged" error somewhat but is NOT notarized; users may
		# still need `xattr -dr com.apple.quarantine` (see desktop/README.md).
		node "$ROOT/desktop/packaging/sign-macos.mjs" "$app" -
	fi

	# Updaters receive a native-architecture app. Universal remains a human
	# download only, so a fat bundle is never copied under architecture names.
	if [ "$arch" != universal ]; then
		ditto -c -k --zlibCompressionLevel 9 --keepParent "$app" "$ROOT/dist/${APPNAME}-darwin-${arch}.zip"
	fi
	candidate_dir="$ROOT/desktop/build/candidate/darwin-${arch}"
	rm -rf "$candidate_dir"
	mkdir -p "$candidate_dir"
	cp -R "$app" "$candidate_dir/${APPNAME}.app"
	node "$ROOT/desktop/packaging/verify.mjs" "$candidate_dir/${APPNAME}.app" --kind darwin-app-dir
	if [ "${DESKTOP_BUILD_SKIP_DMG:-0}" = "1" ]; then
		echo "==> skip DMG packaging (DESKTOP_BUILD_SKIP_DMG=1)"
	else
		# A drag-to-Applications .dmg for first-time human download. cmd/sign uses an
		# exact filename table, so the .zip stays the updater channel and the .dmg is
		# release-page only. create-dmg can exit nonzero
		# while still writing the image, so gate on the file existing, not the exit code.
		dmgsrc=$(mktempd)
		cp -R "$app" "$dmgsrc/${APPNAME}.app"
		dmg="$ROOT/dist/${APPNAME}-darwin-${arch}.dmg"
		create-dmg \
			--volname "$APPNAME" \
			--window-size 540 380 \
			--icon-size 110 \
			--icon "${APPNAME}.app" 150 190 \
			--app-drop-link 390 190 \
			--no-internet-enable \
			"$dmg" "$dmgsrc" || true
		[ -f "$dmg" ] || { echo "create-dmg did not produce $dmg" >&2; exit 1; }
		# The .dmg is a separately-downloaded artifact, so sign + notarize + staple the
		# disk image itself too — the stapled .app inside isn't enough for the image.
		if [ "${HAS_APPLE_CERT:-}" = "true" ]; then
			codesign --force --timestamp -s "$identity" "$dmg"
			node "$ROOT/scripts/notarize-desktop.mjs" "$dmg" "$dmg" dmg "$notary_diagnostics"
		fi
		rm -rf "$dmgsrc"
	fi
	rm -rf "$staging"
	;;
windows)
	windows_resource_tool_dir=$(mktempd)
	windows_host_include="$ROOT/desktop/build/windows/installer/tempora_host.nsh"
	case "$(uname -s 2>/dev/null || printf '%s' unknown)" in
		Darwin* | Linux* | FreeBSD*)
			printf '%s\n' '!define TEMPORA_UNINST_FINALIZE '\''/bin/cp -f "%1" "tempora-uninstall.exe"'\''' >"$windows_host_include"
			;;
		*)
			printf '%s\n' '!define TEMPORA_UNINST_FINALIZE '\''cmd.exe /C for /l %i in (1,1,10) do @((if not exist "tempora-uninstall.exe" ((ping -n 2 127.0.0.1 >NUL) & (copy /Y "%1" "tempora-uninstall.exe" >NUL))))'\''' >"$windows_host_include"
			;;
	esac
	windows_resource_tool="$windows_resource_tool_dir/tempora-windows-resource.exe"
	echo "==> build Windows resource stamper"
	go build -trimpath -o "$windows_resource_tool" ./cmd/windows-resource

	installer_dir="$ROOT/desktop/build/windows/installer"
	guard_out="$installer_dir/$GUARDNAME.exe"
	build_guard
	stamp_windows_executable "$guard_out" "Tempora Legacy Migrator" "$GUARDNAME" "$GUARDNAME.exe"
	launcher_out="$installer_dir/$LAUNCHERNAME.exe"
	echo "==> go build Windows GUI thin launcher"
	(cd "$ROOT" && GOOS=windows GOARCH="$arch" CGO_ENABLED=0 go build -trimpath \
		-ldflags="-s -w -H windowsgui -X main.version=$VERSION" -o "$launcher_out" ./cmd/tempora-launcher)
	stamp_windows_executable "$launcher_out" "Tempora Launcher" "$LAUNCHERNAME" "$LAUNCHERNAME.exe"
	UPDATE_HELPER="tempora-update-helper.exe"
	echo "==> go build Windows update helper"
	GOOS=windows GOARCH="$arch" go build -trimpath -ldflags="-s -w" \
		-o "$installer_dir/$UPDATE_HELPER" ./cmd/update-helper
	stamp_windows_executable "$installer_dir/$UPDATE_HELPER" "Tempora Update Helper" "tempora-update-helper" "$UPDATE_HELPER"
	cli_out="$installer_dir/$WINDOWS_CLINAME.exe"
	build_cli
	stamp_windows_executable "$cli_out" "Tempora CLI" "$WINDOWS_CLINAME" "$WINDOWS_CLINAME.exe"
	cli_entry_out="$ROOT/desktop/build/bin/$WINDOWS_CLI_ENTRY"
	echo "==> go build Windows CLI entry"
	(cd "$ROOT" && GOOS=windows GOARCH="$arch" CGO_ENABLED=0 go build -trimpath \
		-ldflags="-s -w" -o "$cli_entry_out" ./cmd/tempora-cli-launcher)
	stamp_windows_executable "$cli_entry_out" "Tempora CLI Launcher" "tempora-cli-launcher" "$WINDOWS_CLI_ENTRY"

	service_out="$ROOT/desktop/build/bin/$BINNAME.exe"
	build_service
	stamp_windows_executable "$service_out" "Tempora Desktop" "$BINNAME" "$BINNAME.exe"
	# NSIS File sources live next to project.nsi; the service joins the flat
	# payload files there (package-windows-desktop.sh overwrites them with the
	# signed copies before the second pass).
	cp "$service_out" "$installer_dir/$BINNAME.exe"

	package_shell
	mkdir -p "build/electron/${os}-${arch}/app/resources/bin"
	cp "$cli_entry_out" "build/electron/${os}-${arch}/app/resources/bin/$WINDOWS_CLI_ENTRY"
	# The Electron bundle becomes versions/v<ver>/app/ at install time; NSIS
	# consumes it as the "app" directory next to project.nsi.
	rm -rf "$installer_dir/app"
	cp -R "build/electron/${os}-${arch}/app" "$installer_dir/app"

	# First NSIS pass: regenerate this release's uninstaller. A stale preserved
	# uninstaller must never enter the signing payload.
	rm -f "$installer_dir/tempora-uninstall.exe"
	find "$ROOT/desktop/build/bin" -maxdepth 1 -type f -name '*installer*.exe' -delete
	arch_binary_define="ARG_TEMPORA_AMD64_BINARY"
	[ "$arch" = arm64 ] && arch_binary_define="ARG_TEMPORA_ARM64_BINARY"
	(
		cd "$installer_dir"
		makensis "-D${arch_binary_define}=$installer_dir/$BINNAME.exe" project.nsi
	)
	[ -s "$installer_dir/tempora-uninstall.exe" ] || {
		# Defender/MSYS intermittently deny process spawn; one makensis retry
		# is cheaper than aborting the whole build.
		echo "first NSIS pass did not produce tempora-uninstall.exe - retrying makensis" >&2
		(
			cd "$installer_dir"
			makensis "-D${arch_binary_define}=$installer_dir/$BINNAME.exe" project.nsi
		)
	}
	[ -s "$installer_dir/tempora-uninstall.exe" ] || { echo "first NSIS pass did not produce tempora-uninstall.exe after retry" >&2; exit 1; }

	# Keep one canonical payload for SignPath: the flat Go executables plus the
	# Electron app/ tree. The release workflow signs these files, then calls
	# package-windows-desktop.sh again so both the portable archive and the
	# files embedded by NSIS carry Authenticode.
	payload_dir="$ROOT/desktop/build/windows/signing-payload"
	rm -rf -- "$payload_dir"
	mkdir -p "$payload_dir"
	for name in "$BINNAME.exe" "$GUARDNAME.exe" "$LAUNCHERNAME.exe" "$UPDATE_HELPER" "$WINDOWS_CLINAME.exe" "tempora-uninstall.exe"; do
		cp "$installer_dir/$name" "$payload_dir/$name"
	done
	cp -R "$installer_dir/app" "$payload_dir/app"
	# signing-files.txt enumerates every PE file (flat payload + app tree); the
	# SignPath artifact configuration and the Authenticode verifier consume it.
	node "$ROOT/desktop/packaging/signing-files.mjs" "$payload_dir"
	VERSION="$VERSION" "$ROOT/scripts/package-windows-desktop.sh" "$arch" "$payload_dir"
	node "$ROOT/desktop/packaging/verify.mjs" "$ROOT/dist/${APPNAME}-windows-${arch}.zip" --kind windows-portable-zip
	;;
linux)
	service_out="$ROOT/desktop/build/bin/$BINNAME"
	build_service
	# Linux still ships a one-shot migrator named tempora-guard in the portable
	# tarball so 1.18–1.19.1 updaters can hand off.
	guard_out="$ROOT/desktop/build/bin/$GUARDNAME"
	build_guard
	launcher_out="$ROOT/desktop/build/bin/$LAUNCHERNAME"
	echo "==> go build Linux thin launcher"
	(cd "$ROOT" && GOOS=linux GOARCH="$arch" CGO_ENABLED=0 go build -trimpath \
		-ldflags="-s -w -X main.version=$VERSION" -o "$launcher_out" ./cmd/tempora-launcher)
	cli_out="$ROOT/desktop/build/bin/$CLINAME"
	build_cli
	package_shell
	# Stage the Electron tree next to the Go binaries so the tarball and the
	# nfpm config share one source root (build/bin).
	rm -rf "build/bin/app"
	cp -R "build/electron/${os}-${arch}/app" "build/bin/app"

	for desktop_contract in \
		'Exec=tempora-launcher' \
		'Icon=tempora-desktop' \
		'StartupWMClass=Tempora'; do
		grep -F -x -q "$desktop_contract" build/linux/tempora.desktop || { echo "Linux desktop entry missing: $desktop_contract" >&2; exit 1; }
	done
	# Portable Linux tarball: service + thin launcher + one-shot migrator
	# (compat name tempora-guard) + CLI + the Electron app/ tree. After the
	# migrator runs, Guard self-deletes.
	tar -cf - -C build/bin "$BINNAME" "$LAUNCHERNAME" "$GUARDNAME" "$CLINAME" app | \
		gzip -9 >"$ROOT/dist/${APPNAME}-linux-${arch}.tar.gz"
	# Build the privileged update helper shipped inside the .deb. Portable tarball
	# installs do not need it; only the dpkg package installs helper + Polkit policy.
	echo "==> go build tempora-update-helper"
	GOOS=linux GOARCH="$arch" CGO_ENABLED=0 go build -trimpath -ldflags="-s -w -X main.version=$VERSION" \
		-o "build/bin/tempora-update-helper" ./cmd/update-helper
	# .deb for Debian/Ubuntu. Portable updater still uses the tarball under
	# platforms[]; .deb is published under native_packages. Debian versions use
	# "~" for prereleases so 1.18.0~rc.1 < 1.18.0 (policy version ordering).
	# Extra "-" inside the prerelease label becomes "." (Debian policy).
	ver_body="${VERSION#v}"
	if [[ "$ver_body" == *-* ]]; then
		deb_base="${ver_body%%-*}"
		deb_pre="${ver_body#*-}"
		deb_pre="${deb_pre//-/.}"
		deb_version="${deb_base}~${deb_pre}"
	else
		deb_version="$ver_body"
	fi
	DEB_VERSION="$deb_version" DEB_ARCH="$arch" \
		nfpm package --config build/linux/nfpm.yaml --packager deb \
		--target "$ROOT/dist/${APPNAME}-linux-${arch}.deb"
	# Contract smoke: helper, policy, package identity, Electron tree, sandbox.
	deb_path="$ROOT/dist/${APPNAME}-linux-${arch}.deb"
	dpkg-deb --field "$deb_path" Package | grep -x 'tempora-desktop' >/dev/null
	dpkg-deb --field "$deb_path" Version | grep -x "$deb_version" >/dev/null
	dpkg-deb --field "$deb_path" Depends | grep -F 'pkexec' >/dev/null
	dpkg-deb --contents "$deb_path" | grep -E 'usr/lib/tempora/tempora-update-helper' >/dev/null
	dpkg-deb --contents "$deb_path" | grep -E 'usr/share/polkit-1/actions/io.tempora.desktop.update.policy' >/dev/null
	dpkg-deb --contents "$deb_path" | grep -E "usr/lib/tempora/app/${APPNAME}" >/dev/null
	dpkg-deb --contents "$deb_path" | grep -E 'usr/lib/tempora/app/chrome-sandbox' >/dev/null
	node "$ROOT/desktop/packaging/verify.mjs" "$ROOT/dist/${APPNAME}-linux-${arch}.tar.gz" --kind linux-tar
	node "$ROOT/desktop/packaging/verify.mjs" "$deb_path" --kind linux-deb
	;;
*)
	echo "unsupported os: $os" >&2
	exit 1
	;;
esac

case "$os" in
# The staging directory is intentionally removed after the signed app is
# copied into build/candidate.  Reports must inspect that published candidate,
# otherwise every successful macOS package build fails after artifact
# verification with ENOENT.
darwin) report_bundle="$ROOT/desktop/build/candidate/darwin-${arch}/${APPNAME}.app" ;;
windows) report_bundle="$ROOT/desktop/build/windows/signing-payload" ;;
linux) report_bundle="$ROOT/desktop/build/bin" ;;
esac
TEMPORA_COMMIT="$SOURCE_SHA" TEMPORA_BUILD_SECONDS="$((SECONDS - build_started_seconds))" \
	node "$ROOT/desktop/packaging/size-report.mjs" \
		--platform "$PLATFORM" \
		--version "$VERSION" \
		--bundle "$report_bundle" \
		--dist "$ROOT/dist" \
		--output "$ROOT/desktop/build/reports/${os}-${arch}"

echo "==> packaged into dist/:"
ls -la "$ROOT/dist"
