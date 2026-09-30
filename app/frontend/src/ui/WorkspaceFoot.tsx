import { useEffect, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { t } from "../i18n";
import type { TreeWorkspace } from "../port/hub";
import type { AccountState } from "../port/port";
import type { Adder } from "./addws";
import { useDismiss } from "./dismiss";
import { StudioIcon } from "./StudioIcon";

interface Props {
  tree: TreeWorkspace[];
  activeWorkspace: TreeWorkspace | undefined;
  account: AccountState | null;
  unread?: string;
  adder: Adder;
  onOpen: (req: { root?: string; sessionPath?: string; fresh?: boolean }) => Promise<void>;
  onSettings: (section?: string) => void;
  onError: (e: unknown) => void;
}

/** The rail's foot: one capsule naming the workspace the window is looking at.
 *  Its menu opens the places a person actually meant — a new task here, a
 *  conversation they were in, another workspace — instead of the three doors
 *  that used to sit here and all lead to settings. */
export function WorkspaceFoot({
  tree,
  activeWorkspace,
  account,
  unread,
  adder,
  onOpen,
  onSettings,
  onError,
}: Props) {
  const [open, setOpen] = useState(false);
  const [at, setAt] = useState<{ left: number; bottom: number; width: number } | null>(null);
  const foot = useRef<HTMLDivElement>(null);
  const menu = useRef<HTMLDivElement>(null);
  useDismiss(open, foot, () => setOpen(false), menu);

  const root = activeWorkspace?.root ?? "";
  const name = activeWorkspace?.name || t("本地工作空间");
  const projects = tree.length;
  const sessions = useMemo(() => tree.reduce((n, w) => n + w.sessions.length, 0), [tree]);

  // This workspace's own conversations first; anything after that is another
  // workspace's, which is still a likelier destination than a settings pane.
  const recent = useMemo(() => {
    const own = (activeWorkspace?.sessions ?? []).filter((s) => !s.archived);
    const rest = tree
      .filter((w) => w.root !== root)
      .flatMap((w) => w.sessions.filter((s) => !s.archived));
    return [...own, ...rest].slice(0, 4);
  }, [tree, activeWorkspace, root]);

  // The menu is positioned from the capsule's box, so anything that moves the
  // capsule — a resize, a scroll — has to put it away rather than leave it
  // floating where the capsule used to be.
  useEffect(() => {
    if (!open) return;
    const drop = () => setOpen(false);
    window.addEventListener("resize", drop);
    window.addEventListener("scroll", drop, true);
    return () => {
      window.removeEventListener("resize", drop);
      window.removeEventListener("scroll", drop, true);
    };
  }, [open]);

  const toggle = () => {
    if (open) {
      setOpen(false);
      return;
    }
    const box = foot.current?.getBoundingClientRect();
    if (box) setAt({ left: box.left, bottom: window.innerHeight - box.top + 6, width: box.width });
    setOpen(true);
  };

  // Every entry closes the menu before it acts; the destination is the point,
  // and a menu left hanging over the pane it just opened is in the way.
  const go = (run: () => void) => {
    setOpen(false);
    run();
  };

  const who = account?.signedIn
    ? account.user?.label || account.user?.handle || account.user?.email || t("已登录")
    : account?.expired
      ? t("登录已过期")
      : account?.error
        ? t("无法连接身份服务")
        : unread
          ? t("登录状态不可用")
          : t("账号未登录");

  return (
    <div className="studio-user-foot" ref={foot}>
      <button
        className="studio-wsfoot"
        data-action="workspace.menu"
        data-open={open ? "" : undefined}
        aria-expanded={open}
        aria-label={t("工作空间")}
        onClick={toggle}
      >
        <span className="studio-wsfoot-mark" aria-hidden="true"><StudioIcon name="layers" /></span>
        <span className="studio-wsfoot-main">
          <b>{name}</b>
          <small>{projects} {t("个工作区")} · {sessions} {t("个会话")}</small>
        </span>
        <span className="studio-wsfoot-chev" aria-hidden="true"><StudioIcon name="chevron" /></span>
      </button>

      {open && at
        ? createPortal(
            <div
              className="wsmenu"
              ref={menu}
              role="menu"
              style={{ left: at.left, bottom: at.bottom, width: at.width }}
            >
              <div className="wsmenu-head">
                <b>{name}</b>
                {root ? <small>{root}</small> : null}
                <div className="wsmenu-stats">
                  <span>{projects} {t("个工作区")}</span>
                  <span>{sessions} {t("个会话")}</span>
                </div>
              </div>

              <button
                className="wsitem"
                role="menuitem"
                onClick={() => go(() => void onOpen({ root, fresh: true }).catch(onError))}
              >
                <StudioIcon name="plus" />
                <span className="wsmenu-ellipsis">{t("在此新建任务")}</span>
              </button>

              {recent.length ? (
                <>
                  <div className="wsmenu-label">{t("继续最近会话")}</div>
                  {recent.map((s) => (
                    <button
                      key={s.path}
                      className="wsitem"
                      role="menuitem"
                      onClick={() => go(() => void onOpen({ sessionPath: s.path }).catch(onError))}
                    >
                      <StudioIcon name="clock" />
                      <span className="wsmenu-ellipsis">{s.title || s.name}</span>
                    </button>
                  ))}
                </>
              ) : null}

              {projects > 1 ? (
                <>
                  <div className="wsmenu-label">{t("切换工作区")}</div>
                  {tree.slice(0, 6).map((w) => (
                    <button
                      key={w.root}
                      className="wsitem"
                      role="menuitem"
                      data-current={w.root === root ? "" : undefined}
                      onClick={() => go(() => void onOpen({ root: w.root, fresh: true }).catch(onError))}
                    >
                      <StudioIcon name="folder" />
                      <span className="wsmenu-ellipsis">{w.name}</span>
                      <small>{w.sessions.length}</small>
                    </button>
                  ))}
                </>
              ) : null}

              <button
                className="wsitem"
                role="menuitem"
                disabled={adder.busy}
                onClick={() => go(() => adder.add())}
              >
                <StudioIcon name="folder" />
                <span className="wsmenu-ellipsis">{t("添加工作区")}</span>
              </button>

              <div className="wsmenu-sep" />

              <button className="wsitem" role="menuitem" onClick={() => go(() => onSettings("account"))}>
                <StudioIcon name="shield" />
                <span className="wsmenu-ellipsis">{who}</span>
              </button>
              <button className="wsitem" role="menuitem" onClick={() => go(() => onSettings())}>
                <StudioIcon name="settings" />
                <span className="wsmenu-ellipsis">{t("设置")}</span>
              </button>
            </div>,
            document.body,
          )
        : null}
    </div>
  );
}
