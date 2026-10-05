// What a window can do and a page cannot, behind one interface so nothing in
// the app learns which shell it is running in. Electron exposes a preload
// bridge; a browser tab has none, and answers for itself.

export type Shell = "electron" | "browser";

export interface HostInfo {
  shell: Shell;
  /** "darwin" | "windows" | "linux", or "" where the page cannot know. */
  platform: string;
  /** The window has no native title bar, so the top row of the page is one.
   *  Answered by the shell: only it knows how its window was created. */
  titleBar: boolean;
}

export interface HostPort {
  describe(): Promise<HostInfo>;
  minimiseWindow(): void;
  toggleMaximiseWindow(): void;
  isWindowMaximised(): Promise<boolean>;
  closeWindow(): void;
  openExternal(url: string): void;
  /** Where dropped files live. Empty where the shell cannot say — a browser
   *  tab never learns a path. */
  pathsForFiles(files: File[]): string[];
  /** Put text on disk where the user picks. null means this shell has no save
   *  surface at all; "" means they dismissed the dialog, which is an answer. */
  saveText(name: string, content: string): Promise<string | null>;
  saveBytes(name: string, bytes: Uint8Array): Promise<string | null>;
  /** Ask for a directory. null means this shell has no picker at all; "" means
   *  they dismissed it, the same two answers saveText gives. startIn is where
   *  to open: the shell owns the dialog, the kernel owns which workspace runs,
   *  so the page carries one to the other. */
  pickFolder(startIn: string): Promise<string | null>;
  /** Whether this shell draws the agent's browser pages inside the window. */
  drawsBrowserViews(): boolean;
  /** Draw one of the agent's pages over rect, in on-screen coordinates, and
   *  hide every other; hideBrowserView puts them all away again. */
  showBrowserView(target: string, rect: ViewRect): void;
  hideBrowserView(): void;
  controlBrowserView(target: string, action: BrowserControl): void;
  /** Load what the person typed. false when the shell refused the address. */
  navigateBrowserView(target: string, address: string): Promise<boolean>;
  /** Why a page did not load, or null once another load starts. */
  onBrowserLoadState(listener: (state: BrowserLoadState) => void): () => void;
  /** A page or a proxy asking for a login; answered with answerBrowserLogin. */
  onBrowserLogin(listener: (ask: BrowserLogin) => void): () => void;
  /** An empty username cancels the login. */
  answerBrowserLogin(id: string, username: string, password: string): void;
  /** Proceed past the certificate this page was refused for, for this run. */
  trustBrowserCertificate(target: string): Promise<boolean>;
  /** The running shell's own version and whether a newer build is published. */
  updateStatus(): Promise<UpdateStatus>;
  /** Install the newer build. Resolves once the shell has it or reports there
   *  is nothing to do; rejects when the install failed. null where there is no
   *  shell — a page in a browser has nothing to update and must not throw. */
  openUpdater(): Promise<UpdateInstall | null>;
}

/** What the version dot next to the wordmark reports. */
export interface UpdateStatus {
  /** The running version, "0.1.15" style. null where no shell can answer. */
  current: string | null;
  available: boolean;
  /** The newer version; only carries a value when available is true. */
  latest: string | null;
}

/** What an install attempt comes back as. */
export interface UpdateInstall {
  /** true once the new build is on disk; the shell restarts itself after. */
  updated: boolean;
  /** The version that was installed, when updated is true. */
  version: string | null;
}

export interface BrowserLoadFailure {
  url: string;
  /** Chromium's net error number, negative. */
  code: number;
  /** Chromium's net error name, e.g. ERR_CERT_AUTHORITY_INVALID. */
  reason: string;
  /** The certificate a certificate error was raised for. */
  certificate?: BrowserCertificate;
}

export interface BrowserCertificate {
  host: string;
  error: string;
  fingerprint: string;
  subject: string;
  issuer: string;
  /** Seconds since the epoch. */
  expiry: number;
}

export interface BrowserLoadState {
  targetId: string;
  failure: BrowserLoadFailure | null;
}

export interface BrowserLogin {
  id: string;
  targetId: string;
  url: string;
  host: string;
  port: number;
  realm: string;
  proxy: boolean;
}

export interface ViewRect {
  x: number;
  y: number;
  width: number;
  height: number;
}

export type BrowserControl = "back" | "forward" | "reload" | "stop";

// The preload bridge. Verbs only: the origin the page was loaded from and the
// credential that opens it never cross it.
interface ElectronBridge {
  shell: "electron";
  platform: string;
  titleBar: boolean;
  minimiseWindow(): Promise<void>;
  toggleMaximiseWindow(): Promise<void>;
  isWindowMaximised(): Promise<boolean>;
  closeWindow(): Promise<void>;
  openExternal(url: string): Promise<void>;
  pathForFile(file: File): string;
  saveText(name: string, content: string): Promise<string>;
  saveBytes(name: string, bytes: Uint8Array): Promise<string>;
  pickFolder(startIn: string): Promise<string>;
  showBrowserView?(target: string, rect: ViewRect): Promise<void>;
  hideBrowserView?(): Promise<void>;
  controlBrowserView?(target: string, action: string): Promise<void>;
  navigateBrowserView?(target: string, address: string): Promise<boolean>;
  onBrowserLoadState?(listener: (state: BrowserLoadState) => void): () => void;
  onBrowserLogin?(listener: (ask: BrowserLogin) => void): () => void;
  answerBrowserLogin?(id: string, username: string, password: string): Promise<void>;
  trustBrowserCertificate?(target: string): Promise<boolean>;
}

const bridge = () => (window as unknown as { reasonixHost?: ElectronBridge }).reasonixHost;

// Electron reports the platform under Node's names; the page spells them the
// way Go does, and one spelling is what keeps a CSS selector honest.
function normalise(platform: string): string {
  if (platform === "win32") return "windows";
  return platform;
}

class ElectronHost implements HostPort {
  constructor(private readonly api: ElectronBridge) {}
  describe() {
    return Promise.resolve({
      shell: "electron" as const,
      platform: normalise(this.api.platform),
      titleBar: this.api.titleBar,
    });
  }
  minimiseWindow() {
    void this.api.minimiseWindow();
  }
  toggleMaximiseWindow() {
    void this.api.toggleMaximiseWindow();
  }
  isWindowMaximised() {
    return this.api.isWindowMaximised().catch(() => false);
  }
  closeWindow() {
    void this.api.closeWindow();
  }
  openExternal(url: string) {
    void this.api.openExternal(url);
  }
  pathsForFiles(files: File[]) {
    // Resolved one at a time because that is the shape the platform offers;
    // a file the shell cannot place answers with "" and is dropped here.
    return files.map((f) => this.api.pathForFile(f)).filter(Boolean);
  }
  saveText(name: string, content: string) {
    return this.api.saveText(name, content);
  }
  saveBytes(name: string, bytes: Uint8Array) {
    return this.api.saveBytes(name, bytes);
  }
  pickFolder(startIn: string) {
    return this.api.pickFolder(startIn);
  }
  // A shell older than the verbs has no views to draw, and says so by lacking them.
  drawsBrowserViews() {
    return typeof this.api.showBrowserView === "function";
  }
  showBrowserView(target: string, rect: ViewRect) {
    void this.api.showBrowserView?.(target, rect);
  }
  hideBrowserView() {
    void this.api.hideBrowserView?.();
  }
  controlBrowserView(target: string, action: BrowserControl) {
    void this.api.controlBrowserView?.(target, action);
  }
  navigateBrowserView(target: string, address: string) {
    return this.api.navigateBrowserView?.(target, address) ?? Promise.resolve(false);
  }
  onBrowserLoadState(listener: (state: BrowserLoadState) => void) {
    return this.api.onBrowserLoadState?.(listener) ?? (() => {});
  }
  onBrowserLogin(listener: (ask: BrowserLogin) => void) {
    return this.api.onBrowserLogin?.(listener) ?? (() => {});
  }
  answerBrowserLogin(id: string, username: string, password: string) {
    void this.api.answerBrowserLogin?.(id, username, password);
  }
  trustBrowserCertificate(target: string) {
    return this.api.trustBrowserCertificate?.(target) ?? Promise.resolve(false);
  }
  updateStatus(): Promise<UpdateStatus> {
    return Promise.resolve({ current: null, available: false, latest: null });
  }
  openUpdater(): Promise<UpdateInstall | null> {
    return Promise.resolve(null);
  }
}

class BrowserHost implements HostPort {
  describe() {
    return Promise.resolve({ shell: "browser" as const, platform: "", titleBar: false });
  }
  minimiseWindow() {}
  toggleMaximiseWindow() {}
  isWindowMaximised() {
    return Promise.resolve(false);
  }
  closeWindow() {}
  openExternal(url: string) {
    window.open(url, "_blank", "noopener,noreferrer");
  }
  pathsForFiles() {
    return [];
  }
  saveText() {
    return Promise.resolve(null);
  }
  saveBytes() {
    return Promise.resolve(null);
  }
  pickFolder(_startIn?: string): Promise<string | null> {
    return Promise.resolve(null);
  }
  drawsBrowserViews() {
    return false;
  }
  showBrowserView() {}
  hideBrowserView() {}
  controlBrowserView() {}
  navigateBrowserView() {
    return Promise.resolve(false);
  }
  onBrowserLoadState() {
    return () => {};
  }
  onBrowserLogin() {
    return () => {};
  }
  answerBrowserLogin() {}
  trustBrowserCertificate() {
    return Promise.resolve(false);
  }
  updateStatus(): Promise<UpdateStatus> {
    return Promise.resolve({ current: null, available: false, latest: null });
  }
  openUpdater(): Promise<UpdateInstall | null> {
    return Promise.resolve(null);
  }
}

/** The Tauri global arrives in different shapes across versions; every call in
 *  this file goes through whichever one is actually here. */
function tauriInvoke(): ((cmd: string, args?: Record<string, unknown>) => Promise<unknown>) | null {
  const tauri = (window as unknown as { __TAURI__?: Record<string, unknown> }).__TAURI__;
  if (!tauri) return null;
  const core = tauri["core"] as { invoke?: (c: string, a?: Record<string, unknown>) => Promise<unknown> } | undefined;
  if (core?.invoke) return (cmd, args) => core.invoke!(cmd, args);
  if (typeof tauri["invoke"] === "function") {
    return tauri["invoke"] as (cmd: string, args?: Record<string, unknown>) => Promise<unknown>;
  }
  const ns = tauri["tauri"] as { invoke?: (c: string, a?: Record<string, unknown>) => Promise<unknown> } | undefined;
  if (ns?.invoke) return (cmd, args) => ns.invoke!(cmd, args);
  return null;
}

// The Tauri shell (tempora-shell.exe) runs the visible window and exposes the
// global Tauri API. It has no Electron bridge, but it does register a
// `pick_folder` command, so the native dialog opens on the shell's own UI thread
// — owned by the visible window, not the kernel process. That is what makes the
// folder picker actually appear in front instead of getting stuck behind the app.
class TauriHost extends BrowserHost {
  private call(cmd: string, args?: Record<string, unknown>): Promise<unknown> | null {
    const invoke = tauriInvoke();
    return invoke ? invoke(cmd, args) : null;
  }

  pickFolder(startIn?: string): Promise<string | null> {
    const call = this.call("pick_folder", { startIn: startIn ?? "" });
    if (!call) return Promise.resolve(null);
    // A picked folder comes back as its absolute path; cancelling returns "" so
    // SseHub.pickFolder does NOT fall through to the kernel's loopback picker.
    // An invoke ERROR (command missing / ACL denied) means this shell cannot
    // pick at all — return null so the hub falls back to the kernel route
    // instead of silently pretending the user cancelled.
    return call
      .then((p: unknown) => (typeof p === "string" && p ? p : ""))
      .catch((e: unknown) => {
        console.warn("[host] pick_folder invoke failed, falling back:", e);
        return null;
      });
  }

  updateStatus(): Promise<UpdateStatus> {
    const call = this.call("update_status");
    if (!call) return Promise.resolve({ current: null, available: false, latest: null });
    return call
      .then((raw: unknown) => {
        const r = raw as { current?: unknown; available?: unknown; latest?: unknown } | null;
        return {
          current: typeof r?.current === "string" ? r.current : null,
          available: r?.available === true,
          latest: typeof r?.latest === "string" ? r.latest : null,
        };
      })
      .catch((e: unknown) => {
        console.warn("[host] update_status invoke failed:", e);
        return { current: null, available: false, latest: null };
      });
  }

  /** Install the newer build straight away — no window in between.
   *  The shell restarts itself once it is on disk, so a resolve that says
   *  updated=false ("nothing to install") is the only resolve the caller sees;
   *  a real failure rejects, and the page says so instead of sitting silent. */
  openUpdater(): Promise<UpdateInstall | null> {
    const call = this.call("open_updater");
    if (!call) return Promise.resolve(null);
    return call.then((raw: unknown) => {
      const r = raw as { updated?: unknown; version?: unknown } | null;
      return {
        updated: r?.updated === true,
        version: typeof r?.version === "string" ? r.version : null,
      };
    });
  }
}

function pick(): HostPort {
  const api = bridge();
  if (api) return new ElectronHost(api);
  if (typeof (window as unknown as { __TAURI__?: unknown }).__TAURI__ !== "undefined") return new TauriHost();
  return new BrowserHost();
}

let chosen: HostPort | null = null;

/** The shell under this page, decided once. */
export function host(): HostPort {
  chosen ??= pick();
  return chosen;
}
