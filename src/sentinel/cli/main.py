"""
Sentinel CLI — the command-line interface for the meta-agent.

Commands:
  sentinel init          Interactive setup — configure roles, providers, goals
  sentinel cycle         Run one full loop cycle
  sentinel watch         Continuous mode — loop on a schedule
  sentinel scan          Run just the monitor (assess state)
  sentinel research      Run just the researcher on a topic
  sentinel plan          Run monitor + researcher + planner
  sentinel status        Show current project health and backlog
  sentinel goals         View or update project goals
  sentinel config        View or update role configuration
  sentinel providers     Show provider health and capabilities
"""

import click

from sentinel import __version__


@click.group()
@click.version_option(version=__version__)
def main() -> None:
    """Autonomous meta-agent for managing software projects."""


@main.command()
def init() -> None:
    """Initialize Sentinel in the current project."""
    # TODO: Interactive setup flow
    # 1. Detect project type and structure
    # 2. Ask user to configure each role (provider + model)
    # 3. Ask for project goals
    # 4. Set up .sentinel/ directory
    # 5. If local provider selected, help set up Ollama
    click.echo("sentinel init — not yet implemented")


@main.command()
def cycle() -> None:
    """Run one full loop cycle: assess -> research -> plan -> execute -> review."""
    click.echo("sentinel cycle — not yet implemented")


@main.command()
def watch() -> None:
    """Continuous mode — run the loop on a schedule."""
    click.echo("sentinel watch — not yet implemented")


@main.command()
def scan() -> None:
    """Run just the monitor — assess current project state."""
    click.echo("sentinel scan — not yet implemented")


@main.command()
@click.argument("topic", required=False)
@click.option(
    "--mode",
    type=click.Choice(["targeted", "exploratory", "comparative", "consensus"]),
    default="targeted",
    help="Research mode",
)
def research(topic: str | None, mode: str) -> None:
    """Run deep research on a topic."""
    click.echo(f"sentinel research — not yet implemented (topic: {topic}, mode: {mode})")


@main.command()
def plan() -> None:
    """Run monitor + researcher + planner to generate a backlog."""
    click.echo("sentinel plan — not yet implemented")


@main.command()
def status() -> None:
    """Show current project health and backlog."""
    click.echo("sentinel status — not yet implemented")


@main.command()
def goals() -> None:
    """View or update project goals."""
    click.echo("sentinel goals — not yet implemented")


@main.command("config")
def config_cmd() -> None:
    """View or update role configuration."""
    click.echo("sentinel config — not yet implemented")


@main.command()
def providers() -> None:
    """Show provider health and capabilities."""
    click.echo("sentinel providers — not yet implemented")
