/**
 * Configuration schema — defines the shape of .sentinel/config.toml
 *
 * Uses Zod for runtime validation so we can give clear error messages
 * when config is malformed.
 */

import { z } from "zod";

export const ProviderNameSchema = z.enum(["claude", "openai", "gemini", "local"]);
export type ProviderName = z.infer<typeof ProviderNameSchema>;

export const RoleNameSchema = z.enum([
  "monitor",
  "researcher",
  "planner",
  "coder",
  "reviewer",
]);
export type RoleName = z.infer<typeof RoleNameSchema>;

export const ROLE_DESCRIPTIONS: Record<RoleName, string> = {
  monitor:
    "Scans your codebase continuously. Detects drift, tracks changes, assesses state. Runs often — should be cheap.",
  researcher:
    "Deep research, web search, reads docs and papers. Evaluates alternatives and best practices. Needs web access and long context.",
  planner:
    "Makes strategic decisions. Prioritizes work, decomposes tasks, sets architecture direction. Needs the best judgment available.",
  coder:
    "Writes code, runs tests, executes the plan. Needs agentic tool use (file editing, terminal, self-correction).",
  reviewer:
    "Verifies completed work. Code review, acceptance criteria checks. Should ideally be a different provider than coder for independence.",
};

export const ROLE_DEFAULTS: Record<RoleName, { provider: ProviderName; model: string }> = {
  monitor: { provider: "local", model: "qwen2.5-coder:14b" },
  researcher: { provider: "gemini", model: "gemini-2.5-pro" },
  planner: { provider: "claude", model: "claude-opus-4-6" },
  coder: { provider: "claude", model: "claude-sonnet-4-6" },
  reviewer: { provider: "gemini", model: "gemini-2.5-pro" },
};

export const RoleConfigSchema = z.object({
  provider: ProviderNameSchema,
  model: z.string(),
  endpoint: z.string().optional(),
  webSearch: z.boolean().optional(),
  thinking: z.boolean().optional(),
  maxContext: z.number().optional(),
  mode: z.enum(["agent-sdk", "api", "local"]).optional(),
  maxBudgetPerTaskUsd: z.number().optional(),
  schedule: z.enum(["on-change", "hourly", "daily", "manual"]).optional(),
});
export type RoleConfig = z.infer<typeof RoleConfigSchema>;

export const BudgetConfigSchema = z.object({
  dailyLimitUsd: z.number().default(15),
  warnAtUsd: z.number().default(10),
  trackLocalTokens: z.boolean().default(true),
});
export type BudgetConfig = z.infer<typeof BudgetConfigSchema>;

export const LocalConfigSchema = z.object({
  ollamaEndpoint: z.string().default("http://localhost:11434"),
  modelsPulled: z.array(z.string()).default([]),
  autoStartOllama: z.boolean().default(true),
});
export type LocalConfig = z.infer<typeof LocalConfigSchema>;

export const GoalsSchema = z.object({
  description: z.string(),
  milestones: z.array(z.string()).default([]),
  constraints: z.array(z.string()).default([]),
  priorities: z.array(z.string()).default([]),
});
export type Goals = z.infer<typeof GoalsSchema>;

export const SentinelConfigSchema = z.object({
  project: z.object({
    name: z.string(),
    path: z.string(),
  }),
  goals: GoalsSchema.optional(),
  roles: z.object({
    monitor: RoleConfigSchema,
    researcher: RoleConfigSchema,
    planner: RoleConfigSchema,
    coder: RoleConfigSchema,
    reviewer: RoleConfigSchema,
  }),
  budget: BudgetConfigSchema.default({}),
  local: LocalConfigSchema.default({}),
  research: z
    .object({
      multiModelConsensus: z.boolean().default(false),
      maxSourcesPerQuery: z.number().default(10),
      cacheTtlMinutes: z.number().default(60),
    })
    .default({}),
});
export type SentinelConfig = z.infer<typeof SentinelConfigSchema>;
