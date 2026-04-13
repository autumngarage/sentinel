import { describe, it, expect } from "vitest";
import {
  SentinelConfigSchema,
  RoleNameSchema,
  ProviderNameSchema,
  ROLE_DEFAULTS,
  ROLE_DESCRIPTIONS,
} from "./schema.js";

describe("config schema", () => {
  it("validates role names", () => {
    expect(RoleNameSchema.parse("monitor")).toBe("monitor");
    expect(RoleNameSchema.parse("researcher")).toBe("researcher");
    expect(RoleNameSchema.parse("planner")).toBe("planner");
    expect(RoleNameSchema.parse("coder")).toBe("coder");
    expect(RoleNameSchema.parse("reviewer")).toBe("reviewer");
    expect(() => RoleNameSchema.parse("invalid")).toThrow();
  });

  it("validates provider names", () => {
    expect(ProviderNameSchema.parse("claude")).toBe("claude");
    expect(ProviderNameSchema.parse("openai")).toBe("openai");
    expect(ProviderNameSchema.parse("gemini")).toBe("gemini");
    expect(ProviderNameSchema.parse("local")).toBe("local");
    expect(() => ProviderNameSchema.parse("invalid")).toThrow();
  });

  it("has defaults for all five roles", () => {
    expect(Object.keys(ROLE_DEFAULTS)).toHaveLength(5);
    expect(ROLE_DEFAULTS.monitor.provider).toBe("local");
    expect(ROLE_DEFAULTS.researcher.provider).toBe("gemini");
    expect(ROLE_DEFAULTS.planner.provider).toBe("claude");
    expect(ROLE_DEFAULTS.coder.provider).toBe("claude");
    expect(ROLE_DEFAULTS.reviewer.provider).toBe("gemini");
  });

  it("has descriptions for all five roles", () => {
    expect(Object.keys(ROLE_DESCRIPTIONS)).toHaveLength(5);
    for (const desc of Object.values(ROLE_DESCRIPTIONS)) {
      expect(desc.length).toBeGreaterThan(0);
    }
  });

  it("validates a complete config", () => {
    const config = SentinelConfigSchema.parse({
      project: { name: "test-project", path: "/tmp/test" },
      goals: {
        description: "Build something great",
        milestones: ["MVP"],
        priorities: ["Quality"],
      },
      roles: {
        monitor: { provider: "local", model: "qwen2.5-coder:14b" },
        researcher: { provider: "gemini", model: "gemini-2.5-pro" },
        planner: { provider: "claude", model: "claude-opus-4-6" },
        coder: { provider: "claude", model: "claude-sonnet-4-6" },
        reviewer: { provider: "gemini", model: "gemini-2.5-pro" },
      },
    });
    expect(config.project.name).toBe("test-project");
    expect(config.budget.dailyLimitUsd).toBe(15); // default
  });

  it("rejects invalid provider in role config", () => {
    expect(() =>
      SentinelConfigSchema.parse({
        project: { name: "test", path: "/tmp" },
        roles: {
          monitor: { provider: "invalid", model: "test" },
          researcher: { provider: "gemini", model: "test" },
          planner: { provider: "claude", model: "test" },
          coder: { provider: "claude", model: "test" },
          reviewer: { provider: "gemini", model: "test" },
        },
      }),
    ).toThrow();
  });
});
