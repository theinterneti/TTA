#!/usr/bin/env python3
"""
TTA Main Script

This script provides a command-line interface for the TTA Orchestrator.

Usage:
    ```bash
    # Start all components
    python src/main.py start

    # Start specific components
    python src/main.py start neo4j llm

    # Stop all components
    python src/main.py stop

    # Get status of all components
    python src/main.py status

    # Run Docker Compose command in both repositories
    python src/main.py docker compose up -d

    # Get configuration value
    python src/main.py config get tta.dev.enabled
    ```
"""

import argparse
import logging
import sys
from pathlib import Path

from rich.console import Console

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestration import TTAOrchestrator
from src.orchestration.decorators import log_entry_exit, timing_decorator

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configure rich console
console = Console()

# Initialize observability (APM) early in application startup
try:
    from observability_integration import initialize_observability

    # Initialize with environment-aware configuration
    observability_enabled = initialize_observability(
        service_name="tta",
        service_version="0.1.0",
        enable_prometheus=True,
        prometheus_port=9464,
    )

    if observability_enabled:
        logger.info("✅ Observability (APM) initialized successfully")
        logger.info("📊 Prometheus metrics available at http://localhost:9464/metrics")
    else:
        logger.warning(
            "⚠️ Observability degraded to no-op mode (OpenTelemetry unavailable)"
        )

except ImportError:
    logger.warning(
        "Observability integration not available - install with: uv add opentelemetry-api opentelemetry-sdk"
    )
except Exception as e:
    logger.error(f"Failed to initialize observability: {e}", exc_info=True)


@log_entry_exit
def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description="TTA Orchestrator")

    # Main command
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Start command
    start_parser = subparsers.add_parser("start", help="Start components")
    start_parser.add_argument(
        "components", nargs="*", help="Components to start (default: all)"
    )
    start_parser.add_argument("--config", help="Path to configuration file")

    # Stop command
    stop_parser = subparsers.add_parser("stop", help="Stop components")
    stop_parser.add_argument(
        "components", nargs="*", help="Components to stop (default: all)"
    )
    stop_parser.add_argument("--config", help="Path to configuration file")

    # Restart command
    restart_parser = subparsers.add_parser("restart", help="Restart components")
    restart_parser.add_argument(
        "components", nargs="*", help="Components to restart (default: all)"
    )
    restart_parser.add_argument("--config", help="Path to configuration file")

    # Status command
    status_parser = subparsers.add_parser("status", help="Get component status")
    status_parser.add_argument(
        "components", nargs="*", help="Components to get status for (default: all)"
    )
    status_parser.add_argument("--config", help="Path to configuration file")

    # Docker command
    docker_parser = subparsers.add_parser("docker", help="Run Docker commands")
    docker_parser.add_argument("docker_command", help="Docker command to run")
    docker_parser.add_argument(
        "docker_args", nargs="*", help="Arguments for the Docker command"
    )
    docker_parser.add_argument(
        "--repository",
        choices=["tta.dev", "tta.prototype", "both"],
        default="both",
        help="Repository to run the command in (default: both)",
    )
    docker_parser.add_argument("--config", help="Path to configuration file")

    # Config command
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_subparsers = config_parser.add_subparsers(
        dest="config_command", help="Configuration command"
    )

    # Config get command
    config_get_parser = config_subparsers.add_parser(
        "get", help="Get configuration value"
    )
    config_get_parser.add_argument(
        "key", help='Configuration key (e.g., "tta.dev.enabled")'
    )
    config_get_parser.add_argument("--config", help="Path to configuration file")

    # Config set command
    config_set_parser = config_subparsers.add_parser(
        "set", help="Set configuration value"
    )
    config_set_parser.add_argument(
        "key", help='Configuration key (e.g., "tta.dev.enabled")'
    )
    config_set_parser.add_argument("value", help="Configuration value")
    config_set_parser.add_argument("--config", help="Path to configuration file")

    # Config save command
    config_save_parser = config_subparsers.add_parser("save", help="Save configuration")
    config_save_parser.add_argument("--path", help="Path to save configuration to")
    config_save_parser.add_argument("--config", help="Path to configuration file")

    # Admin command
    admin_parser = subparsers.add_parser("admin", help="Administrative commands")
    admin_subparsers = admin_parser.add_subparsers(
        dest="admin_command", help="Admin subcommand"
    )

    # Admin recover subcommand
    admin_recover = admin_subparsers.add_parser(
        "recover",
        help="Recover expired message reservations and report per-agent stats",
    )
    admin_recover.add_argument(
        "redis_url",
        nargs="?",
        default="redis://localhost:6379/0",
        help="Redis URL (default: redis://localhost:6379/0)",
    )
    admin_recover.add_argument(
        "--key-prefix", default="ao", help="Redis key prefix (default: ao)"
    )

    return parser.parse_args()


@log_entry_exit
@timing_decorator
def main() -> int:
    """
    Main function.

    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    args = parse_args()

    if not args.command:
        console.print(
            "[bold red]No command specified. Use --help for usage information.[/bold red]"
        )
        return 1

    # Create the orchestrator
    try:
        orchestrator = TTAOrchestrator(args.config if hasattr(args, "config") else None)
    except Exception as e:
        logger.error(f"Error creating orchestrator: {e}")
        console.print(f"[bold red]Error creating orchestrator: {e}[/bold red]")
        return 1

    # Handle commands
    if args.command == "start":
        if args.components:
            # Start specific components
            success = True
            for component in args.components:
                console.print(
                    f"[bold blue]Starting component {component}...[/bold blue]"
                )
                if not orchestrator.start_component(component):
                    success = False
                    console.print(
                        f"[bold red]Failed to start component {component}[/bold red]"
                    )
            return 0 if success else 1
        # Start all components
        console.print("[bold blue]Starting all components...[/bold blue]")
        success = orchestrator.start_all()
        if success:
            console.print(
                "[bold green]All components started successfully![/bold green]"
            )
        else:
            console.print("[bold red]Failed to start all components[/bold red]")
        return 0 if success else 1

    if args.command == "stop":
        if args.components:
            # Stop specific components
            success = True
            for component in args.components:
                console.print(
                    f"[bold blue]Stopping component {component}...[/bold blue]"
                )
                if not orchestrator.stop_component(component):
                    success = False
                    console.print(
                        f"[bold red]Failed to stop component {component}[/bold red]"
                    )
            return 0 if success else 1
        # Stop all components
        console.print("[bold blue]Stopping all components...[/bold blue]")
        success = orchestrator.stop_all()
        if success:
            console.print(
                "[bold green]All components stopped successfully![/bold green]"
            )
        else:
            console.print("[bold red]Failed to stop all components[/bold red]")
        return 0 if success else 1

    if args.command == "restart":
        if args.components:
            # Restart specific components
            success = True
            for component in args.components:
                console.print(
                    f"[bold blue]Restarting component {component}...[/bold blue]"
                )
                if not orchestrator.stop_component(
                    component
                ) or not orchestrator.start_component(component):
                    success = False
                    console.print(
                        f"[bold red]Failed to restart component {component}[/bold red]"
                    )
            return 0 if success else 1
        # Restart all components
        console.print("[bold blue]Restarting all components...[/bold blue]")
        success = orchestrator.stop_all() and orchestrator.start_all()
        if success:
            console.print(
                "[bold green]All components restarted successfully![/bold green]"
            )
        else:
            console.print("[bold red]Failed to restart all components[/bold red]")
        return 0 if success else 1

    if args.command == "status":
        if args.components:
            # Get status of specific components
            for component in args.components:
                status = orchestrator.get_component_status(component)
                if status is not None:
                    console.print(
                        f"{component}: [bold green]{status.value}[/bold green]"
                    )
                else:
                    console.print(f"{component}: [bold red]not found[/bold red]")
        else:
            # Get status of all components
            orchestrator.display_status()
        return 0

    if args.command == "docker":
        if args.docker_command == "compose":
            # Run Docker Compose command
            console.print(
                f"[bold blue]Running Docker Compose command in {args.repository}...[/bold blue]"
            )
            try:
                results = orchestrator.run_docker_compose_command(
                    args.docker_args, args.repository
                )
                success = True
                for repo, result in results.items():
                    console.print(f"[bold blue]=== {repo} ===[/bold blue]")
                    console.print(result.stdout)
                    if result.stderr:
                        console.print(f"[bold yellow]{result.stderr}[/bold yellow]")
                    if result.returncode != 0:
                        success = False
                return 0 if success else 1
            except Exception as e:
                console.print(
                    f"[bold red]Error running Docker Compose command: {e}[/bold red]"
                )
                return 1
        else:
            # Run Docker command
            console.print(
                f"[bold blue]Running Docker command: {args.docker_command} {' '.join(args.docker_args)}[/bold blue]"
            )
            try:
                result = orchestrator.run_docker_command(
                    [args.docker_command] + args.docker_args
                )
                console.print(result.stdout)
                if result.stderr:
                    console.print(f"[bold yellow]{result.stderr}[/bold yellow]")
                return result.returncode
            except Exception as e:
                console.print(f"[bold red]Error running Docker command: {e}[/bold red]")
                return 1

    elif args.command == "config":
        if not args.config_command:
            console.print(
                "[bold red]No config command specified. Use --help for usage information.[/bold red]"
            )
            return 1

        if args.config_command == "get":
            # Get configuration value
            value = orchestrator.config.get(args.key)
            console.print(f"{args.key}: [bold green]{value}[/bold green]")
            return 0

        if args.config_command == "set":
            # Set configuration value
            # Convert value to appropriate type
            value = args.value
            if value.lower() in ["true", "yes", "1"]:
                value = True
            elif value.lower() in ["false", "no", "0"]:
                value = False
            elif value.isdigit():
                value = int(value)
            elif value.replace(".", "", 1).isdigit() and value.count(".") == 1:
                value = float(value)

            orchestrator.config.set(args.key, value)
            console.print(f"Set {args.key} to [bold green]{value}[/bold green]")
            return 0

        if args.config_command == "save":
            # Save configuration
            success = orchestrator.config.save(args.path)
            if success:
                console.print(
                    "[bold green]Configuration saved successfully![/bold green]"
                )
            else:
                console.print("[bold red]Failed to save configuration[/bold red]")
            return 0 if success else 1
    elif args.command == "admin":
        if not args.admin_command:
            console.print(
                "[bold red]No admin subcommand specified. Use --help for usage information.[/bold red]"
            )
            return 1
        if args.admin_command == "recover":
            from tta_ai.orchestration.admin.recover import run_recovery

            try:
                per_agent = __import__("asyncio").run(
                    run_recovery(args.redis_url, key_prefix=args.key_prefix)
                )
                total = sum(per_agent.values())
                console.print("[bold blue]Recovered messages summary:[/bold blue]")
                if not per_agent:
                    console.print("  No expired reservations found.")
                for agent, count in per_agent.items():
                    console.print(f"  {agent}: [bold green]{count}[/bold green]")
                console.print(f"Total recovered: [bold green]{total}[/bold green]")
                return 0
            except Exception as e:
                console.print(f"[bold red]Admin recovery failed: {e}[/bold red]")
                return 1

    return 0


if __name__ == "__main__":
    exit_code = 0
    try:
        exit_code = main()
    finally:
        # Shutdown observability cleanly
        try:
            from observability_integration import shutdown_observability

            shutdown_observability()
            logger.info("🔌 Observability shutdown complete")
        except Exception as e:
            logger.debug(f"Observability shutdown failed: {e}")

    sys.exit(exit_code)
