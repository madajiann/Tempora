import assert from "node:assert/strict";
import { test } from "node:test";
import { rewriteDragRegions, shellFromEnv } from "./shell-css.mjs";

test("browser build keeps the custom property byte-for-byte", () => {
  const css = ".tabbar{--tempora-draggable:drag}.tabbar *{--tempora-draggable: no-drag}";
  assert.equal(rewriteDragRegions(css, "browser"), css);
});

test("electron build rewrites every drag declaration", () => {
  const css = ".tabbar{--tempora-draggable:drag}.tabbar *{--tempora-draggable: no-drag}/* --tempora-draggable marks */";
  assert.equal(
    rewriteDragRegions(css, "electron"),
    ".tabbar{-webkit-app-region:drag}.tabbar *{-webkit-app-region: no-drag}/* --tempora-draggable marks */",
  );
});

test("shell selection is explicit", () => {
  assert.equal(shellFromEnv({}), "browser");
  assert.equal(shellFromEnv({ TEMPORA_SHELL: "electron" }), "electron");
  assert.throws(() => shellFromEnv({ TEMPORA_SHELL: "wails" }), "the Wails shell is retired");
  assert.throws(() => shellFromEnv({ TEMPORA_SHELL: "tauri" }));
});
