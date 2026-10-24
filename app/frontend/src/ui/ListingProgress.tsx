// Ported from DeepSeek-Reasonix (MIT) — upstream PR #14086.
import { t } from "../i18n";
import type { TreeWorkspace } from "../port/hub";

/** What one folder says while its history is still being read.
 *
 *  A progressive listing answers twice: once with the conversations it has
 *  found, then again as their summaries arrive. Without a line here the second
 *  answer looks like the first one being wrong — the count beside the folder
 *  stops matching and nothing says why.
 *
 *  Nothing is rendered once the counts are final, which is also what an older
 *  kernel that never reports them gets: it has no listing state, so it never
 *  draws a line about reading that is not happening.
 */
export function ListingProgress({
  workspace,
  searching,
  onRetry,
}: {
  workspace: TreeWorkspace;
  searching: boolean;
  onRetry?: () => void;
}) {
  if (workspace.countsComplete !== false) return null;
  const failed = workspace.listingState === "degraded";
  return (
    <small className="sessnote" role="status" aria-busy={!failed}>
      {failed
        ? t("部分历史摘要暂不可用，可继续打开会话")
        : searching
          ? t("仍在搜索部分历史会话…")
          : t("正在读取历史摘要…")}
      {failed && onRetry && (
        <>
          {" "}
          {/* remote.read is the registry's "ask again for a list that did not
              answer" — the same gesture as re-reading a host's book, which is
              what this button does for this machine's folder. */}
          <button
            type="button"
            className="ws-reading-retry"
            data-action="remote.read"
            data-target={workspace.root}
            onClick={onRetry}
          >
            {t("重试")}
          </button>
        </>
      )}
    </small>
  );
}