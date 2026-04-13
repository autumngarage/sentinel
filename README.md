# Sentinel

**Autonomous meta-agent for managing software projects.**

Sentinel manages software projects through a continuous loop of goal-setting, state assessment, deep research, planning, and delegated execution across multiple LLM providers. It automates what a technical PM does every day: understand the project, research the best approach, make a plan, and dispatch coding agents to execute it.

## The Vision

Most AI coding tools are reactive — you give them a task, they do it. Sentinel is proactive. It understands your project holistically, identifies what needs doing, researches the best approach, creates a plan, and delegates to coding agents. Then it reviews their work, learns from the results, and starts the next cycle.

The ultimate goal: **Sentinel manages its own development.** Real dogfooding.

## The Loop

Sentinel operates on a five-step cycle that mirrors what a human technical PM does:

```
┌──────────┐
│  1. KNOW  │  What are we trying to achieve?
│   GOALS   │  Project intent, milestones, priorities
└────┬─────┘
     │
     ▼
┌──────────┐
│ 2. ASSESS │  Where are we right now?
│  CURRENT  │  Code state, test health, tech debt,
│   STATE   │  what changed since last cycle
└────┬─────┘
     │
     ▼
┌──────────┐
│3. RESEARCH│  What's the best way forward?
│ EXPERTISE │  Best practices, docs, how others solved
│           │  this, tradeoffs, new tools available
└────┬─────┘
     │
     ▼
┌──────────┐
│ 4. PLAN  │  What specifically should we do?
│          │  Prioritized tasks, acceptance criteria,
│          │  risk assessment, scoped work items
└────┬─────┘
     │
     ▼
┌──────────┐
│5. DELEGATE│  Hand off to coding agents
│          │  Right model for each task, full context,
│          │  verify results, learn from outcomes
└────┬─────┘
     │
     └──────→ (cycle repeats)
```

## The Five Roles

Each step in the loop is powered by a **role** — an LLM configured for a specific job. You assign a provider to each role during setup:

| Role | What It Does | Default | Why |
|------|-------------|---------|-----|
| **Monitor** | Scans codebase, assesses state, detects drift | Local (Ollama) | Runs often — should be free |
| **Researcher** | Deep research, web search, docs, best practices | Gemini 2.5 Pro | Built-in web search, cheap |
| **Planner** | Strategic decisions, task decomposition, prioritization | Claude Opus 4.6 | Best judgment available |
| **Coder** | Writes code, runs tests, executes the plan | Claude Agent SDK | Full agentic coding loop |
| **Reviewer** | Verifies completed work, code review | Gemini 2.5 Pro | Independent from coder |

**The Reviewer should be a different provider than the Coder.** Same model reviewing its own work has the same blind spots.

## Multi-Provider Architecture

Sentinel supports four LLM providers. Every role can use any provider:

| Provider | Models | Strengths | Cost |
|----------|--------|-----------|------|
| **Claude** (Anthropic) | Opus 4.6, Sonnet 4.6, Haiku 4.5 | Best agentic coding, 1M context, Agent SDK | $1-5/MTok input |
| **OpenAI** | GPT-5.4, gpt-5.3-codex, o4-mini | Strong coding, Responses API, Codex SDK | $0.20-2.50/MTok |
| **Gemini** (Google) | 2.5 Pro, 2.5 Flash, Flash Lite | Native web search, cheapest frontier, 1M ctx | $0.10-1.25/MTok |
| **Local** (Ollama) | Qwen 2.5 Coder, DeepSeek R1, etc. | Free, private, offline, no rate limits | $0 |

### Why Multiple Providers?

Different tasks need different models:
- **High-volume scanning** should be cheap → Local or Gemini Flash
- **Deep research** needs web search → Gemini (native grounding) or Claude (web tool)
- **Strategic planning** needs best judgment → Claude Opus
- **Code execution** needs agentic tools → Claude Agent SDK or Codex SDK
- **Independent review** needs a different perspective → different provider than coder

## Deep Research

Sentinel's research capability is a first-class feature, not an afterthought. Before any non-trivial work, the researcher investigates.

### Research Modes

- **Targeted** — "Before implementing X, research how to do it well"
- **Exploratory** — "What should we be thinking about that we're not?"
- **Comparative** — "How does our approach compare to alternatives?"
- **Consensus** — Ask multiple models independently, synthesize disagreements

### Multi-Model Consensus

For important questions, Sentinel queries multiple providers independently:

```
Question
  ├──→ Claude Opus  ──→ Answer A
  ├──→ Gemini Pro   ──→ Answer B
  ├──→ GPT-5.4      ──→ Answer C
  └──→ (optional) Local → Answer D
            │
            ▼
  Synthesis: Where do they agree? Disagree?
  What's the strongest conclusion?
```

When models agree, confidence is high. When they disagree, you've found something worth investigating deeper.

### Inspired by Autoresearch

Sentinel's research loop draws from [Karpathy's autoresearch](https://github.com/karpathy/autoresearch) pattern:
- **Fixed budget per research iteration** — makes results comparable
- **Immutable evaluation criteria** — separate "what we measure" from "what we change"
- **Structured results logging** — data, not prose, so the planner can reason over results
- **Crash recovery** — handle failures gracefully, log and move on, never stop
- **Simplicity-weighted decisions** — a simpler solution that's 95% as good is often preferable

## Setup

```bash
# Install (npm)
npm install -g sentinel

# Initialize in a project
cd your-project
sentinel init
```

### Interactive Setup

`sentinel init` walks you through configuring each role:

```
Sentinel uses 5 AI roles. Let's configure which LLM powers each one.

Available providers:
  claude   - Anthropic (requires ANTHROPIC_API_KEY)
  openai   - OpenAI    (requires OPENAI_API_KEY)
  gemini   - Google    (requires GEMINI_API_KEY)
  local    - Ollama    (free, runs on your machine)

Choose a preset or configure individually:
  ❯ Recommended (Local monitor, cloud for the rest)
    All Claude (simplest, one API key)
    All Local (free, private, offline)
    Budget (minimize cloud spend)
    Custom (pick each role individually)
```

If you choose Local for any role, Sentinel helps you set up Ollama:
- Checks if Ollama is installed (offers to install via brew)
- Detects your hardware (RAM, chip) and recommends models
- Pulls the recommended model
- Verifies it works with a test prompt

### Configuration

Setup creates `.sentinel/config.toml` in your project:

```toml
[project]
name = "my-project"
path = "/Users/you/Repos/my-project"

[goals]
description = "Build a real-time data pipeline"
milestones = ["MVP ingestion", "Dashboard v1", "Alerting"]
priorities = ["Reliability", "Performance", "Cost efficiency"]

[roles.monitor]
provider = "local"
model = "qwen2.5-coder:14b"

[roles.researcher]
provider = "gemini"
model = "gemini-2.5-pro"
web_search = true

[roles.planner]
provider = "claude"
model = "claude-opus-4-6"
thinking = true

[roles.coder]
provider = "claude"
mode = "agent-sdk"
model = "claude-sonnet-4-6"
max_budget_per_task_usd = 2.00

[roles.reviewer]
provider = "gemini"
model = "gemini-2.5-pro"

[budget]
daily_limit_usd = 15.00
```

## CLI Commands

```bash
sentinel init              # Interactive setup
sentinel cycle             # Run one full loop
sentinel watch             # Continuous mode
sentinel scan              # Just assess state
sentinel research [topic]  # Deep research on a topic
sentinel plan              # Assess → research → plan
sentinel status            # Project health dashboard
sentinel goals             # View/update goals
sentinel config            # View/update role config
sentinel providers         # Provider health check
sentinel history           # Past cycle results
sentinel cost              # Token usage & cost tracking
```

## Relationship to Toolkit

Sentinel is complementary to [toolkit](https://github.com/henrymodisett/toolkit):

- **Toolkit** provides the engineering principles, git workflow, scripts, and code review hooks
- **Sentinel** provides the autonomous intelligence layer that drives continuous improvement

Toolkit defines *what good looks like*. Sentinel uses that definition to *make things better*.

Sentinel inherits toolkit's principles via the standard `principles/` directory. When toolkit defines "every fix gets a test," Sentinel's reviewer enforces it.

## Project Status

**v0.1.0 — Foundation.** Project structure, provider abstraction, role definitions, and CLI scaffolding are in place. Core loop and provider implementations are next.

## License

MIT
