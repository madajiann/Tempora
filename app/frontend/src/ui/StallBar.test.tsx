// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import "./testkit";
import { RuntimeBar } from "./RuntimeBar";
import type { Stall } from "../state/session_types";

afterEach(cleanup);

const stall = (over: Partial<Stall> = {}): Stall => ({
  cause: "rounds", idleRounds: 20, roundLimit: 20, promptTokens: 0, tokenMultiple: 8, paused: false, ...over,
});

describe("the stall strip beside the composer", () => {
  it("says the count and offers stop or quiet while the run goes on", async () => {
    const onStall = vi.fn();
    render(<RuntimeBar notices={[]} onSeen={() => {}} watch={{ stall: stall() }} onStall={onStall} />);
    expect(screen.getByRole("status").textContent).toContain("已连续 20 轮没有可观察的进展");
    await userEvent.click(screen.getByRole("button", { name: "停止" }));
    await userEvent.click(screen.getByRole("button", { name: "不再提示（本会话）" }));
    expect(onStall.mock.calls.map((c) => c[0])).toEqual(["stop", "mute"]);
  });

  it("offers to go on once the user's own setting paused the run", async () => {
    const onStall = vi.fn();
    render(<RuntimeBar notices={[]} onSeen={() => {}} watch={{ stall: stall({ paused: true, idleRounds: 4 }) }} onStall={onStall} />);
    expect(screen.getByRole("status").textContent).toContain("任务已暂停");
    await userEvent.click(screen.getByRole("button", { name: "继续（计数清零）" }));
    expect(onStall.mock.calls.map((c) => c[0])).toEqual(["continue"]);
  });

  it("says the token backstop when that is what the kernel saw", () => {
    render(<RuntimeBar notices={[]} onSeen={() => {}} watch={{ stall: stall({ cause: "tokens", tokenMultiple: 8, promptTokens: 1234 }) }} onStall={() => {}} />);
    expect(screen.getByRole("status").textContent).toContain("自上次有进展以来已用约 8 倍上下文的输入 token");
  });

  it("says a perseveration stall as perseveration", () => {
    render(<RuntimeBar notices={[]} onSeen={() => {}} watch={{ stall: stall({ cause: "perseveration" }) }} onStall={() => {}} />);
    expect(screen.getByRole("status").textContent).toContain("模型在重复输出同一段文字");
  });
});
