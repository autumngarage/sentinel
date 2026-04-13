# Sentinel — Claude Code Instructions

## Who You Are on This Project

Sentinel is an autonomous meta-agent that manages software projects through a continuous loop of goal-setting, state assessment, research, planning, and delegated execution across multiple LLM providers. Think of it as an AI technical PM — it understands a project holistically, identifies what needs doing, plans the work, dispatches coding agents, and verifies the results.

You are building a tool that automates what Henry does every day: investigate the project, research best approaches, make a plan, and ask AI coding agents to execute. The goal is to take this into any project and hand it off to the meta-agent.

"Good" looks like: clean TypeScript, well-defined provider abstraction, the 5-role architecture working end-to-end, and eventually Sentinel managing its own development (dogfooding).

## Engineering Principles

@principles/engineering-principles.md
@principles/pre-implementation-checklist.md
@principles/audit-weak-points.md
@principles/documentation-ownership.md

## Git Workflow

@principles/git-workflow.md

### The lifecycle (drive this automatically, do not ask the user for permission at each step)

1. **Pull.** `git pull --rebase` on the default branch before starting work.
2. **Branch.** `git checkout -b <type>/<short-description>` where `<type>` is one of `feat`, `fix`, `chore`, `refactor`, `docs`.
3. **Change + commit.** Make the code change, stage explicit file paths, commit with a concise message.
4. **Ship.** `bash scripts/open-pr.sh --auto-merge` — pushes, creates the PR, runs Codex review, squash-merges, and syncs the default branch in one step.
5. **Clean up.** `git branch -D <feature-branch>` if it still exists locally.

### Housekeeping

- Concise commit messages. Logically grouped changes.
- Run `/compact` at ~50% context. Start fresh sessions for unrelated work.

## Testing

```bash
# Reinstall dependencies without rerunning the full machine setup
bash setup.sh --deps-only

# Before any push — uses .toolkit-config profile defaults and command overrides
bash scripts/toolkit-run.sh validate

# Run tests directly
uv run pytest

# Lint
uv run ruff check src/ tests/

# Auto-fix lint issues
uv run ruff check --fix src/ tests/
```

Fix failing tests before pushing.

## Release & Distribution

Not yet established. Planned: PyPI package (`sentinel`) + Homebrew formula (following the toolkit pattern). The release process will mirror toolkit's: version bump, tag, push, GitHub release, formula update.

## Architecture

### The Five-Step Loop

Sentinel's core is a continuous cycle that mirrors what a human technical PM does:

```
1. KNOW GOALS    → Read project goals from config
2. ASSESS STATE  → Monitor role scans the codebase
3. RESEARCH      → Researcher role investigates best approaches
4. PLAN          → Planner role creates prioritized backlog
5. DELEGATE      → Coder role executes, Reviewer role verifies
```

### The Five Roles

Each role is assigned a configurable LLM provider during `sentinel init`:

| Role | Purpose | Default Provider | Why |
|------|---------|-----------------|-----|
| Monitor | Scans codebase, assesses state | Local (Ollama) | Runs often, should be free |
| Researcher | Deep research, web search | Gemini 2.5 Pro | Built-in web search grounding |
| Planner | Strategic decisions, task decomposition | Claude Opus 4.6 | Best judgment and reasoning |
| Coder | Writes code, executes tasks | Claude Agent SDK | Full agentic coding loop |
| Reviewer | Verifies completed work | Gemini 2.5 Pro | Independent from coder |

### Package Structure

```
src/sentinel/
├── cli/          CLI entrypoint (click)
├── config/       Pydantic schemas for .sentinel/config.toml
├── providers/    Unified LLM provider abstraction
│   ├── interface.py   Common types (Provider, ChatResponse, etc.)
│   ├── claude.py      Anthropic SDK + Agent SDK
│   ├── openai.py      OpenAI Responses API + Codex SDK
│   ├── gemini.py      Google GenAI SDK
│   ├── local.py       Ollama via OpenAI-compatible API
│   └── router.py      Role → provider routing
├── roles/        The five agent roles
│   ├── monitor.py     State assessment
│   ├── researcher.py  Deep research + multi-model consensus
│   ├── planner.py     Task decomposition + prioritization
│   ├── coder.py       Code execution
│   └── reviewer.py    Independent code review
├── loop/         The core cycle orchestrator
├── research/     Extended research engine
└── memory/       Persistent project knowledge
```

### Provider Abstraction

All providers implement a common `Provider` interface with `chat()`, optional `research()` (web search), and optional `code()` (agentic execution). The `Router` maps roles to providers based on config. Local models use the OpenAI SDK pointed at Ollama's compatible API.

### Multi-Model Consensus (Research)

For important research questions, Sentinel can query multiple providers independently and synthesize their responses. Agreements = high confidence. Disagreements = worth investigating deeper.

## Key Files

| File | Purpose |
|------|---------|
| `src/sentinel/providers/interface.py` | The core Provider type that all LLM integrations implement |
| `src/sentinel/providers/router.py` | Maps roles to providers based on project config |
| `src/sentinel/config/schema.py` | Pydantic schemas defining .sentinel/config.toml shape |
| `src/sentinel/loop/cycle.py` | The five-step cycle orchestrator |
| `src/sentinel/roles/*.py` | Individual role implementations |
| `src/sentinel/cli/main.py` | CLI entrypoint and command definitions |

## State & Config

- **Project config**: `.sentinel/config.toml` in the target project (created by `sentinel init`)
- **Memory**: `.sentinel/memory/` directory (markdown files with YAML frontmatter)
- **Backlog**: `.sentinel/backlog/` directory (generated work items)
- **Reports**: `.sentinel/reports/` directory (health snapshots over time)
- **Gitignored**: `node_modules/`, `dist/`, `.sentinel/memory/` (project-specific, not committed)

## Hard-Won Lessons

(None yet — project is brand new. This section will grow as we encounter and resolve real issues.)
