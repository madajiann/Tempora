import { t } from "../i18n";
import type { ApprovalMode } from "../port/port";

// One table for every surface that names an approval mode: the composer menu,
// Settings and the shelf. Ordered from strictest to most permissive.
export const APPROVALS: [ApprovalMode, string, string][] = [
  ["dontAsk", "不询问", "不显示审批请求；需要批准的操作一律不执行"],
  ["ask", "询问", "每次执行操作前请求确认"],
  ["auto", "自动批准", "低风险操作自动放行，写入操作仍需确认"],
  ["yolo", "全部放行", "不再请求确认，仅在完全信任当前工作区时使用"],
];

const row = (mode: ApprovalMode | undefined) => APPROVALS.find(([id]) => id === mode);

// 放行等级 1–4，直接由上面那张表的顺序推导：表是从最严写到最松的，
// 所以加一档不会漏掉等级，改顺序也不会和图标对不上。
// 图标、等级条、配色都读它——「越往下放行越多」因此是看得见的，不必读描述。
export const APPROVAL_TIER = Object.fromEntries(
  APPROVALS.map(([id], i) => [id, (i + 1) as 1 | 2 | 3 | 4]),
) as Record<ApprovalMode, 1 | 2 | 3 | 4>;

export const approvalName = (mode: ApprovalMode | undefined, fallback = "询问"): string => t(row(mode)?.[1] ?? fallback);

export const approvalNote = (mode: ApprovalMode | undefined): string => t(row(mode)?.[2] ?? "");
