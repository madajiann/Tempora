// @vitest-environment jsdom
import { afterEach, expect, it, vi } from "vitest";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import "./testkit";
import type { ProviderEntry } from "../port/port";
import type { Port } from "./Providers";
import { EditConn } from "./EditConn";

afterEach(cleanup);

const relay = (over: Partial<ProviderEntry> = {}): ProviderEntry => ({
  name: "relay", kind: "openai", baseUrl: "https://relay.invalid/v1",
  models: ["big", "small"], default: "big", hasKey: true, inUse: false, preset: false,
  supportedEfforts: ["low", "high"], defaultEffort: "low",
  inheritedEfforts: { big: { supportedEfforts: ["low", "high"] }, small: { supportedEfforts: ["low", "high"] } },
  ...over,
});

const mount = (entry: ProviderEntry, editProvider = vi.fn(async () => {})) => {
  render(<EditConn entry={entry} port={{ editProvider } as unknown as Port} busy="" setBusy={() => {}} onDone={() => {}} declare />);
  return editProvider;
};

it("shows the inherited ladder as a placeholder and never sends it as an override", async () => {
  const editProvider = mount(relay());
  const levels = screen.getByRole("textbox", { name: "small 的推理档位" }) as HTMLInputElement;
  expect(levels.value).toBe("");
  expect(levels.placeholder).toBe("继承 low, high");
  await userEvent.click(screen.getByRole("button", { name: "保存" }));
  await waitFor(() => expect(editProvider).toHaveBeenCalled());
  expect(editProvider).toHaveBeenCalledWith(expect.objectContaining({ modelEfforts: {} }));
});

it("sends one model's own ladder, normalised and de-duplicated", async () => {
  const editProvider = mount(relay());
  await userEvent.type(screen.getByRole("textbox", { name: "small 的推理档位" }), "XHigh, high");
  await userEvent.click(screen.getByRole("button", { name: "保存" }));
  await waitFor(() => expect(editProvider).toHaveBeenCalled());
  expect(editProvider).toHaveBeenCalledWith(expect.objectContaining({
    modelEfforts: { small: { supportedEfforts: ["xhigh", "high"] } },
  }));
});

it("sends the per-model default only when it names one of that model's levels", async () => {
  const editProvider = mount(relay({ modelEfforts: { small: { supportedEfforts: ["low", "high"], defaultEffort: "high" } } }));
  expect((screen.getByRole("combobox", { name: "small 的默认档位" }) as HTMLSelectElement).value).toBe("high");
  await userEvent.click(screen.getByRole("button", { name: "保存" }));
  await waitFor(() => expect(editProvider).toHaveBeenCalled());
  expect(editProvider).toHaveBeenCalledWith(expect.objectContaining({
    modelEfforts: { small: { supportedEfforts: ["low", "high"], defaultEffort: "high" } },
  }));
});

it("clearing a stored ladder sends the model without one, so it inherits again", async () => {
  const editProvider = mount(relay({ modelEfforts: { small: { supportedEfforts: ["xhigh"] } } }));
  const levels = screen.getByRole("textbox", { name: "small 的推理档位" }) as HTMLInputElement;
  expect(levels.value).toBe("xhigh");
  await userEvent.clear(levels);
  await userEvent.click(screen.getByRole("button", { name: "保存" }));
  await waitFor(() => expect(editProvider).toHaveBeenCalled());
  expect(editProvider).toHaveBeenCalledWith(expect.objectContaining({ modelEfforts: {} }));
});
