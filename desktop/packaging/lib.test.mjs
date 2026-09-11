import assert from "node:assert/strict";
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import {
  checkMembers,
  inferArtifactKind,
  listZipEntries,
  nsisProjectDefines,
  numericVersion,
  packagerOptions,
  parseSigningFileList,
  parseTarget,
  PRODUCT,
  readProductIdentity,
  requiredMembers,
  runBuildScript,
  sanitizeShellPackageJson,
  shellIgnore,
  signingFileList,
  versionTag,
  WINDOWS_FLAT_PAYLOAD,
} from "./lib.mjs";

const desktop = dirname(dirname(fileURLToPath(import.meta.url)));
const read = (path) => readFileSync(join(desktop, path), "utf8");
const identity = { projectName: "tempora-desktop", companyName: "Tempora", productName: "Tempora", copyright: "Copyright © 2026 Tempora Contributors" };

test("build scripts preserve paths, arguments and environment without shell encoding", (t) => {
  const directory = mkdtempSync(join(tmpdir(), "tempora build & 中文 "));
  t.after(() => rmSync(directory, { recursive: true, force: true }));
  mkdirSync(join(directory, "scripts"));
  const output = join(directory, "result.json");
  writeFileSync(join(directory, "scripts", "fixture.mjs"), `
    import { writeFileSync } from "node:fs";
    writeFileSync(process.env.TEMPORA_BUILD_TEST_OUTPUT, JSON.stringify({
      args: process.argv.slice(2), cwd: process.cwd(), channel: process.env.TEMPORA_CHANNEL,
    }));
  `);
  const args = ["", "a b", 'a"b', "C:\\build path\\", 'C:\\path\\"quoted"\\', "a&b|c<d>e^f%PATH%!x!", "$(echo unwanted)", "中文"];
  runBuildScript(directory, "fixture.mjs", args, { TEMPORA_CHANNEL: "preview", TEMPORA_BUILD_TEST_OUTPUT: output });
  const actual = JSON.parse(readFileSync(output, "utf8"));
  assert.deepEqual(actual.args, args);
  assert.equal(actual.channel, "preview");
  assert.equal(readFileSync(join(actual.cwd, "result.json"), "utf8"), readFileSync(output, "utf8"));
  writeFileSync(join(directory, "scripts", "failure.mjs"), "process.exit(17);\n");
  assert.throws(() => runBuildScript(directory, "failure.mjs"), /failure\.mjs exited with 17/);
});

test("targets map Go platform names onto packager platform and arch", () => {
  assert.deepEqual(parseTarget("darwin/universal"), { os: "darwin", arch: "universal", packagerPlatform: "darwin", packagerArch: "universal", spec: "darwin/universal", key: "darwin-universal" });
  assert.equal(parseTarget("windows/amd64").packagerArch, "x64");
  assert.equal(parseTarget("windows/arm64").packagerPlatform, "win32");
  assert.equal(parseTarget("linux/amd64").key, "linux-amd64");
  assert.throws(() => parseTarget("windows/universal"), /unsupported target/);
  assert.throws(() => parseTarget("darwin"), /unsupported target/);
});

test("versions keep the full tag for identity and strip it for OS resources", () => {
  assert.equal(numericVersion("v1.2.3"), "1.2.3");
  assert.equal(numericVersion("v1.2.3-rc.1"), "1.2.3");
  assert.equal(numericVersion("v0.0.0-local"), "0.0.0");
  assert.equal(versionTag("v1.20.0-preview.42"), "v1.20.0-preview.42");
  for (const bad of ["1.2.3", "v1.2", "v01.2.3", "v1.2.3+meta", ""]) assert.throws(() => numericVersion(bad), /version must look like/);
});

test("the product identity is a frozen constant and keeps the Wails-era bundle id", () => {
  const product = readProductIdentity();
  assert.equal(product.productName, "Tempora");
  assert.equal(product.projectName, "tempora-desktop");
  assert.equal(product.companyName, "Tempora");
  assert.match(product.copyright, /Tempora Contributors/);
  assert.equal(PRODUCT.bundleId, "com.wails.tempora-desktop");
});

test("only the shell bundle and its package.json enter the asar", () => {
  for (const kept of ["", "/package.json", "/dist", "/dist/main.cjs", "/dist/preload.cjs", "/dist/desktopContract.json", "/dist/guestPreload.cjs"]) {
    assert.equal(shellIgnore(kept), false, kept);
  }
  for (const dropped of ["/dist/main.cjs.map", "/src", "/src/main/index.ts", "/node_modules", "/node_modules/electron", "/scripts/build.mjs", "/tsconfig.json", "/README.md", "/artifacts"]) {
    assert.equal(shellIgnore(dropped), true, dropped);
  }
});

test("package.json uses the numeric native version; build.json owns the full release identity", () => {
  const pkg = sanitizeShellPackageJson(
    { name: "tempora-desktop-shell", private: true, version: "0.0.0", type: "module", main: "dist/main.cjs", description: "shell", scripts: { build: "x" }, devDependencies: { electron: "44.2.0" }, engines: { node: ">=24" } },
    { version: "v1.2.3-rc.1", productName: "Tempora" },
  );
  assert.deepEqual(pkg, { name: "tempora-desktop-shell", description: "shell", main: "dist/main.cjs", type: "module", productName: "Tempora", version: "1.2.3" });
});

test("packager options pin the product identity and layout for every target", () => {
  const common = { version: "v1.2.3-rc.1", identity, root: "/repo/desktop", electronVersion: "44.2.0", extraResources: ["/tmp/app", "/tmp/icons", "/tmp/build.json"] };
  const mac = packagerOptions({ ...common, target: parseTarget("darwin/universal"), icon: "/repo/desktop/build/darwin/icon.icns" });
  assert.equal(mac.dir, join("/repo/desktop", "electron"));
  assert.equal(mac.name, "Tempora");
  assert.equal(mac.executableName, "Tempora");
  assert.equal(mac.platform, "darwin");
  assert.equal(mac.arch, "universal");
  assert.equal(mac.appBundleId, "com.wails.tempora-desktop");
  assert.equal(mac.appVersion, "1.2.3");
  assert.equal(mac.buildVersion, "1.2.3");
  assert.equal(mac.appCopyright, identity.copyright);
  assert.equal(mac.asar, true);
  assert.equal(mac.prune, true);
  assert.equal(mac.overwrite, true);
  assert.equal(mac.icon, "/repo/desktop/build/darwin/icon.icns");
  assert.deepEqual(mac.extraResource, common.extraResources);
  assert.equal(mac.ignore, shellIgnore);
  assert.equal(mac.win32metadata, undefined);

  const win = packagerOptions({ ...common, target: parseTarget("windows/arm64"), icon: "/repo/desktop/build/windows/icon.ico" });
  assert.equal(win.platform, "win32");
  assert.equal(win.arch, "arm64");
  assert.deepEqual(win.win32metadata, { CompanyName: "Tempora", FileDescription: "Tempora", ProductName: "Tempora", InternalName: "Tempora", OriginalFilename: "Tempora.exe" });

  const linux = packagerOptions({ ...common, target: parseTarget("linux/amd64") });
  assert.equal(linux.platform, "linux");
  assert.equal(linux.arch, "x64");
  assert.equal("icon" in linux, false);
});

test("NSIS project defines replace the Wails-generated INFO_* values", () => {
  const defines = nsisProjectDefines(identity, "v1.2.3-rc.1");
  assert.ok(defines.startsWith("﻿"), "UTF-8 BOM for makensis");
  assert.match(defines, /!define INFO_PROJECTNAME "tempora-desktop"\r\n/);
  assert.match(defines, /!define INFO_COMPANYNAME "Tempora"\r\n/);
  assert.match(defines, /!define INFO_PRODUCTNAME "Tempora"\r\n/);
  assert.match(defines, /!define INFO_PRODUCTVERSION "1\.2\.3"\r\n/);
  assert.match(defines, /!define INFO_COPYRIGHT "Copyright © 2026 Tempora Contributors"\r\n/);
  assert.match(defines, /!define TEMPORA_VERSION_TAG "v1\.2\.3-rc\.1"\r\n/);
});

test("signing files are every PE file, sorted, deduplicated and slash-normalised", () => {
  const files = signingFileList([
    "tempora-desktop.exe",
    "app\\Tempora.exe",
    "app/ffmpeg.dll",
    "app/resources/app.asar",
    "app/LICENSE",
    "app/vk_swiftshader_icd.json",
    "app/d3dcompiler_47.DLL",
    "./tempora-uninstall.exe",
    "tempora-desktop.exe",
    "tempora-payload.json",
  ]);
  assert.deepEqual(files, ["app/Tempora.exe", "app/d3dcompiler_47.DLL", "app/ffmpeg.dll", "tempora-desktop.exe", "tempora-uninstall.exe"]);
  assert.deepEqual(parseSigningFileList("# comment\r\napp/Tempora.exe\n\n tempora-cli.exe \n"), ["app/Tempora.exe", "tempora-cli.exe"]);
  assert.deepEqual([...WINDOWS_FLAT_PAYLOAD], ["tempora-desktop.exe", "tempora-guard.exe", "tempora-launcher.exe", "tempora-update-helper.exe", "tempora-cli.exe", "tempora-uninstall.exe"]);
});

test("required members cover every artifact and the checks report gaps", () => {
  const macEntries = requiredMembers("darwin-zip").map(String);
  assert.deepEqual(checkMembers([...macEntries, "Tempora.app/", "Tempora.app/Contents/"], "darwin-zip"), { missing: [], forbidden: [] });
  assert.deepEqual(checkMembers(macEntries.slice(1), "darwin-zip").missing, [macEntries[0]]);
  assert.deepEqual(checkMembers([...macEntries, "Tempora.app/Contents/MacOS/tempora-guard"], "darwin-zip").forbidden, ["Tempora.app/Contents/MacOS/tempora-guard"]);
  assert.ok(macEntries.includes("Tempora.app/Contents/MacOS/tempora-desktop"));
  assert.ok(macEntries.includes("Tempora.app/Contents/Resources/service/tempora"));
  assert.ok(macEntries.includes("Tempora.app/Contents/Resources/service/tempora-desktop"));
  assert.deepEqual(checkMembers(requiredMembers("darwin-app-dir").map(String), "darwin-app-dir").missing, []);

  const portable = [
    "Tempora.exe", "tempora-launcher.exe", "tempora-cli.exe", "current.json",
    "versions/v1.2.3-rc.1/tempora-desktop.exe", "versions/v1.2.3-rc.1/tempora-update-helper.exe", "versions/v1.2.3-rc.1/tempora-cli.exe",
    "versions/v1.2.3-rc.1/app/Tempora.exe", "versions/v1.2.3-rc.1/app/resources/app.asar", "versions/v1.2.3-rc.1/app/resources/app/index.html", "versions/v1.2.3-rc.1/app/resources/build.json",
  ];
  assert.deepEqual(checkMembers(portable, "windows-portable-zip"), { missing: [], forbidden: [] });
  assert.deepEqual(checkMembers(portable.filter((name) => !name.endsWith("app/Tempora.exe")), "windows-portable-zip").missing, [String(/^versions\/v[^/]+\/app\/Tempora\.exe$/)]);
  assert.deepEqual(checkMembers([...portable, "tempora-guard.exe"], "windows-portable-zip").forbidden, ["tempora-guard.exe"]);

  const winApp = ["Tempora.exe", "ffmpeg.dll", "libEGL.dll", "libGLESv2.dll", "resources.pak", "icudtl.dat", "locales\\en-US.pak", "resources\\app.asar", "resources\\app\\index.html", "resources\\build.json", "resources\\icons\\appicon.png"];
  assert.deepEqual(checkMembers(winApp, "windows-app-dir"), { missing: [], forbidden: [] });

  const tar = requiredMembers("linux-tar").map(String);
  assert.deepEqual(checkMembers(tar, "linux-tar"), { missing: [], forbidden: [] });
  assert.ok(tar.includes("app/chrome-sandbox"));
  const deb = requiredMembers("linux-deb").map((name) => `./${name}`);
  assert.deepEqual(checkMembers(deb, "linux-deb"), { missing: [], forbidden: [] });
  assert.deepEqual(checkMembers([...deb, "./usr/bin/tempora-guard"], "linux-deb").forbidden, ["usr/bin/tempora-guard"]);
  assert.deepEqual(checkMembers(requiredMembers("linux-app-dir").map(String), "linux-app-dir").missing, []);
  assert.throws(() => checkMembers([], "nope"), /unknown artifact kind/);
});

test("artifact kinds are inferred from release names and bundle shapes", () => {
  assert.equal(inferArtifactKind("/dist/Tempora-darwin-arm64.zip", false), "darwin-zip");
  assert.equal(inferArtifactKind("/dist/Tempora-windows-amd64.zip", false), "windows-portable-zip");
  assert.equal(inferArtifactKind("/dist/Tempora-linux-amd64.tar.gz", false), "linux-tar");
  assert.equal(inferArtifactKind("/dist/Tempora-linux-amd64.deb", false), "linux-deb");
  assert.equal(inferArtifactKind("/x/Tempora.app", true, ["Contents"]), "darwin-app-dir");
  assert.equal(inferArtifactKind("/x/app", true, ["Tempora.exe", "resources"]), "windows-app-dir");
  assert.equal(inferArtifactKind("/x/app", true, ["Tempora", "chrome-sandbox"]), "linux-app-dir");
  assert.throws(() => inferArtifactKind("/dist/Tempora-darwin-universal.dmg", false), /cannot infer/);
});

function storedZip(entries) {
  const locals = [];
  const centrals = [];
  let offset = 0;
  for (const [name, content] of entries) {
    const nameBytes = Buffer.from(name, "utf8");
    const data = Buffer.from(content, "utf8");
    const local = Buffer.alloc(30);
    local.writeUInt32LE(0x04034b50, 0);
    local.writeUInt16LE(nameBytes.length, 26);
    const central = Buffer.alloc(46);
    central.writeUInt32LE(0x02014b50, 0);
    central.writeUInt32LE(data.length, 20);
    central.writeUInt32LE(data.length, 24);
    central.writeUInt16LE(nameBytes.length, 28);
    central.writeUInt32LE(offset, 42);
    locals.push(local, nameBytes, data);
    centrals.push(central, nameBytes);
    offset += local.length + nameBytes.length + data.length;
  }
  const directory = Buffer.concat(centrals);
  const end = Buffer.alloc(22);
  end.writeUInt32LE(0x06054b50, 0);
  end.writeUInt16LE(entries.length, 8);
  end.writeUInt16LE(entries.length, 10);
  end.writeUInt32LE(directory.length, 12);
  end.writeUInt32LE(offset, 16);
  return Buffer.concat([...locals, directory, end]);
}

test("zip listing reads the central directory without extracting", () => {
  const dir = mkdtempSync(join(tmpdir(), "tempora-ziptest-"));
  try {
    const file = join(dir, "Tempora-darwin-arm64.zip");
    writeFileSync(file, storedZip([["Tempora.app/", ""], ["Tempora.app/Contents/MacOS/Tempora", "mach-o"], ["Tempora.app/Contents/Resources/app/index.html", "<html>"]]));
    assert.deepEqual(listZipEntries(file), ["Tempora.app/", "Tempora.app/Contents/MacOS/Tempora", "Tempora.app/Contents/Resources/app/index.html"]);
    writeFileSync(join(dir, "not.zip"), "plain text");
    assert.throws(() => listZipEntries(join(dir, "not.zip")), /not a zip archive/);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test("the Linux package inputs install the Electron tree beside the update helper", () => {
  const nfpm = read("build/linux/nfpm.yaml");
  assert.match(nfpm, /src: \.\/build\/bin\/app\n\s+dst: \/usr\/lib\/tempora\/app\n\s+type: tree/);
  assert.match(nfpm, /dst: \/usr\/lib\/tempora\/tempora-update-helper/);
  assert.match(nfpm, /dst: \/usr\/share\/polkit-1\/actions\/io\.tempora\.desktop\.update\.policy/);
  assert.match(nfpm, /dst: \/usr\/bin\/tempora-launcher/);
  assert.doesNotMatch(nfpm, /dst: \/usr\/bin\/tempora-guard/);
  assert.match(nfpm, /postinstall: \.\/build\/linux\/postinstall\.sh/);
  for (const dep of ["libgtk-3-0", "libnss3", "libgbm1", "libasound2", "pkexec"]) assert.ok(nfpm.includes(`  - ${dep}`), dep);
  const postinstall = read("build/linux/postinstall.sh");
  assert.match(postinstall, /chown root:root \/usr\/lib\/tempora\/app\/chrome-sandbox/);
  assert.match(postinstall, /chmod 4755 \/usr\/lib\/tempora\/app\/chrome-sandbox/);
  const entry = read("build/linux/tempora.desktop");
  assert.match(entry, /^Exec=tempora-launcher$/m);
  assert.match(entry, /^Icon=tempora-desktop$/m);
  assert.match(entry, /^StartupWMClass=Tempora$/m);
});

test("the NSIS script installs the Electron tree with both payload modes and no WebView2", () => {
  const nsi = read("build/windows/installer/project.nsi");
  assert.ok(nsi.startsWith("﻿"), "UTF-8 BOM");
  assert.match(nsi, /!include "tempora_project\.nsh"/);
  assert.doesNotMatch(nsi, /wails_tools\.nsh/);
  assert.doesNotMatch(nsi, /webview2/i);
  assert.equal((nsi.match(/!insertmacro tempora\.files/g) ?? []).length, 2, "stage payload and normal install both extract the payload");
  assert.match(nsi, /File \/r "app"/);
  assert.match(nsi, /ARG_TEMPORA_AMD64_BINARY/);
  assert.match(nsi, /ARG_TEMPORA_ARM64_BINARY/);
  assert.match(nsi, /!define UNINST_KEY_NAME "\$\{INFO_COMPANYNAME\}\$\{INFO_PRODUCTNAME\}"/);
  assert.match(nsi, /!define PRODUCT_EXECUTABLE "\$\{INFO_PROJECTNAME\}\.exe"/);
  assert.match(nsi, /RMDir \/r "\$INSTDIR\\versions"/);
  assert.match(nsi, /File "\/oname=uninstall\.exe" "\$\{ARG_TEMPORA_SIGNED_UNINSTALLER\}"/);
});

test("the installer stamps the shortcuts it created without launching the desktop", () => {
  const nsi = read("build/windows/installer/project.nsi");
  const maintenance = nsi.indexOf('--repair-shortcuts "$SMPROGRAMS\\${INFO_PRODUCTNAME}.lnk" "$DESKTOP\\${INFO_PRODUCTNAME}.lnk"');
  assert.ok(maintenance > nsi.indexOf('CreateShortCut "$DESKTOP\\${INFO_PRODUCTNAME}.lnk"'), "maintenance follows shortcut creation");
  assert.match(nsi.slice(maintenance, maintenance + 350), /Pop \$0/);
  assert.match(nsi.slice(maintenance, maintenance + 350), /shortcut identity repair failed/);
});

test("installer unlock checks do not create or lock missing release entries", () => {
  const nsi = read("build/windows/installer/project.nsi");
  const body = nsi.slice(nsi.indexOf("Function tempora.waitForExecutableUnlock"), nsi.indexOf("FunctionEnd", nsi.indexOf("Function tempora.waitForExecutableUnlock")));
  const opens = [...body.matchAll(/FileOpen \$1 "([^"]+)" a/g)];
  assert.equal(opens.length, 6);
  for (const open of opens) {
    const preceding = body.slice(0, open.index);
    const guard = `IfFileExists "${open[1]}" 0 `;
    const at = preceding.lastIndexOf(guard);
    assert.ok(at >= 0, `missing existence guard for ${open[1]}`);
    assert.match(preceding.slice(at), /^IfFileExists [^\n]+\r?\n\s+ClearErrors\s+$/);
  }
});
