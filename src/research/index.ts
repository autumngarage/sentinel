/**
 * Research engine — deep research capabilities for Sentinel.
 *
 * This module extends the Researcher role with specialized research
 * patterns. It's the component that makes Sentinel think like a
 * staff engineer who does their homework before writing code.
 *
 * Research patterns:
 * - Web search and synthesis
 * - Documentation analysis (long-context ingestion)
 * - Multi-model consensus (independent answers → synthesis)
 * - Codebase-aware research (understands the project when searching)
 * - Research caching (avoid re-researching the same topic)
 *
 * Inspired by Karpathy's autoresearch — the idea that research itself
 * can be automated through iterative search → read → synthesize loops.
 */

export { Researcher } from "../roles/researcher.js";
