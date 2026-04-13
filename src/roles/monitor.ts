/**
 * Monitor role — continuously scans the codebase and assesses current state.
 *
 * This is the "eyes" of Sentinel. It runs frequently (on-change, hourly,
 * or on-demand) and produces a state assessment that feeds the rest of the loop.
 *
 * What it scans:
 * - Git status: uncommitted changes, branch state, recent commits
 * - Code quality: complexity hotspots, duplication, dead code
 * - Test coverage: gaps, failing tests, missing edge cases
 * - Dependency health: outdated deps, known CVEs, license issues
 * - Architectural drift: deviations from stated patterns in CLAUDE.md
 * - Open issues: GitHub issues, TODOs in code
 *
 * Default provider: Local (free, runs continuously)
 * Recommended model: qwen2.5-coder:14b
 */

import type { Router } from "../providers/router.js";

export interface StateAssessment {
  timestamp: string;
  gitStatus: {
    branch: string;
    uncommittedChanges: number;
    recentCommits: string[];
    aheadOfRemote: number;
  };
  codeHealth: {
    issues: StateIssue[];
    score: number; // 0-100
  };
  testHealth: {
    passing: number;
    failing: number;
    coverage?: number;
  };
  dependencyHealth: {
    outdated: string[];
    vulnerabilities: string[];
  };
  changedSinceLastScan: string[];
}

export interface StateIssue {
  type: "quality" | "test" | "dependency" | "architecture" | "todo";
  severity: "low" | "medium" | "high" | "critical";
  file?: string;
  line?: number;
  description: string;
}

export class Monitor {
  constructor(private router: Router) {}

  async assess(projectPath: string): Promise<StateAssessment> {
    // TODO: Implement state assessment
    // 1. Run git commands to get repo state
    // 2. Ask the monitor LLM to analyze code quality
    // 3. Run tests and collect results
    // 4. Check dependencies
    // 5. Compare against previous scan
    throw new Error("Not yet implemented");
  }
}
