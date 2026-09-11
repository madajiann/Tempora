import assert from "node:assert/strict";
import { join } from "node:path";
import { test } from "node:test";
import { packagedSmokeEnv } from "./smoke-env.mjs";

test("packaged startup uses an isolated home without inherited development or service overrides", () => {
  const parent = {
    PATH: "system-path", DISPLAY: ":99", HOME: "system-home",
    TEMPORA_DEV: "1", Tempora_Dev: "1", TEMPORA_CHANNEL: "dev", TEMPORA_COMMIT: "old",
    TEMPORA_DESKTOP_SERVICE: "old-service", TEMPORA_ELECTRON_DEV_URL: "http://localhost:5173",
    TEMPORA_HOME: "real-user-data", TEMPORA_STATE_HOME: "real-state", TEMPORA_CACHE_HOME: "real-cache",
    NODE_OPTIONS: "--require development-hook", ELECTRON_RUN_AS_NODE: "1",
  };
  assert.deepEqual(packagedSmokeEnv(parent, "fixture"), {
    PATH: "system-path", DISPLAY: ":99", HOME: "system-home",
    TEMPORA_HOME: "fixture", TEMPORA_STATE_HOME: "fixture", TEMPORA_CACHE_HOME: join("fixture", "cache"),
  });
  assert.equal(parent.TEMPORA_DEV, "1", "the caller environment is not mutated");
});
