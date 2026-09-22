// Run: node node_modules/tsx/dist/cli.mjs src/__tests__/updater-startup-quiet.test.tsx
//
// Regression guard for the cold-boot banner sequence.
//
// Bug: on startup the automatic check ran with the same error handling as an
// explicit user check. A transient failure in the first seconds of boot (the
// manifest fetch racing the desktop bridge, a 15s HTTP timeout, a flaky
// network) painted a red "update failed" banner; the next refresh then
// succeeded and flipped to the "update available" banner. Users saw
// "error, then update" instead of just the update prompt.
//
// Contract now: the AUTOMATIC path (refresh) stays silent on a transient
// failure, while an EXPLICIT path (check from Settings) still surfaces it.

import assert from "node:assert/strict";
import { JSDOM } from "jsdom";
import React, { act, useEffect } from "react";
import { createRoot } from "react-dom/client";
import { UpdateBanner } from "../components/UpdateBanner";
import { LocaleProvider } from "../lib/i18n";
import {
  __resetUpdaterCheckScheduleForTests,
  UpdaterProvider,
  useUpdater,
  type Updater,
} from "../lib/useUpdater";
import { installDesktopHostStub } from "./desktopHostStub";

const dom = new JSDOM("<!doctype html><div id='root'></div>", { url: "http://localhost", pretendToBeVisual: true });
Object.assign(globalThis, {
  window: dom.window,
  document: dom.window.document,
  Node: dom.window.Node,
  Element: dom.window.Element,
  HTMLElement: dom.window.HTMLElement,
  Event: dom.window.Event,
  MouseEvent: dom.window.MouseEvent,
  IS_REACT_ACT_ENVIRONMENT: true,
});

const baseInfo = {
  available: false,
  current: "v0.1.3",
  latest: "v0.1.4",
  notes: "",
  channel: "stable",
  canSelfUpdate: true,
  manualOnly: false,
  installMode: "portable",
  requiresElevation: false,
  downloaded: false,
  downloadUrl: "https://example.invalid/download",
  assetSize: 0,
};

/** A boot-time transient failure: manifest fetch could not complete. */
async function transientFailure() {
  return { ...baseInfo, available: false, err: "fetch manifest: dial tcp: i/o timeout" };
}

const holder: { updater: Updater | null } = { updater: null };

function Probe() {
  const updater = useUpdater();
  useEffect(() => { holder.updater = updater; }, [updater]);
  return (
    <>
      <output id="status">{updater.status.kind}</output>
      <button id="explicit-check" type="button" onClick={() => void updater.check()}>Check</button>
      <UpdateBanner onShowReleaseNotes={() => {}} />
    </>
  );
}

async function flush() {
  await new Promise((resolve) => setTimeout(resolve, 0));
}

const root = createRoot(document.getElementById("root")!);
let failures = 0;
function check(label: string, condition: boolean) {
  if (condition) {
    process.stdout.write(`  PASS  ${label}\n`);
  } else {
    process.stdout.write(`  FAIL  ${label}\n`);
    failures += 1;
  }
}

try {
  // ---- Case 1: automatic check hits a transient failure -> no red banner ----
  __resetUpdaterCheckScheduleForTests();
  installDesktopHostStub({ CheckUpdate: transientFailure });

  await act(async () => {
    root.render(
      <LocaleProvider>
        <UpdaterProvider>
          <Probe />
        </UpdaterProvider>
      </LocaleProvider>,
    );
  });

  await act(async () => {
    await holder.updater!.refresh();
    await flush();
  });

  check(
    "automatic check with a transient failure does not enter the error state",
    holder.updater!.status.kind !== "error",
  );
  check(
    "automatic check with a transient failure renders no error banner",
    document.querySelector(".banner--error") === null,
  );

  // ---- Case 2: the retry succeeds -> the update banner appears, calmly ----
  installDesktopHostStub({
    CheckUpdate: async () => ({ ...baseInfo, available: true, latest: "v0.1.4" }),
  });
  await act(async () => {
    await holder.updater!.check();
    await flush();
  });
  check("a later successful check reports the update as available", holder.updater!.status.kind === "available");
  check("the update banner renders after the quiet failure", document.querySelector(".banner--update") !== null);
  check("still no error banner once the update is available", document.querySelector(".banner--error") === null);

  // ---- Case 3: an EXPLICIT check still surfaces a real error ----
  installDesktopHostStub({ CheckUpdate: transientFailure });
  await act(async () => {
    (document.getElementById("explicit-check") as HTMLButtonElement).click();
    await flush();
  });
  check(
    "an explicit user check still surfaces the error",
    holder.updater!.status.kind === "error",
  );
  check(
    "an explicit failure still renders the error banner",
    document.querySelector(".banner--error") !== null,
  );
} finally {
  await act(async () => { root.unmount(); });
}

process.stdout.write(failures === 0 ? "\nALL PASS updater-startup-quiet\n" : `\n${failures} failed\n`);
if (failures > 0) process.exit(1);
