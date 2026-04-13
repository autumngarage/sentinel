/**
 * Coder role — executes work items by writing code.
 *
 * The coder receives a well-scoped work item from the planner and
 * executes it. Depending on the provider, this may use:
 * - Claude Agent SDK (full Claude Code agentic loop)
 * - Codex SDK (OpenAI's agentic coding)
 * - Direct API (generate code, apply with simple file writes)
 * - Local model (generate code, apply with simple file writes)
 *
 * Default provider: Claude Agent SDK (full agentic loop)
 * Recommended model: claude-sonnet-4-6
 */

import type { Router } from "../providers/router.js";
import type { WorkItem } from "./planner.js";

export interface ExecutionResult {
  workItemId: string;
  status: "success" | "partial" | "failed";
  filesChanged: string[];
  testsRun: boolean;
  testsPassing: boolean;
  commitSha?: string;
  error?: string;
  usage: {
    inputTokens: number;
    outputTokens: number;
    costUsd: number;
    durationMs: number;
  };
}

export class Coder {
  constructor(private router: Router) {}

  /** Execute a work item */
  async execute(
    workItem: WorkItem,
    projectPath: string,
  ): Promise<ExecutionResult> {
    // TODO: Implement code execution
    // 1. Build a detailed prompt from the work item
    //    - Include description, acceptance criteria, relevant files
    //    - Include any attached research brief
    // 2. Dispatch to the coder provider
    //    - If agent-sdk: use Claude Code subprocess
    //    - If codex: use Codex SDK
    //    - If api/local: generate code and apply file changes
    // 3. Run tests to verify
    // 4. Collect results
    throw new Error("Not yet implemented");
  }
}
