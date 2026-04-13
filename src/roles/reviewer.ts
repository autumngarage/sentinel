/**
 * Reviewer role — verifies completed work against acceptance criteria.
 *
 * The reviewer checks the coder's output independently. By default, it
 * uses a DIFFERENT provider than the coder — this prevents the same
 * model from reviewing its own work (same blind spots).
 *
 * Default provider: Gemini (independent from Claude coder)
 * Recommended model: gemini-2.5-pro
 */

import type { Router } from "../providers/router.js";
import type { WorkItem } from "./planner.js";
import type { ExecutionResult } from "./coder.js";

export interface ReviewResult {
  workItemId: string;
  verdict: "approved" | "changes-requested" | "rejected";
  blockingIssues: ReviewIssue[];
  observations: string[];
  acceptanceCriteriaMet: Map<string, boolean>;
}

export interface ReviewIssue {
  file: string;
  line?: number;
  severity: "blocking" | "warning";
  description: string;
  suggestedFix?: string;
}

export class Reviewer {
  constructor(private router: Router) {}

  /** Review completed work against acceptance criteria */
  async review(
    workItem: WorkItem,
    executionResult: ExecutionResult,
    projectPath: string,
  ): Promise<ReviewResult> {
    // TODO: Implement review
    // 1. Read the diff of changed files
    // 2. Check each acceptance criterion
    // 3. Look for common issues (security, silent failures, missing tests)
    // 4. Produce structured review result
    throw new Error("Not yet implemented");
  }
}
