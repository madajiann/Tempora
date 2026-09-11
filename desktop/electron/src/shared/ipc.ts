export const IPC = {
  contract: "tempora:contract",
  invoke: "tempora:invoke",
  event: "tempora:event",
  serviceState: "tempora:service-state",
  serviceStateGet: "tempora:service-state:get",
  processDiagnostics: "tempora:native:process-diagnostics",
  captureRendererProfile: "tempora:native:capture-renderer-profile",
  cancelRendererProfile: "tempora:native:cancel-renderer-profile",
  exportHeapSnapshot: "tempora:native:export-heap-snapshot",
  openExternal: "tempora:native:open-external",
  clipboardWrite: "tempora:native:clipboard-write",
  clipboardRead: "tempora:native:clipboard-read",
  windowMinimise: "tempora:native:window-minimise",
  windowToggleMaximise: "tempora:native:window-toggle-maximise",
  windowIsMaximised: "tempora:native:window-is-maximised",
  windowClose: "tempora:native:window-close",
  windowGetBounds: "tempora:native:window-get-bounds",
  windowSetTheme: "tempora:native:window-set-theme",
  windowSetBackground: "tempora:native:window-set-background",
  appZoomGet: "tempora:native:app-zoom-get",
  appZoomSet: "tempora:native:app-zoom-set",
  appZoomReset: "tempora:native:app-zoom-reset",
  graphicsGet: "tempora:native:graphics-get",
  graphicsSet: "tempora:native:graphics-set",
  browserControlGet: "tempora:native:browser-control-get",
  browserControlSetEnabled: "tempora:native:browser-control-set-enabled",
  browserControlSetIgnoreCertificateErrors: "tempora:native:browser-control-set-ignore-certificate-errors",
  browserControlClearCache: "tempora:native:browser-control-clear-cache",
  browserControlClearAll: "tempora:native:browser-control-clear-all",
  browserControlImportChrome: "tempora:native:browser-control-import-chrome",
  browserList: "tempora:browser:list",
  browserOpen: "tempora:browser:open",
  browserClose: "tempora:browser:close",
  browserActivate: "tempora:browser:activate",
  browserNavigate: "tempora:browser:navigate",
  browserSetZoom: "tempora:browser:set-zoom",
  browserToggleDevTools: "tempora:browser:toggle-devtools",
  browserResume: "tempora:browser:resume",
  browserUserTakeover: "tempora:browser:user-takeover",
  browserSetLayout: "tempora:browser:set-layout",
  browserSetOverlay: "tempora:browser:set-overlay",
  browserTabs: "tempora:browser:tabs",
  browserDownload: "tempora:browser:download",
  browserTakeover: "tempora:browser:takeover",
} as const;

export type ServicePhase = "starting" | "ready" | "restarting" | "failed" | "exited";

export interface ServiceState {
  phase: ServicePhase;
  generation: string;
  error?: string;
}

export interface ContractInfo {
  protocolVersion: number;
  digest: string;
  commands: readonly string[];
}

export interface EventFrame {
  seq: number;
  generation: string;
  name: string;
  args: unknown[];
}

export type IpcResult = { ok: true; value: unknown } | { ok: false; message: string };

export interface WindowBounds {
  x: number;
  y: number;
  width: number;
  height: number;
  maximised: boolean;
}

export type WindowTheme = "system" | "light" | "dark";

export type HostOS = "darwin" | "windows" | "linux";

export type BrowserControlWarning = "invalid-config" | "unreadable-config" | "unsupported-version";

export interface BrowserControlState {
  controlEnabled: boolean;
  ignoreCertificateErrors: boolean;
  writable: boolean;
  warning: BrowserControlWarning | null;
}

export type ChromeImportFailure =
  | "chrome-missing"
  | "profile-not-found"
  | "cookies-unreadable"
  | "safe-storage-denied"
  | "safe-storage-unavailable"
  | "unsupported-platform";

export type ChromeImportOutcome =
  | { ok: true; profile: string; cookies: number; skipped: number }
  | { ok: false; reason: ChromeImportFailure };

export function hostOS(platform: string): HostOS {
  if (platform === "darwin") return "darwin";
  if (platform === "win32") return "windows";
  return "linux";
}

export type BrowserTabMode = "agent" | "human";

export interface BrowserTabView {
  id: string;
  taskId: string;
  url: string;
  title: string;
  loading: boolean;
  canGoBack: boolean;
  canGoForward: boolean;
  temporary: boolean;
  mode: BrowserTabMode;
  epoch: number;
  zoom: number;
  active: boolean;
  error: { code: number; description: string } | null;
}

export type BrowserDownloadState = "progressing" | "completed" | "cancelled" | "interrupted";

export interface BrowserDownloadView {
  id: string;
  tabId: string;
  url: string;
  filename: string;
  path: string;
  state: BrowserDownloadState;
  received: number;
  total: number;
}

export interface BrowserLayoutRect {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface BrowserOpenOptions {
  temporary?: boolean;
  taskId?: string;
}

export type BrowserNavigateAction = "back" | "forward" | "reload" | "stop";

export interface BrowserNavigateTarget {
  url?: string;
  action?: BrowserNavigateAction;
}

export type BrowserTakeoverKind = "mousedown" | "keydown" | "wheel" | "touchstart" | "pointerdown";
