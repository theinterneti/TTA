#!/usr/bin/env python3
"""
Fix Docker Compose Security Issues

This script automatically fixes common security issues in docker-compose files:
1. Adds no-new-privileges security option
2. Adds read_only: true where appropriate (with exceptions for databases)
3. Removes privileged mode where not necessary
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, Any

# Services that need writable filesystem (databases, caches, etc.)
WRITABLE_SERVICES = [
    'neo4j', 'redis', 'postgres', 'postgresql', 'mongodb', 'mysql',
    'elasticsearch', 'prometheus', 'grafana', 'loki', 'tempo',
    'minio', 'vault'
]

def should_be_readonly(service_name: str, service_config: Dict[str, Any]) -> bool:
    """Determine if a service should have read_only filesystem."""
    # Check if service name suggests it needs writable filesystem
    service_lower = service_name.lower()
    for writable in WRITABLE_SERVICES:
        if writable in service_lower:
            return False
    
    # Check if service has volumes that suggest it needs writes
    volumes = service_config.get('volumes', [])
    for volume in volumes:
        if isinstance(volume, str):
            # Check for data directories
            if any(x in volume.lower() for x in ['data', 'logs', 'cache', 'tmp']):
                return False
    
    return True

def fix_docker_compose_security(file_path: Path) -> bool:
    """Fix security issues in a docker-compose file."""
    print(f"\nProcessing: {file_path}")
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            compose = yaml.safe_load(content)
        
        if not compose or 'services' not in compose:
            print(f"  ⚠️  No services found in {file_path}")
            return False
        
        changes_made = False
        
        for service_name, service_config in compose['services'].items():
            if not isinstance(service_config, dict):
                continue
            
            # Fix 1: Add no-new-privileges security option
            if 'security_opt' not in service_config:
                service_config['security_opt'] = []
                changes_made = True
            
            if isinstance(service_config['security_opt'], list):
                if 'no-new-privileges:true' not in service_config['security_opt']:
                    service_config['security_opt'].append('no-new-privileges:true')
                    print(f"  ✓ Added no-new-privileges to {service_name}")
                    changes_made = True
            
            # Fix 2: Add read_only where appropriate
            if should_be_readonly(service_name, service_config):
                if 'read_only' not in service_config:
                    service_config['read_only'] = True
                    print(f"  ✓ Added read_only to {service_name}")
                    changes_made = True
            else:
                print(f"  ℹ️  Skipping read_only for {service_name} (needs writable filesystem)")
            
            # Fix 3: Remove privileged mode if present (unless explicitly needed)
            if service_config.get('privileged') == True:
                # Only remove if not a monitoring/system service
                if not any(x in service_name.lower() for x in ['prometheus', 'node-exporter', 'cadvisor']):
                    del service_config['privileged']
                    print(f"  ✓ Removed privileged mode from {service_name}")
                    changes_made = True
        
        if changes_made:
            # Write back to file
            with open(file_path, 'w') as f:
                yaml.dump(compose, f, default_flow_style=False, sort_keys=False, indent=2)
            print(f"  ✅ Updated {file_path}")
            return True
        else:
            print(f"  ℹ️  No changes needed for {file_path}")
            return False
    
    except Exception as e:
        print(f"  ❌ Error processing {file_path}: {e}")
        return False

def main():
    """Main function to fix all docker-compose files."""
    docker_compose_files = [
        'docker-compose.yml',
        'docker-compose.dev.yml',
        'docker-compose.test.yml',
        'docker-compose.staging.yml',
        'docker-compose.homelab.yml',
        'docker-compose.phase2a.yml',
        'docker-compose.analytics.yml',
        'monitoring/docker-compose.yml',
        'monitoring/docker-compose.monitoring.yml',
        'src/player_experience/docker-compose.yml',
        'src/player_experience/franchise_worlds/deployment/docker-compose.yml',
        'templates/tta.dev/docker-compose.yml',
        'templates/tta.prototype/docker-compose.yml',
    ]
    
    print("=" * 80)
    print("Docker Compose Security Fixer")
    print("=" * 80)
    
    total_files = 0
    fixed_files = 0
    
    for file_path_str in docker_compose_files:
        file_path = Path(file_path_str)
        if file_path.exists():
            total_files += 1
            if fix_docker_compose_security(file_path):
                fixed_files += 1
        else:
            print(f"\n⚠️  File not found: {file_path}")
    
    print("\n" + "=" * 80)
    print(f"Summary: Fixed {fixed_files}/{total_files} files")
    print("=" * 80)

if __name__ == '__main__':
    main()

