// Ported from DeepSeek-Reasonix (MIT) — upstream PR #14086.
import { useCallback, useRef, useState } from "react";
import type { HubPort, TreeWorkspace } from "../port/hub";

/** The sidebar's tree, and the one way it is read.
 *
 *  A progressive listing answers twice — the rows it has found, then the
 *  summaries it has since read — so a read is not a snapshot of a finished
 *  answer but the first half of one. `retryTree` is the explicit second ask: it
 *  tells the kernel to put the summaries a degraded read could not produce back
 *  on the queue, which an ordinary reload does not.
 *
 *  The newest read owns the state. A reload fired while a retry is in flight
 *  would otherwise land afterwards and put the failed summaries back as
 *  pending, which is the thing the reader just asked to get rid of.
 */
export function useTreeRead(hub: Pick<HubPort, "tree">) {
  const [tree, setTree] = useState<TreeWorkspace[]>([]);
  const newest = useRef(0);

  const read = useCallback(
    (retryMetadata: boolean) => {
      const mine = ++newest.current;
      return hub
        .tree(retryMetadata ? { retryMetadata: true } : undefined)
        .then((rows) => {
          if (mine === newest.current) setTree(rows);
        })
        .catch(() => {
          if (mine === newest.current) setTree([]);
        });
    },
    [hub],
  );

  const reloadTree = useCallback(() => read(false), [read]);
  const retryTree = useCallback(() => read(true), [read]);

  return { tree, reloadTree, retryTree };
}