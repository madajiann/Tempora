// @vitest-environment jsdom
import { describe, expect, it, vi } from "vitest";
import { act, renderHook } from "@testing-library/react";
import { useTreeRead } from "./useTreeRead";
import type { HubPort, TreeRead, TreeWorkspace } from "../port/hub";

// Ported from DeepSeek-Reasonix (MIT) — upstream PR #14086.

const ws = (...roots: string[]): TreeWorkspace[] =>
  roots.map((root) => ({ root, name: root, sessions: [], countsComplete: false }) as TreeWorkspace);

const hubOf = (tree: HubPort["tree"]) => ({ tree }) as unknown as HubPort;

describe("reading this machine's tree", () => {
  it("asks for the progressive tree, and a retry asks again for the failed summaries", async () => {
    const k = { calls: [] as unknown[], fn: vi.fn(async (_read?: unknown) => ws("/new")) };
    const hub = hubOf(k.fn as unknown as HubPort["tree"]);
    const { result } = renderHook(() => useTreeRead(hub));

    await act(() => result.current.reloadTree());
    // An ordinary read carries no retry: the kernel's background work is
    // already filling the summaries in, and re-queueing them on every reload
    // would undo the ordering it chose.
    expect(k.fn).toHaveBeenNthCalledWith(1, undefined);
    expect(result.current.tree.map((w) => w.root)).toEqual(["/new"]);

    await act(() => result.current.retryTree());
    expect(k.fn).toHaveBeenNthCalledWith(2, { retryMetadata: true });

    await act(() => result.current.reloadTree());
    expect(k.fn).toHaveBeenNthCalledWith(3, undefined);
  });

  // Two reads in flight, and the older one lands last. The retry asked for a
  // better answer than the reload behind it, so the reload's answer is the one
  // that must not be shown.
  it("drops the older read's late answer instead of the retry's", async () => {
    let land: (() => void)[] = [];
    const fn = vi.fn(
      (read?: TreeRead) =>
        new Promise<TreeWorkspace[]>((resolve) => land.push(() => resolve(ws(String(read?.retryMetadata))))),
    );
    const { result } = renderHook(() => useTreeRead(hubOf(fn as unknown as HubPort["tree"])));

    let first: Promise<unknown>;
    let second: Promise<unknown>;
    act(() => {
      first = result.current.reloadTree();
      second = result.current.retryTree();
    });
    // The retry resolves first, then the reload it was meant to replace.
    await act(async () => {
      land[1]();
      await second;
    });
    await act(async () => {
      land[0]();
      await first;
    });
    expect(result.current.tree.map((w) => w.root)).toEqual(["true"]);
  });

  // A kernel that cannot answer leaves the tree empty rather than keeping a
  // stale one on screen: the sidebar's counts come from this.
  it("empties the tree when a read fails", async () => {
    const fn = vi.fn(async () => {
      throw new Error("remote.unreachable");
    });
    const { result } = renderHook(() => useTreeRead(hubOf(fn as unknown as HubPort["tree"])));
    await act(() => result.current.reloadTree());
    expect(result.current.tree).toEqual([]);
  });
});