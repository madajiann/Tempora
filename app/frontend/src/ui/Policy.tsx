import { useRef, useState } from "react";
import { t } from "../i18n";
import { reason } from "../i18n/kernel";
import type { AgentPort, ApprovalMode, SessionStatus } from "../port/port";
import { useDismiss } from "./dismiss";
import { APPROVALS, APPROVAL_TIER, approvalName } from "./approvals";
import { ApprovalIcon, ApprovalLevel } from "./ApprovalIcon";

// Permission is one boundary, not a catch-all for every way a turn can run.
// Work strategy and model effort live in their own controls beside this one.
interface Props {
  port: AgentPort;
  status: SessionStatus | null;
  onChanged: () => void;
  onBoundary?: () => void;
}

export function Policy({ port, status, onChanged, onBoundary }: Props) {
  const [open, setOpen] = useState(false);
  const [asking, setAsking] = useState("");
  const [refused, setRefused] = useState("");
  const wrap = useRef<HTMLDivElement>(null);
  useDismiss(open, wrap, () => setOpen(false));

  if (!status) return null;

  const apv = status.toolApprovalMode ?? "ask";
  const label = approvalName(apv);
  const apply = (value: ApprovalMode) => {
    if (asking) return;
    setAsking(value);
    setRefused("");
    port.setApprovalMode(value)
      .then(onChanged)
      .catch((e: unknown) => setRefused(reason(e)))
      .finally(() => setAsking(""));
  };

  return (
    <div
      className="picker policy"
      ref={wrap}
      data-quiet={apv === "ask" ? "" : undefined}
    >
      <button
        className="mode plain"
        data-action="chrome.policy"
        data-tier={APPROVAL_TIER[apv]}
        data-risk={apv === "yolo" ? "" : undefined}
        aria-expanded={open}
        aria-label={`${t("执行权限")}：${label}`}
        title={`${t("执行权限")}：${label}`}
        onClick={() => setOpen((value) => !value)}
      >
        <span className="ic" aria-hidden="true">
          <ApprovalIcon mode={apv} />
        </span>
        <span className={apv === "yolo" ? "lb polrisk" : "lb"} data-display={label}>{label}</span>
        <span className="studio-control-chevron" aria-hidden="true">⌄</span>
      </button>
      <div className="menu modemenu polmenu" role="group" aria-label={t("执行权限")} hidden={!open}>
        <div className="studio-policy-head"><b>{t("执行权限")}</b><small>{t("当前任务")}</small></div>
        <div className="studio-policy-primary">
          {APPROVALS.map(([value, name, note]) => (
            <div key={value}>
              {value === "yolo" && <div className="studio-policy-risk">{t("高风险")}</div>}
              <button
                className={`studio-permission-option${value === "yolo" ? " studio-permission-yolo" : ""}`}
                data-action="tool-approval.mode"
                data-value={value}
                data-tier={APPROVAL_TIER[value]}
                data-on={apv === value ? "" : undefined}
                data-pending={asking === value ? "" : undefined}
                aria-pressed={apv === value}
                disabled={!!asking}
                onClick={() => apply(value)}
              >
                <span className="studio-permission-icon" aria-hidden="true">
                  <ApprovalIcon mode={value} />
                </span>
                <span className="studio-permission-copy">
                  <span className="studio-permission-title">
                    <b>{t(name)}</b>
                    <ApprovalLevel mode={value} />
                  </span>
                  <small>{t(note)}</small>
                </span>
                {apv === value && <span className="studio-permission-check" aria-hidden="true">✓</span>}
              </button>
            </div>
          ))}
          {refused && <div className="note bad studio-policy-error" role="alert">{refused}</div>}
        </div>
        <div className="studio-policy-note">{t("审批决定何时询问；沙盒限定实际访问范围。")}</div>
        <button className="studio-policy-boundary" data-action="settings.section" data-value="tools:sandbox" onClick={onBoundary} disabled={!onBoundary}>
          <span><b>{t("沙盒与运行边界")}</b><small>{t("在设置中查看当前隔离与网络权限")}</small></span>
          <span aria-hidden="true">›</span>
        </button>
      </div>
    </div>
  );
}
