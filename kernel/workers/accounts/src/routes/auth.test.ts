import { describe, expect, it } from "vitest";
import { verifyLink } from "./auth";

describe("verifyLink", () => {
  it("uses the configured account origin instead of the web app origin", () => {
    expect(verifyLink("https://id.tempora.io", "test-token")).toBe(
      "https://id.tempora.io/auth/verify?token=test-token",
    );
  });

  it("normalizes a trailing slash and encodes the token", () => {
    expect(verifyLink("https://id.tempora.io/", "token+/=?")).toBe(
      "https://id.tempora.io/auth/verify?token=token%2B%2F%3D%3F",
    );
  });
});
