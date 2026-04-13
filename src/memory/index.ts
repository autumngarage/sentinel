/**
 * Memory — persistent project knowledge across Sentinel sessions.
 *
 * Sentinel needs to remember what it learned about a project across
 * sessions. This is NOT the same as chat history — it's structured
 * knowledge about the project that evolves over time.
 *
 * What gets persisted:
 * - State assessments (health snapshots over time)
 * - Research briefs (what we learned and when)
 * - Plan history (what we planned and what happened)
 * - Execution results (what worked, what failed, why)
 * - Lessons learned (patterns that emerged from past cycles)
 *
 * Storage: .sentinel/memory/ directory in the project
 * Format: Markdown files with YAML frontmatter (human-readable, git-trackable)
 */

export interface MemoryEntry {
  id: string;
  type: "assessment" | "research" | "plan" | "execution" | "lesson";
  timestamp: string;
  title: string;
  content: string;
  tags: string[];
}

export class Memory {
  private memoryDir: string;

  constructor(projectPath: string) {
    this.memoryDir = `${projectPath}/.sentinel/memory`;
  }

  async save(entry: MemoryEntry): Promise<void> {
    // TODO: Write entry as markdown file with frontmatter
    throw new Error("Not yet implemented");
  }

  async load(id: string): Promise<MemoryEntry | null> {
    // TODO: Read and parse a memory entry
    throw new Error("Not yet implemented");
  }

  async search(query: string, type?: MemoryEntry["type"]): Promise<MemoryEntry[]> {
    // TODO: Search memory entries by content and type
    throw new Error("Not yet implemented");
  }

  async recent(count: number, type?: MemoryEntry["type"]): Promise<MemoryEntry[]> {
    // TODO: Get most recent entries
    throw new Error("Not yet implemented");
  }
}
