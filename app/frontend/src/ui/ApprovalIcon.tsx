import type { ApprovalMode } from "../port/port";
import { APPROVAL_TIER } from "./approvals";

// 权限档的标记：同一支盾牌家族，盾内的符号随放行等级升级——
//   1 锁（需要批准的一律不放行）→ 2 问号（每次都停下来问）→ 3 闪电（低风险自动过）
// 到第 4 级盾牌本身让位给警示三角：那时候已经没有「边界」可画了。
// 等级越高的图标越「通」，颜色也从中性走到警示，眼睛不用读文字就能排序。
const SHIELD = "M8 2.2 13 4v3.5c0 3-1.8 5.1-5 6.3-3.2-1.2-5-3.3-5-6.3V4l5-1.8Z";

const MARK: Record<ApprovalMode, string> = {
  dontAsk: `${SHIELD}M6.8 8.4h2.4v2.1H6.8zM7.5 8.4v-.9a.5.5 0 0 1 1 0v.9`,
  ask: `${SHIELD}M7.05 7.05a1 1 0 1 1 1.45.9c-.3.16-.4.46-.4.9M8 10.45h.01`,
  auto: `${SHIELD}M8.7 6.1 7 8.6h1.9l-.4 2.4 1.8-2.7H8.5l.2-2.2z`,
  yolo: "M8 2.3 13.6 13H2.4L8 2.3zM8 6.5v3.1M8 11.2h.01",
};

export function ApprovalIcon({ mode, className }: { mode: ApprovalMode; className?: string }) {
  return (
    <svg
      className={["studio-approval-mark", className].filter(Boolean).join(" ")}
      viewBox="0 0 16 16"
      data-tier={APPROVAL_TIER[mode]}
      fill="none"
      stroke="currentColor"
      strokeWidth="1.35"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d={MARK[mode]} />
    </svg>
  );
}

// 四格等级条，填到第几格就是第几级。图标回答「什么档」，它回答「多重」，
// 两者一起把递增关系量出来——不靠颜色单独承担，色觉障碍下也读得出来。
export function ApprovalLevel({ mode }: { mode: ApprovalMode }) {
  const tier = APPROVAL_TIER[mode];
  return (
    <span className="studio-approval-level" aria-hidden="true">
      {[1, 2, 3, 4].map((n) => (
        <i key={n} data-on={n <= tier ? "" : undefined} />
      ))}
    </span>
  );
}
