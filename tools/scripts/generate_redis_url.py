#!/usr/bin/env python3
"""
Redis Connection URL Generator for TTA Project

This script generates the appropriate Redis connection URL based on the environment
and configuration settings found in the TTA project codebase.

Environments supported:
- Development: Local Redis with password authentication
- Testing: Local Redis with separate database for isolation
- Production: Docker-based Redis with enhanced security
- Testcontainers: Dynamic Redis containers for integration tests

Usage:
    python scripts/generate_redis_url.py [environment]
    
    environment options: dev, test, prod, testcontainer
    default: dev
"""

import os
import sys
from typing import Optional
from urllib.parse import quote_plus


class RedisURLGenerator:
    """Generates Redis connection URLs for different TTA environments."""
    
    # Default configurations based on TTA project analysis
    ENVIRONMENTS = {
        'dev': {
            'host': 'localhost',
            'port': 6379,
            'password': 'TTA_Redis_2024!',
            'db': 0,
            'description': 'Development environment - Local Redis with authentication'
        },
        'test': {
            'host': 'localhost', 
            'port': 6379,
            'password': None,  # Tests typically don't use password
            'db': 1,  # Separate database for test isolation
            'description': 'Testing environment - Local Redis with separate database'
        },
        'prod': {
            'host': 'localhost',  # Will be overridden by Docker networking
            'port': 6379,
            'password': 'TTA_Redis_Prod_2024!',  # Default, overridden by REDIS_PASSWORD
            'db': 0,
            'description': 'Production environment - Docker Redis with enhanced security'
        },
        'testcontainer': {
            'host': 'dynamic',  # Set by testcontainer
            'port': 'dynamic',  # Set by testcontainer  
            'password': None,
            'db': 0,
            'description': 'Testcontainer environment - Dynamic Redis container'
        }
    }
    
    def __init__(self, environment: str = 'dev'):
        """Initialize the URL generator for a specific environment."""
        if environment not in self.ENVIRONMENTS:
            raise ValueError(f"Unknown environment: {environment}. "
                           f"Available: {', '.join(self.ENVIRONMENTS.keys())}")
        
        self.environment = environment
        self.config = self.ENVIRONMENTS[environment].copy()
        
    def _get_env_override(self, key: str, default: any) -> any:
        """Get environment variable override for configuration."""
        env_mappings = {
            'host': ['REDIS_HOST', 'REDIS_URL'],
            'port': ['REDIS_PORT'],
            'password': ['REDIS_PASSWORD'],
            'db': ['REDIS_DB']
        }
        
        for env_var in env_mappings.get(key, []):
            value = os.getenv(env_var)
            if value:
                if key == 'port' or key == 'db':
                    try:
                        return int(value)
                    except ValueError:
                        continue
                elif key == 'host' and env_var == 'REDIS_URL':
                    # Extract host from full URL if provided
                    if value.startswith('redis://'):
                        from urllib.parse import urlparse
                        parsed = urlparse(value)
                        return parsed.hostname
                return value
        return default
    
    def generate_url(self) -> str:
        """Generate the Redis connection URL for the configured environment."""
        # Apply environment variable overrides
        host = self._get_env_override('host', self.config['host'])
        port = self._get_env_override('port', self.config['port'])
        password = self._get_env_override('password', self.config['password'])
        db = self._get_env_override('db', self.config['db'])
        
        # Handle special cases
        if self.environment == 'testcontainer':
            return "redis://dynamic-host:dynamic-port/0  # Set by testcontainer runtime"
        
        # Build URL components
        url_parts = ['redis://']
        
        # Add authentication if password exists
        if password:
            # URL encode password to handle special characters
            encoded_password = quote_plus(password)
            url_parts.append(f":{encoded_password}@")
        
        # Add host and port
        url_parts.append(f"{host}:{port}")
        
        # Add database number
        url_parts.append(f"/{db}")
        
        return ''.join(url_parts)
    
    def get_config_details(self) -> dict:
        """Get detailed configuration information for the environment."""
        return {
            'environment': self.environment,
            'description': self.config['description'],
            'host': self._get_env_override('host', self.config['host']),
            'port': self._get_env_override('port', self.config['port']),
            'password_set': bool(self._get_env_override('password', self.config['password'])),
            'database': self._get_env_override('db', self.config['db']),
            'url': self.generate_url()
        }
    
    def print_environment_info(self):
        """Print detailed environment configuration information."""
        config = self.get_config_details()
        
        print(f"\n🔗 Redis Connection URL for TTA Project")
        print(f"{'='*50}")
        print(f"Environment: {config['environment'].upper()}")
        print(f"Description: {config['description']}")
        print(f"\n📋 Configuration Details:")
        print(f"  Host: {config['host']}")
        print(f"  Port: {config['port']}")
        print(f"  Database: {config['database']}")
        print(f"  Password: {'✅ Set' if config['password_set'] else '❌ None'}")
        print(f"\n🌐 Connection URL:")
        print(f"  {config['url']}")
        
        # Add environment-specific notes
        if self.environment == 'dev':
            print(f"\n📝 Development Notes:")
            print(f"  - Uses Docker Compose Redis service")
            print(f"  - Password: TTA_Redis_2024! (from docker-compose.yml)")
            print(f"  - Override with REDIS_URL or REDIS_PASSWORD env vars")
            
        elif self.environment == 'test':
            print(f"\n📝 Testing Notes:")
            print(f"  - Uses separate database (db=1) for test isolation")
            print(f"  - Configured in TestingSettings class")
            print(f"  - Testcontainers provide dynamic Redis for integration tests")
            
        elif self.environment == 'prod':
            print(f"\n📝 Production Notes:")
            print(f"  - Uses Docker Compose production configuration")
            print(f"  - Password from REDIS_PASSWORD env var or default")
            print(f"  - Enhanced security and performance settings")
            print(f"  - 2GB memory limit with LRU eviction policy")


def main():
    """Main function to generate Redis URL based on command line arguments."""
    # Parse command line arguments
    environment = 'dev'  # default
    if len(sys.argv) > 1:
        environment = sys.argv[1].lower()
    
    try:
        # Generate URL for specified environment
        generator = RedisURLGenerator(environment)
        generator.print_environment_info()
        
        # Also show quick reference for all environments
        print(f"\n🚀 Quick Reference - All Environments:")
        print(f"{'='*50}")
        for env_name in RedisURLGenerator.ENVIRONMENTS.keys():
            try:
                env_generator = RedisURLGenerator(env_name)
                url = env_generator.generate_url()
                print(f"  {env_name.upper():12} {url}")
            except Exception as e:
                print(f"  {env_name.upper():12} Error: {e}")
                
    except ValueError as e:
        print(f"❌ Error: {e}")
        print(f"\nUsage: python {sys.argv[0]} [environment]")
        print(f"Available environments: {', '.join(RedisURLGenerator.ENVIRONMENTS.keys())}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
