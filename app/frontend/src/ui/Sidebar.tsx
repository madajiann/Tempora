import { useEffect, useMemo, useRef, useState } from "react";
import { t } from "../i18n";
import type { AccountState } from "../port/port";
import type { HubPort, RuntimeView, TreeWorkspace } from "../port/hub";
import type { RemoteHost } from "../port/remote";
import type { Adder } from "./addws";
import { WorkspaceFoot } from "./WorkspaceFoot";
import { RailSearch } from "./railsearch";
import { RemoteHosts } from "./RemoteHosts";
import { host, type UpdateStatus } from "../port/host";
import { StudioIcon } from "./StudioIcon";
import { Palette, type Command } from "./Palette";
import { Workspaces } from "./Workspaces";

interface Props {
  hub: HubPort;
  // Collapsed, the column keeps its scroll position and its folds; inert is the
  // other half of that — a column nobody can see must not be reachable by Tab.
  collapsed: boolean;
  tree: TreeWorkspace[];
  runtimes: RuntimeView[];
  runs: Record<string, { run: string; live: boolean }>;
  active: string;
  // Where a new session lands, and the row the tree marks as focused. The window
  // decides it from the focused pane, so it arrives rather than being derived.
  activeWorkspace: TreeWorkspace | undefined;
  liveIds: (ids: string[]) => string[];
  // Pins outlive this column — archiving a session drops one — so the set is the
  // window's and only the toggle comes down here.
  pinned: Set<string>;
  onPin: (path: string) => void;
  remotes: RemoteHost[] | null;
  remoteTrees: Record<string, TreeWorkspace[] | null>;
  reloadRemotes: () => Promise<void>;
  reloadRemoteTrees: () => Promise<void>;
  readRemoteTree: (host: string) => Promise<void>;
  reloadTree: () => Promise<void>;
  adder: Adder;
  onOpen: (req: { root?: string; sessionPath?: string; fresh?: boolean }) => Promise<void>;
  onOpenRemote: (host: string, workspace?: string, sessionPath?: string) => Promise<void>;
  onFocusPane: (id: string) => void;
  onClosePanes: (ids: string[]) => Promise<void>;
  onPause: (runtimeId: string) => void;
  onArchive: (path: string, archived: boolean, runtimeId?: string) => Promise<void>;
  onRename: (path: string, title: string) => void;
  onCollapse: () => void;
  account: AccountState | null;
  accountUnread: string;
  wallet: string;
  onSettings: (section?: string) => void;
  onError: (e: unknown) => void;
}

/** The window's left column: what is mounted, what has been said in it, and who
 *  is signed in. It owns only what nothing outside it reads — which scope the
 *  session filter is on, whether the switcher is open, and which workspaces are
 *  folded. Everything else belongs to the window and arrives as a prop. */
export function Sidebar({
  hub,
  collapsed,
  tree,
  runtimes,
  runs,
  active,
  activeWorkspace,
  liveIds,
  pinned,
  onPin,
  remotes,
  remoteTrees,
  reloadRemotes,
  reloadRemoteTrees,
  readRemoteTree,
  reloadTree,
  adder,
  onOpen,
  onOpenRemote,
  onFocusPane,
  onClosePanes,
  onPause,
  onArchive,
  onRename,
  onCollapse,
  account,
  accountUnread,
  wallet,
  onSettings,
  onError,
}: Props) {
  const [railScope, setRailScope] = useState<"all" | "live" | "pinned" | "archived">("all");
  const [palette, setPalette] = useState(false);
  const [folded, setFolded] = useState<Set<string>>(new Set());
  const newSessionRoot = activeWorkspace?.root;

  // The shortcut the button prints. It was drawn and never bound, so the one
  // thing a person learns from the label did nothing.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (!(e.ctrlKey || e.metaKey) || e.key.toLowerCase() !== "k" || e.altKey) return;
      e.preventDefault();
      setPalette((on) => !on);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  // What the palette can do is what this column already offers, named once so
  // the two cannot drift into two different lists of the same thing.
  const commands = useMemo<Command[]>(
    () => [
      { id: "new", label: t("新建会话"), icon: "plus", keywords: "new session chat 新建",
        run: () => void onOpen({ root: newSessionRoot, fresh: true }).catch(onError) },
      { id: "storage", label: t("文件"), icon: "file", keywords: "files storage 文件 存储",
        run: () => onSettings("storage") },
      { id: "ext", label: t("工具与集成"), icon: "plug", keywords: "tools mcp skills 工具 集成",
        run: () => onSettings("ext") },
      { id: "remote", label: t("运行环境"), icon: "server", keywords: "ssh local remote 运行环境",
        run: () => onSettings("remote") },
      { id: "providers", label: t("模型服务"), icon: "layers", keywords: "model provider 模型 来源 服务",
        run: () => onSettings("providers") },
      { id: "usage", label: t("钱包与用量"), icon: "wallet", keywords: "usage cost token 用量 费用",
        run: () => onSettings("usage") },
      { id: "settings", label: t("设置"), icon: "settings", keywords: "settings preferences 设置 偏好",
        run: () => onSettings() },
    ],
    [newSessionRoot, onOpen, onSettings, onError],
  );
  const sessionCount = tree.reduce((n, ws) => n + ws.sessions.filter((session) => !session.archived).length, 0);
  const archivedCount = tree.reduce((n, ws) => n + ws.sessions.filter((session) => session.archived).length, 0);
  const liveCount = liveIds(runtimes.map((rt) => rt.id)).length;

  // The wordmark reports the shell's own version and whether a newer build is
  // out. Asked on mount and then every half hour — never per render, which
  // would hammer the update endpoint.
  const [update, setUpdate] = useState<UpdateStatus>({ current: null, available: false, latest: null });
  // idle → installing → failed. 装完壳会自己重启，所以「成功」这一态根本不会
  // 留在屏幕上 —— failed 才是唯一需要画出来的结果。
  const [install, setInstall] = useState<"idle" | "installing" | "failed">("idle");
  useEffect(() => {
    let alive = true;
    let asked = 0;
    const ask = () => {
      asked = Date.now();
      void host()
        .updateStatus()
        .then((s) => {
          if (alive) setUpdate(s);
        });
    };
    ask();
    // 半小时复查一次：只在挂载时问一次的话，运行期间发布的新版本要等下次重启
    // 才看得见，用户看到的就是「明明发了新版却一直不提示」。间隔取半小时而不是
    // 更短，是因为版本是小时级变化的事，不该按分钟去敲更新端点。
    const timer = window.setInterval(ask, 30 * 60 * 1000);
    // 窗口重新可见时补一次（切回来、从最小化恢复），五分钟内的重复不算。
    const onVisible = () => {
      if (document.visibilityState === "visible" && Date.now() - asked > 5 * 60 * 1000) ask();
    };
    document.addEventListener("visibilitychange", onVisible);
    return () => {
      alive = false;
      window.clearInterval(timer);
      document.removeEventListener("visibilitychange", onVisible);
    };
  }, []);

  // 直接装，中间不开窗口：壳历史上把 updater.html 加载成 about:blank，弹出的
  // 是一扇没有关闭按钮的空白窗，看着就是「点了之后卡死」。
  const installUpdate = () => {
    if (install === "installing") return;
    setInstall("installing");
    void host()
      .openUpdater()
      .then(() => setInstall("idle"))
      .catch((e: unknown) => {
        console.warn("[sidebar] update install failed:", e);
        setInstall("failed");
      });
  };

  // 版本号挂在按钮上而不是写进词条：「v0.1.22」这种东西不该进翻译表。
  const updateLabel =
    install === "failed"
      ? t("安装失败，点击重试")
      : install === "installing"
        ? t("正在安装 v{version}…", { version: update.latest ?? "" })
        : t("有新版本 v{version}", { version: update.latest ?? "" });

  const onFold = (root: string, shut: boolean) =>
    setFolded((prev) => {
      const next = new Set(prev);
      if (shut) next.add(root);
      else next.delete(root);
      return next;
    });

  // Seeded once, never per reload: after that the folds are the reader's.
  const seeded = useRef(false);
  useEffect(() => {
    if (seeded.current || !tree.length) return;
    seeded.current = true;
    setFolded(new Set(tree.map((ws) => ws.root).filter((root) => root !== newSessionRoot)));
  }, [tree, newSessionRoot]);

  return (
    <>
    {/* Outside the column's inert wrapper: a collapsed rail must still be
        reachable by the shortcut that opens this. */}
    <Palette
      open={palette}
      onClose={() => setPalette(false)}
      commands={commands}
      tree={tree}
      onOpenSession={(path) => void onOpen({ sessionPath: path }).catch(onError)}
    />
    {/* 收起而不是卸载：卸掉就丢了侧栏的滚动位置、Inspector 的展开、当前选
        中的面板。inert 是「看不见就够不着」那一半 —— 只做视觉隐藏的话，
        屏幕上没有的栏还能被 Tab 走进去。 */}
    <button className="railveil" data-action="chrome.rail" tabIndex={-1} aria-label={t("收起工作区栏")} onClick={() => onCollapse()} />
    <div className="rail" inert={collapsed}>
      <div className="railscroll">
      <div className="studio-rail-head">
        <div className="studio-brand" aria-label="Tempora Studio">
          <span className="studio-brand-mark" aria-hidden="true"><StudioIcon name="brand" /></span>
          <span className="studio-brand-word">
            <span className="studio-brand-line">
              <b>empor<span className="studio-brand-accent">a</span></b>
              <i className="studio-brand-suffix">studio</i>
            </span>
          </span>
          <span
            className="studio-brand-meta"
            data-tip={update.available ? `有新版本 ${update.latest}，点击更新` : "当前已是最新版本"}
          >
              <small>{update.current ? `v${update.current}` : ""}</small>
              <button
                type="button"
                className="studio-update-dot"
                data-state={update.available ? "available" : "current"}
                aria-label={update.available ? `有新版本 ${update.latest}，点击更新` : "已是最新版本"}
                onClick={() => installUpdate()}
              />
          </span>
          <button className="studio-collapse" data-action="chrome.rail" onClick={() => onCollapse()} aria-label={t("收起工作区栏")} title={t("收起侧栏")}><StudioIcon name="panel" /></button>
        </div>
        {update.available && (
          <button
            type="button"
            className="studio-update-bar"
            data-action="chrome.update"
            data-phase={install}
            aria-label={updateLabel}
            onClick={() => installUpdate()}
          >
            <span className="studio-update-bar-mark" aria-hidden="true">
              <StudioIcon name={install === "installing" ? "refresh" : "download"} />
            </span>
            <span className="studio-update-bar-label">{updateLabel}</span>
          </button>
        )}
        <button
          className="studio-new-task"
          data-action="session.new"
          onClick={() => void onOpen({ root: newSessionRoot, fresh: true }).catch(onError)}
        >
          <span aria-hidden="true"><StudioIcon name="plus" /></span>{t("新建会话")}<kbd>Alt N</kbd>
        </button>
        <button className="studio-search" data-action="workspace.search" onClick={() => setPalette(true)}>
          <span aria-hidden="true"><StudioIcon name="search" /></span>{t("搜索与快捷操作")}<kbd>Ctrl K</kbd>
        </button>
        <div className="studio-quicknav">
          <button data-action="settings.section" data-value="storage" onClick={() => onSettings("storage")}><span aria-hidden="true"><StudioIcon name="file" /></span><b>{t("文件")}</b></button>
          <button data-action="settings.section" data-value="ext" onClick={() => onSettings("ext")}><span aria-hidden="true"><StudioIcon name="plug" /></span><b>{t("工具与集成")}</b><small>MCP · Skills</small></button>
          <button data-action="settings.section" data-value="remote" onClick={() => onSettings("remote")}><span aria-hidden="true"><StudioIcon name="server" /></span><b>{t("运行环境")}</b><small>Local / SSH</small></button>
        </div>
        <div className="studio-section-label studio-session-label"><span>{t("会话")}</span></div>
        <div className="studio-session-filters" role="group" aria-label={t("会话范围")}>
          <div className="studio-session-segments">
            <button data-action="session.filter" data-value="all" aria-pressed={railScope === "all"} onClick={() => setRailScope("all")}><span>{t("全部")}</span><b>{sessionCount}</b></button>
            <button data-action="session.filter" data-value="live" aria-pressed={railScope === "live"} onClick={() => setRailScope("live")}><span>{t("进行中")}</span><b>{liveCount}</b></button>
            <button data-action="session.filter" data-value="pinned" aria-pressed={railScope === "pinned"} onClick={() => setRailScope("pinned")}><span>{t("置顶")}</span><b>{pinned.size}</b></button>
            <button data-action="session.filter" data-value="archived" aria-pressed={railScope === "archived"} onClick={() => setRailScope("archived")}><span>{t("归档")}</span><b>{archivedCount}</b></button>
          </div>
          <button className="studio-filter-search" data-action="workspace.search" onClick={() => document.querySelector<HTMLInputElement>(".wsfind input")?.focus()} aria-label={t("按名称筛选会话")}><StudioIcon name="search" /></button>
        </div>
      </div>
      <RailSearch>
      <Workspaces
        hub={hub}
        tree={tree}
        runtimes={runtimes}
        active={active}
        folded={folded}
        onFold={onFold}
        reload={reloadTree}
        onOpen={onOpen}
        onFocus={onFocusPane}
        onClose={onClosePanes}
        liveIds={liveIds}
        runs={runs}
        scope={railScope}
        pinned={pinned}
        onPin={onPin}
        onPause={(runtimeId) => onPause(runtimeId)}
        onArchive={onArchive}
        onRename={onRename}
        onError={onError}
        adder={adder}
      >
        {remotes ? (
          <RemoteHosts
            hub={hub}
            hosts={remotes}
            runtimes={runtimes}
            active={active}
            onOpen={onOpenRemote}
            onFocus={onFocusPane}
            reload={reloadRemotes}
            trees={remoteTrees}
            reloadTrees={reloadRemoteTrees}
            readTree={readRemoteTree}
            onClose={onClosePanes}
            liveIds={liveIds}
            onError={onError}
          />
        ) : null}
      </Workspaces>
      </RailSearch>
      </div>
      <div className="railfoot">
        <button className="studio-wallet" data-action="settings.section" data-value="usage" onClick={() => onSettings("usage")}><span aria-hidden="true"><StudioIcon name="wallet" /></span><b>{t("钱包与用量")}</b>{wallet && <small>{wallet}</small>}</button>
        <WorkspaceFoot
          tree={tree}
          activeWorkspace={activeWorkspace}
          account={account}
          unread={accountUnread}
          adder={adder}
          onOpen={onOpen}
          onSettings={onSettings}
          onError={onError}
        />
      </div>
    </div>
    </>
  );
}
