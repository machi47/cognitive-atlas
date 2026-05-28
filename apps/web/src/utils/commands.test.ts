import { describe, expect, it } from "vitest";
import { modeForCommand, parseCommand } from "./commands";

describe("commands", () => {
  it("parses slash commands", () => {
    expect(parseCommand("/research analog compute")).toEqual({ command: "research", content: "analog compute" });
  });

  it("routes command modes", () => {
    expect(modeForCommand("deepen", "discuss")).toBe("deep");
    expect(modeForCommand(null, "discuss")).toBe("discuss");
  });
});

