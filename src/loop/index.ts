/**
 * The Loop — Sentinel's core execution cycle.
 *
 * The loop implements the five-step cycle that mirrors what a human
 * technical PM does every day:
 *
 *   1. KNOW GOALS    — Read project goals from config
 *   2. ASSESS STATE  — Monitor scans the codebase
 *   3. RESEARCH      — Researcher investigates best approaches
 *   4. PLAN          — Planner creates prioritized backlog
 *   5. DELEGATE      — Coder executes, Reviewer verifies
 *
 * The loop can run in different cadences:
 *   - Single cycle: `sentinel cycle`
 *   - Continuous: `sentinel watch` (re-runs after each delegation)
 *   - Scheduled: via cron or Claude Code scheduled tasks
 *   - Triggered: on git push, PR merge, issue creation
 *
 * The ultimate dogfooding goal: Sentinel manages its own development.
 */

import type { SentinelConfig, Goals } from "../config/schema.js";
import type { Router } from "../providers/router.js";
import type { StateAssessment } from "../roles/monitor.js";
import type { ResearchBrief } from "../roles/researcher.js";
import type { Plan, WorkItem } from "../roles/planner.js";
import type { ExecutionResult } from "../roles/coder.js";
import type { ReviewResult } from "../roles/reviewer.js";
import { Monitor } from "../roles/monitor.js";
import { Researcher } from "../roles/researcher.js";
import { Planner } from "../roles/planner.js";
import { Coder } from "../roles/coder.js";
import { Reviewer } from "../roles/reviewer.js";

export interface CycleResult {
  timestamp: string;
  assessment: StateAssessment;
  researchBriefs: ResearchBrief[];
  plan: Plan;
  executions: ExecutionResult[];
  reviews: ReviewResult[];
  totalCostUsd: number;
  durationMs: number;
}

export class Loop {
  private monitor: Monitor;
  private researcher: Researcher;
  private planner: Planner;
  private coder: Coder;
  private reviewer: Reviewer;

  constructor(
    private config: SentinelConfig,
    private router: Router,
  ) {
    this.monitor = new Monitor(router);
    this.researcher = new Researcher(router);
    this.planner = new Planner(router);
    this.coder = new Coder(router);
    this.reviewer = new Reviewer(router);
  }

  /** Run one full cycle of the loop */
  async cycle(): Promise<CycleResult> {
    const start = Date.now();
    const goals = this.config.goals;
    if (!goals) {
      throw new Error(
        "No goals configured. Run `sentinel goals` to set project goals.",
      );
    }

    // Step 1: KNOW GOALS — already in config
    console.log("[sentinel] Step 1/5: Goals loaded");

    // Step 2: ASSESS STATE
    console.log("[sentinel] Step 2/5: Assessing current state...");
    const assessment = await this.monitor.assess(this.config.project.path);

    // Step 3: RESEARCH
    console.log("[sentinel] Step 3/5: Researching...");
    const researchBriefs = await this.researchPhase(goals, assessment);

    // Step 4: PLAN
    console.log("[sentinel] Step 4/5: Planning...");
    const plan = await this.planner.plan(goals, assessment, researchBriefs);

    // Step 5: DELEGATE
    console.log("[sentinel] Step 5/5: Executing plan...");
    const { executions, reviews } = await this.executePhase(plan);

    const result: CycleResult = {
      timestamp: new Date().toISOString(),
      assessment,
      researchBriefs,
      plan,
      executions,
      reviews,
      totalCostUsd: this.calculateCost(executions),
      durationMs: Date.now() - start,
    };

    return result;
  }

  private async researchPhase(
    goals: Goals,
    assessment: StateAssessment,
  ): Promise<ResearchBrief[]> {
    // TODO: Determine what needs researching based on goals + state
    // - If there are new areas to work on, do targeted research
    // - Periodically do exploratory research
    // - For major decisions, do multi-model consensus
    return [];
  }

  private async executePhase(
    plan: Plan,
  ): Promise<{ executions: ExecutionResult[]; reviews: ReviewResult[] }> {
    const executions: ExecutionResult[] = [];
    const reviews: ReviewResult[] = [];

    // Execute top priority items (respecting budget)
    for (const item of plan.backlog.slice(0, 3)) {
      // Limit per cycle
      const result = await this.coder.execute(item, this.config.project.path);
      executions.push(result);

      if (result.status === "success") {
        const review = await this.reviewer.review(
          item,
          result,
          this.config.project.path,
        );
        reviews.push(review);
      }
    }

    return { executions, reviews };
  }

  private calculateCost(executions: ExecutionResult[]): number {
    return executions.reduce((sum, e) => sum + e.usage.costUsd, 0);
  }
}
