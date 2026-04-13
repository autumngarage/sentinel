/**
 * Researcher role — deep research to guide the next step.
 *
 * This is the "brain" that ensures Sentinel makes informed decisions.
 * Before any non-trivial work, the researcher investigates best practices,
 * reads documentation, and evaluates alternatives.
 *
 * Research modes:
 * - Targeted: "Before implementing X, research how to do it well"
 * - Exploratory: "What should we be thinking about that we're not?"
 * - Comparative: "How does our approach compare to alternatives?"
 * - Consensus: Ask multiple models independently, synthesize disagreements
 *
 * Default provider: Gemini (built-in Google Search grounding, 1M context)
 * Recommended model: gemini-2.5-pro
 */

import type { Router } from "../providers/router.js";
import type { StateAssessment } from "./monitor.js";

export interface ResearchBrief {
  question: string;
  mode: "targeted" | "exploratory" | "comparative" | "consensus";
  findings: ResearchFinding[];
  synthesis: string;
  confidence: "low" | "medium" | "high";
  sources: string[];
  timestamp: string;
}

export interface ResearchFinding {
  source: string;
  summary: string;
  relevance: "low" | "medium" | "high";
  model?: string; // which model produced this finding (for consensus mode)
}

export interface ConsensusResult {
  agreements: string[];
  disagreements: string[];
  synthesis: string;
  modelResponses: Map<string, string>;
}

export class Researcher {
  constructor(private router: Router) {}

  /** Targeted research — investigate a specific topic before acting */
  async targeted(question: string, context?: string): Promise<ResearchBrief> {
    // TODO: Implement targeted research
    // 1. Formulate search queries from the question
    // 2. Use researcher provider's web search capability
    // 3. Synthesize findings into actionable brief
    throw new Error("Not yet implemented");
  }

  /** Exploratory research — discover what we should be thinking about */
  async exploratory(assessment: StateAssessment): Promise<ResearchBrief> {
    // TODO: Implement exploratory research
    // 1. Analyze current state for areas of improvement
    // 2. Search for ecosystem updates relevant to dependencies
    // 3. Check for new patterns/tools that could help
    throw new Error("Not yet implemented");
  }

  /** Comparative research — evaluate alternatives */
  async comparative(
    topic: string,
    alternatives: string[],
  ): Promise<ResearchBrief> {
    // TODO: Implement comparative research
    // 1. Research each alternative
    // 2. Compare against current approach
    // 3. Produce tradeoff analysis
    throw new Error("Not yet implemented");
  }

  /** Multi-model consensus — ask multiple providers, synthesize */
  async consensus(question: string): Promise<ConsensusResult> {
    // TODO: Implement multi-model consensus
    // 1. Send the same question to all available providers in parallel
    // 2. Collect independent responses
    // 3. Use the planner model to synthesize agreements/disagreements
    // 4. Rate confidence based on degree of agreement
    throw new Error("Not yet implemented");
  }
}
