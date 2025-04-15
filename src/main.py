#!/usr/bin/env python3
"""
TTA Main Script

This script provides a command-line interface for the TTA Orchestrator.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestration import TTAOrchestrator, TTAConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='TTA Orchestrator')
    
    # Main command
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start components')
    start_parser.add_argument(
        'components',
        nargs='*',
        help='Components to start (default: all)'
    )
    start_parser.add_argument(
        '--config',
        help='Path to configuration file'
    )
    
    # Stop command
    stop_parser = subparsers.add_parser('stop', help='Stop components')
    stop_parser.add_argument(
        'components',
        nargs='*',
        help='Components to stop (default: all)'
    )
    stop_parser.add_argument(
        '--config',
        help='Path to configuration file'
    )
    
    # Restart command
    restart_parser = subparsers.add_parser('restart', help='Restart components')
    restart_parser.add_argument(
        'components',
        nargs='*',
        help='Components to restart (default: all)'
    )
    restart_parser.add_argument(
        '--config',
        help='Path to configuration file'
    )
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Get component status')
    status_parser.add_argument(
        'components',
        nargs='*',
        help='Components to get status for (default: all)'
    )
    status_parser.add_argument(
        '--config',
        help='Path to configuration file'
    )
    
    # Docker command
    docker_parser = subparsers.add_parser('docker', help='Run Docker commands')
    docker_parser.add_argument(
        'docker_command',
        help='Docker command to run'
    )
    docker_parser.add_argument(
        'docker_args',
        nargs='*',
        help='Arguments for the Docker command'
    )
    docker_parser.add_argument(
        '--repository',
        choices=['tta.dev', 'tta.prototype', 'both'],
        default='both',
        help='Repository to run the command in (default: both)'
    )
    docker_parser.add_argument(
        '--config',
        help='Path to configuration file'
    )
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Manage configuration')
    config_subparsers = config_parser.add_subparsers(dest='config_command', help='Configuration command')
    
    # Config get command
    config_get_parser = config_subparsers.add_parser('get', help='Get configuration value')
    config_get_parser.add_argument(
        'key',
        help='Configuration key (e.g., "tta.dev.enabled")'
    )
    config_get_parser.add_argument(
        '--config',
        help='Path to configuration file'
    )
    
    # Config set command
    config_set_parser = config_subparsers.add_parser('set', help='Set configuration value')
    config_set_parser.add_argument(
        'key',
        help='Configuration key (e.g., "tta.dev.enabled")'
    )
    config_set_parser.add_argument(
        'value',
        help='Configuration value'
    )
    config_set_parser.add_argument(
        '--config',
        help='Path to configuration file'
    )
    
    # Config save command
    config_save_parser = config_subparsers.add_parser('save', help='Save configuration')
    config_save_parser.add_argument(
        '--path',
        help='Path to save configuration to'
    )
    config_save_parser.add_argument(
        '--config',
        help='Path to configuration file'
    )
    
    return parser.parse_args()


def main():
    """Main function."""
    args = parse_args()
    
    if not args.command:
        print("No command specified. Use --help for usage information.")
        return 1
    
    # Create the orchestrator
    try:
        orchestrator = TTAOrchestrator(args.config if hasattr(args, 'config') else None)
    except Exception as e:
        logger.error(f"Error creating orchestrator: {e}")
        return 1
    
    # Handle commands
    if args.command == 'start':
        if args.components:
            # Start specific components
            success = True
            for component in args.components:
                if not orchestrator.start_component(component):
                    success = False
            return 0 if success else 1
        else:
            # Start all components
            return 0 if orchestrator.start_all() else 1
    
    elif args.command == 'stop':
        if args.components:
            # Stop specific components
            success = True
            for component in args.components:
                if not orchestrator.stop_component(component):
                    success = False
            return 0 if success else 1
        else:
            # Stop all components
            return 0 if orchestrator.stop_all() else 1
    
    elif args.command == 'restart':
        if args.components:
            # Restart specific components
            success = True
            for component in args.components:
                if not orchestrator.stop_component(component) or not orchestrator.start_component(component):
                    success = False
            return 0 if success else 1
        else:
            # Restart all components
            return 0 if orchestrator.stop_all() and orchestrator.start_all() else 1
    
    elif args.command == 'status':
        if args.components:
            # Get status of specific components
            for component in args.components:
                status = orchestrator.get_component_status(component)
                if status is not None:
                    print(f"{component}: {status.value}")
                else:
                    print(f"{component}: not found")
        else:
            # Get status of all components
            statuses = orchestrator.get_all_statuses()
            for component, status in statuses.items():
                print(f"{component}: {status.value}")
        return 0
    
    elif args.command == 'docker':
        if args.docker_command == 'compose':
            # Run Docker Compose command
            results = orchestrator.run_docker_compose_command(args.docker_args, args.repository)
            success = True
            for repo, result in results.items():
                print(f"=== {repo} ===")
                print(result.stdout)
                if result.stderr:
                    print(result.stderr)
                if result.returncode != 0:
                    success = False
            return 0 if success else 1
        else:
            # Run Docker command
            result = orchestrator.run_docker_command([args.docker_command] + args.docker_args)
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
            return result.returncode
    
    elif args.command == 'config':
        if not args.config_command:
            print("No config command specified. Use --help for usage information.")
            return 1
        
        if args.config_command == 'get':
            # Get configuration value
            value = orchestrator.config.get(args.key)
            print(f"{args.key}: {value}")
            return 0
        
        elif args.config_command == 'set':
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
            print(f"Set {args.key} to {value}")
            return 0
        
        elif args.config_command == 'save':
            # Save configuration
            success = orchestrator.config.save(args.path)
            return 0 if success else 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
