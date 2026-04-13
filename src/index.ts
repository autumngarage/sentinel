/**
 * Sentinel — Autonomous Meta-Agent for Software Projects
 *
 * Sentinel manages software projects through a continuous loop:
 *   1. Know Goals    — what are we trying to achieve?
 *   2. Assess State  — where are we right now?
 *   3. Research       — what's the best way forward?
 *   4. Plan          — what specifically should we do?
 *   5. Delegate      — hand off to coding agents, verify results
 *
 * Each step is powered by a configurable LLM provider:
 *   - Monitor    (assess)    → default: Local/Ollama (free, runs often)
 *   - Researcher (research)  → default: Gemini (web search, cheap)
 *   - Planner    (plan)      → default: Claude Opus (best judgment)
 *   - Coder      (delegate)  → default: Claude Agent SDK (agentic coding)
 *   - Reviewer   (verify)    → default: Gemini (independent from coder)
 */

export { Loop } from "./loop/index.js";
export { Router } from "./providers/router.js";
export { Monitor } from "./roles/monitor.js";
export { Researcher } from "./roles/researcher.js";
export { Planner } from "./roles/planner.js";
export { Coder } from "./roles/coder.js";
export { Reviewer } from "./roles/reviewer.js";
export { Memory } from "./memory/index.js";
export type { SentinelConfig, RoleName, ProviderName, Goals } from "./config/schema.js";
