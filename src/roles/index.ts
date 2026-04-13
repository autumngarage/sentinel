/**
 * Roles — the five agents that power Sentinel's loop.
 *
 * Each role represents a distinct function in the project management loop:
 *
 *   1. Monitor  — ASSESS current state
 *   2. Researcher — RESEARCH expertise to guide next steps
 *   3. Planner  — PLAN prioritized work items
 *   4. Coder    — DELEGATE and execute tasks
 *   5. Reviewer — VERIFY completed work
 *
 * Goals (step 0) are stored in config, not a role — they're the user's
 * intent, not an LLM's output.
 *
 * Each role is configured with a provider (Claude, OpenAI, Gemini, or Local)
 * and a model. The user chooses during `sentinel init`.
 */

export { Monitor } from "./monitor.js";
export { Researcher } from "./researcher.js";
export { Planner } from "./planner.js";
export { Coder } from "./coder.js";
export { Reviewer } from "./reviewer.js";
