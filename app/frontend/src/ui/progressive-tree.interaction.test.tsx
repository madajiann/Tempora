// @vitest-environment jsdom
import { afterEach, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import "./testkit";
import { Workspaces } from "./Workspaces";
import { ListingProgress } from "./ListingProgress";
import type { TreeWorkspace } from "../port/hub";

// Ported from DeepSeek-Reasonix (MIT) — upstream PR #14086.

afterEach(cleanup);

// A folder the kernel has found but not finished counting. Everything here is
// about one thing: the folder is real, its rows are still arriving, and the
// sidebar must not draw that as an empty or a finished list.
const pending: TreeWorkspace = {
  root: "/project",
  name: "project",
  remembered: true,
  sessions: [],
  countsComplete: false,
  listingState: "discovering",
};

function tree(ws: TreeWorkspace, open = vi.fn(async () => {}), onRetryTree: (() => void) | undefined = undefined) {
  return (
    <Workspaces
      hub={{} as never}
      tree={[ws]}
      runtimes={[]}
      active=""
      folded={new Set()}
      onFold={() => {}}
      reload={async () => {}}
      onRetryTree={onRetryTree}
      onOpen={open}
      onFocus={() => {}}
      onClose={async () => {}}
      liveIds={() => []}
      runs={{}}
      onRename={() => {}}
      onError={() => {}}
      adder={{ add: () => {}, close: () => {}, at: null } as never}
    />
  );
}

it("keeps a discovered folder visible until its history is known", () => {
  render(tree(pending));
  expect(screen.getByText("project")).toBeTruthy();
  expect(screen.getByText("正在读取历史摘要…")).toBeTruthy();
  // Neither empty state: the folder is there, it is the count that is not.
  expect(screen.queryByText("没有匹配的会话")).toBeNull();
  expect(screen.queryByText("尚无文件夹")).toBeNull();
});

it("opens a conversation whose summary is still being read, then shows the real one", () => {
  const open = vi.fn(async () => {});
  const row = {
    path: "/project/sessions/v4-a.jsonl",
    name: "v4-a",
    countsKnown: false,
    metadataState: "pending" as const,
  };
  const { rerender } = render(tree({ ...pending, listingState: "indexing", sessions: [row] }, open));
  fireEvent.click(screen.getByText("v4-a"));
  expect(open).toHaveBeenCalledWith({ root: "/project", sessionPath: row.path });
  expect(screen.getByText("正在读取摘要")).toBeTruthy();

  rerender(
    tree(
      {
        ...pending,
        countsComplete: true,
        listingState: "ready",
        sessions: [{ ...row, title: "Recovered title", turns: 2, metadataState: "ready", countsKnown: true }],
      },
      open,
    ),
  );
  expect(screen.getByText("Recovered title")).toBeTruthy();
  expect(screen.queryByText("正在读取摘要")).toBeNull();
  expect(screen.queryByText("正在读取历史摘要…")).toBeNull();
});

// The three states are three sentences: still working, working on a search, and
// stopped. A kernel that reports none of them draws nothing at all, which is
// what keeps an older server's folder from being nagged about a read it never
// started.
it("distinguishes an unfinished search, failed summaries, and an old kernel", () => {
  const { rerender } = render(<ListingProgress workspace={pending} searching />);
  expect(screen.getByText("仍在搜索部分历史会话…")).toBeTruthy();

  rerender(<ListingProgress workspace={{ ...pending, listingState: "degraded" }} searching />);
  expect(screen.getByText("部分历史摘要暂不可用，可继续打开会话")).toBeTruthy();
  // Not busy: the read stopped, and saying otherwise leaves it spinning.
  expect(screen.getByRole("status").getAttribute("aria-busy")).toBe("false");

  rerender(<ListingProgress workspace={{ root: "/old", name: "old", sessions: [] }} searching />);
  expect(screen.queryByRole("status")).toBeNull();
});

// Only a stopped read is worth asking again about, and the ask is the retry —
// an ordinary reload would re-read the same failed summaries and fail again.
it("offers the retry on a stopped read, and only when there is one to make", () => {
  const onRetryTree = vi.fn();
  const { rerender } = render(<ListingProgress workspace={{ ...pending, listingState: "degraded" }} searching={false} onRetry={onRetryTree} />);
  fireEvent.click(screen.getByRole("button", { name: "重试" }));
  expect(onRetryTree).toHaveBeenCalledTimes(1);

  rerender(<ListingProgress workspace={pending} searching={false} onRetry={onRetryTree} />);
  expect(screen.queryByRole("button", { name: "重试" })).toBeNull();

  rerender(<ListingProgress workspace={{ ...pending, listingState: "degraded" }} searching={false} />);
  expect(screen.queryByRole("button")).toBeNull();
});

// The count beside a folder is the number a reader would quote, so it appears
// only once it stops moving.
it("quotes a session count only once the count is final", () => {
  const row = { path: "/project/sessions/a.jsonl", name: "a", metadataState: "pending" as const };
  const { rerender } = render(tree({ ...pending, sessions: [row] }));
  expect(screen.queryByText("1 会话")).toBeNull();

  rerender(tree({ ...pending, countsComplete: true, listingState: "ready", sessions: [{ ...row, metadataState: "ready" }] }));
  expect(screen.getByText("1 会话")).toBeTruthy();
});