#!/usr/bin/env node

/**
 * Sentinel CLI — the command-line interface for the meta-agent.
 *
 * Commands:
 *   sentinel init          Interactive setup — configure roles, providers, goals
 *   sentinel cycle         Run one full loop cycle
 *   sentinel watch         Continuous mode — loop on a schedule
 *   sentinel scan          Run just the monitor (assess state)
 *   sentinel research      Run just the researcher on a topic
 *   sentinel plan          Run monitor + researcher + planner
 *   sentinel status        Show current project health and backlog
 *   sentinel goals         View or update project goals
 *   sentinel config        View or update role configuration
 *   sentinel providers     Show provider health and capabilities
 *   sentinel history       Show past cycle results
 *   sentinel cost          Show token usage and cost tracking
 */

import { Command } from "commander";

const program = new Command();

program
  .name("sentinel")
  .description(
    "Autonomous meta-agent for managing software projects across multiple LLM providers",
  )
  .version("0.1.0");

program
  .command("init")
  .description("Initialize Sentinel in the current project")
  .action(async () => {
    // TODO: Interactive setup flow
    // 1. Detect project type and structure
    // 2. Ask user to configure each role (provider + model)
    // 3. Ask for project goals
    // 4. Set up .sentinel/ directory
    // 5. If local provider selected, help set up Ollama
    console.log("sentinel init — not yet implemented");
  });

program
  .command("cycle")
  .description("Run one full loop cycle: assess → research → plan → execute → review")
  .action(async () => {
    console.log("sentinel cycle — not yet implemented");
  });

program
  .command("watch")
  .description("Continuous mode — run the loop on a schedule")
  .action(async () => {
    console.log("sentinel watch — not yet implemented");
  });

program
  .command("scan")
  .description("Run just the monitor — assess current project state")
  .action(async () => {
    console.log("sentinel scan — not yet implemented");
  });

program
  .command("research [topic]")
  .description("Run deep research on a topic")
  .option("--mode <mode>", "Research mode: targeted, exploratory, comparative, consensus", "targeted")
  .action(async (topic: string | undefined, options: { mode: string }) => {
    console.log(`sentinel research — not yet implemented (topic: ${topic}, mode: ${options.mode})`);
  });

program
  .command("plan")
  .description("Run monitor + researcher + planner to generate a backlog")
  .action(async () => {
    console.log("sentinel plan — not yet implemented");
  });

program
  .command("status")
  .description("Show current project health and backlog")
  .action(async () => {
    console.log("sentinel status — not yet implemented");
  });

program
  .command("goals")
  .description("View or update project goals")
  .action(async () => {
    console.log("sentinel goals — not yet implemented");
  });

program
  .command("config")
  .description("View or update role configuration")
  .action(async () => {
    console.log("sentinel config — not yet implemented");
  });

program
  .command("providers")
  .description("Show provider health and capabilities")
  .action(async () => {
    console.log("sentinel providers — not yet implemented");
  });

program.parse();
