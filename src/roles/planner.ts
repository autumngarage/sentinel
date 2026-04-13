/**
 * Planner role — strategic decisions, task decomposition, prioritization.
 *
 * The planner takes the state assessment and research briefs and produces
 * a prioritized backlog of well-scoped work items. Each item has clear
 * acceptance criteria so the coder knows when it's done and the reviewer
 * knows what to check.
 *
 * Default provider: Claude Opus 4.6 (best judgment and reasoning)
 * Recommended model: claude-opus-4-6
 */

import type { Router } from "../providers/router.js";
import type { StateAssessment } from "./monitor.js";
import type { ResearchBrief } from "./researcher.js";
import type { Goals } from "../config/schema.js";

export interface WorkItem {
  id: string;
  title: string;
  description: string;
  type: "feature" | "bugfix" | "refactor" | "test" | "docs" | "chore";
  priority: "critical" | "high" | "medium" | "low";
  estimatedComplexity: 1 | 2 | 3 | 4 | 5; // 1=trivial, 5=major
  files: string[]; // files likely to be touched
  acceptanceCriteria: string[];
  researchBrief?: ResearchBrief; // attached research, if any
  riskAssessment: string;
  blockedBy?: string[]; // IDs of work items that must complete first
}

export interface Plan {
  timestamp: string;
  goals: Goals;
  assessment: StateAssessment;
  backlog: WorkItem[];
  rationale: string; // why these items, in this order
}

export class Planner {
  constructor(private router: Router) {}

  /** Generate a plan from current state and research */
  async plan(
    goals: Goals,
    assessment: StateAssessment,
    research: ResearchBrief[],
  ): Promise<Plan> {
    // TODO: Implement planning
    // 1. Analyze goals vs current state to identify gaps
    // 2. Use research briefs to inform approach
    // 3. Decompose gaps into atomic work items
    // 4. Prioritize by impact × effort × risk
    // 5. Add acceptance criteria to each item
    throw new Error("Not yet implemented");
  }

  /** Re-prioritize an existing backlog based on new information */
  async reprioritize(
    plan: Plan,
    newAssessment: StateAssessment,
  ): Promise<Plan> {
    // TODO: Implement re-prioritization
    throw new Error("Not yet implemented");
  }
}
