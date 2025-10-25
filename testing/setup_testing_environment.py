#!/usr/bin/env python3
"""
TTA Single-Player Testing Environment Setup

This script helps set up the testing environment for comprehensive
single-player storytelling experience testing.
"""

import os
from pathlib import Path

import requests
import yaml


def print_banner():
    """Print setup banner."""
    print("\n" + "=" * 80)
    print("TTA SINGLE-PLAYER TESTING ENVIRONMENT SETUP")
    print("=" * 80)
    print("Setting up comprehensive AI model testing for storytelling experience")
    print("=" * 80 + "\n")


def check_python_dependencies():
    """Check if required Python packages are installed."""
    print("🔍 Checking Python dependencies...")

    required_packages = [
        "aiohttp",
        "redis",
        "neo4j",
        "yaml",
        "pytest",
        "asyncio",
        "dataclasses",
        "pathlib",
    ]

    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} (missing)")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print(f"💡 Install with: pip install {' '.join(missing_packages)}")
        return False

    print("✅ All Python dependencies satisfied")
    return True


def check_database_connections():
    """Check database connectivity."""
    print("\n🔍 Checking database connections...")

    # Check Redis
    try:
        import redis

        r = redis.Redis(host="localhost", port=6379, decode_responses=True)
        r.ping()
        print("  ✅ Redis connection successful")
        redis_ok = True
    except Exception as e:
        print(f"  ❌ Redis connection failed: {e}")
        print("  💡 Start Redis with: redis-server")
        redis_ok = False

    # Check Neo4j
    try:
        from neo4j import GraphDatabase

        driver = GraphDatabase.driver(
            "bolt://localhost:7687", auth=("neo4j", "neo4j_password")
        )
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            result.single()
        driver.close()
        print("  ✅ Neo4j connection successful")
        neo4j_ok = True
    except Exception as e:
        print(f"  ❌ Neo4j connection failed: {e}")
        print("  💡 Start Neo4j and ensure credentials are correct")
        neo4j_ok = False

    return redis_ok and neo4j_ok


def check_local_models():
    """Check local model availability."""
    print("\n🔍 Checking local model availability...")

    models_to_check = [
        {"name": "Qwen2.5-7B-Instruct", "url": "http://localhost:1234/v1/models"},
        {"name": "Llama-3.1-8B-Instruct", "url": "http://localhost:1235/v1/models"},
    ]

    available_models = []
    for model in models_to_check:
        try:
            response = requests.get(model["url"], timeout=5)
            if response.status_code == 200:
                print(f"  ✅ {model['name']} available")
                available_models.append(model["name"])
            else:
                print(f"  ❌ {model['name']} not responding")
        except Exception as e:
            print(f"  ❌ {model['name']} connection failed: {e}")

    if not available_models:
        print("  💡 Start local models with LM Studio or similar")
        print("  💡 Qwen2.5-7B-Instruct on port 1234")
        print("  💡 Llama-3.1-8B-Instruct on port 1235")

    return available_models


def check_openrouter_config():
    """Check OpenRouter configuration."""
    print("\n🔍 Checking OpenRouter configuration...")

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("  ❌ OPENROUTER_API_KEY environment variable not set")
        print("  💡 Set with: export OPENROUTER_API_KEY=your_key_here")
        print("  💡 Get free API key from: https://openrouter.ai/")
        return False

    # Test API key
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        response = requests.get(
            "https://openrouter.ai/api/v1/models", headers=headers, timeout=10
        )
        if response.status_code == 200:
            models = response.json()
            free_models = [
                m for m in models.get("data", []) if "free" in m.get("id", "").lower()
            ]
            print(
                f"  ✅ OpenRouter API key valid ({len(free_models)} free models available)"
            )
            return True
        print(f"  ❌ OpenRouter API key invalid (status: {response.status_code})")
        return False
    except Exception as e:
        print(f"  ❌ OpenRouter API test failed: {e}")
        return False


def update_config_file(available_models: list[str], openrouter_ok: bool):
    """Update configuration file based on available resources."""
    print("\n🔧 Updating configuration file...")

    config_path = Path("testing/model_testing_config.yaml")

    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"  ❌ Configuration file not found: {config_path}")
        return False

    # Update local model availability
    if "Qwen2.5-7B-Instruct" in available_models:
        config["models"]["local"]["qwen2_5_7b"]["enabled"] = True
        print("  ✅ Enabled Qwen2.5-7B-Instruct")
    else:
        config["models"]["local"]["qwen2_5_7b"]["enabled"] = False
        print("  ⚠️  Disabled Qwen2.5-7B-Instruct (not available)")

    if "Llama-3.1-8B-Instruct" in available_models:
        config["models"]["local"]["llama3_1_8b"]["enabled"] = True
        print("  ✅ Enabled Llama-3.1-8B-Instruct")
    else:
        config["models"]["local"]["llama3_1_8b"]["enabled"] = False
        print("  ⚠️  Disabled Llama-3.1-8B-Instruct (not available)")

    # Update OpenRouter model availability
    if openrouter_ok:
        config["models"]["openrouter"]["llama3_1_8b_openrouter"]["enabled"] = True
        config["models"]["openrouter"]["mistral_7b"]["enabled"] = True
        print("  ✅ Enabled OpenRouter models")
    else:
        config["models"]["openrouter"]["llama3_1_8b_openrouter"]["enabled"] = False
        config["models"]["openrouter"]["mistral_7b"]["enabled"] = False
        print("  ⚠️  Disabled OpenRouter models (API key not configured)")

    # Save updated configuration
    try:
        with open(config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        print("  ✅ Configuration file updated")
        return True
    except Exception as e:
        print(f"  ❌ Failed to update configuration: {e}")
        return False


def create_results_directory():
    """Create results directory structure."""
    print("\n📁 Creating results directory structure...")

    results_dir = Path("testing/results")
    results_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectories
    subdirs = ["raw_data", "analysis", "reports", "logs"]
    for subdir in subdirs:
        (results_dir / subdir).mkdir(exist_ok=True)
        print(f"  ✅ Created {results_dir / subdir}")

    # Create .gitignore for results
    gitignore_path = results_dir / ".gitignore"
    if not gitignore_path.exists():
        with open(gitignore_path, "w") as f:
            f.write("# Ignore test results but keep directory structure\n")
            f.write("*.json\n")
            f.write("*.csv\n")
            f.write("*.log\n")
            f.write("!.gitkeep\n")
        print(f"  ✅ Created {gitignore_path}")

    return True


def generate_quick_start_guide():
    """Generate a quick start guide."""
    print("\n📝 Generating quick start guide...")

    guide_content = """# TTA Single-Player Testing Quick Start Guide

## Prerequisites Checklist
- [ ] Python dependencies installed
- [ ] Redis running on localhost:6379
- [ ] Neo4j running on localhost:7687
- [ ] At least one local model running (Qwen2.5 or Llama-3.1)
- [ ] OpenRouter API key configured (optional)

## Quick Commands

### Check Configuration Status
```bash
python testing/run_single_player_tests.py --mode status
```

### Run Quick Test (Single Model/Profile/Scenario)
```bash
python testing/run_single_player_tests.py --mode quick
```

### Run Comprehensive Test Suite
```bash
python testing/run_single_player_tests.py --mode comprehensive
```

## Model Setup Instructions

### Local Models (Recommended)
1. Install LM Studio or similar local inference server
2. Download and run:
   - Qwen2.5-7B-Instruct on port 1234
   - Llama-3.1-8B-Instruct on port 1235

### OpenRouter Models (Optional)
1. Get free API key from https://openrouter.ai/
2. Set environment variable:
   ```bash
   export OPENROUTER_API_KEY=your_key_here
   ```

## Understanding Results

### Scoring System (1-10 scale)
- **Narrative Quality (40%)**: Creativity, consistency, depth
- **User Engagement (30%)**: Fun factor, immersion, retention
- **Therapeutic Integration (20%)**: Subtlety, effectiveness, safety
- **Technical Performance (10%)**: Speed, reliability, efficiency

### Target Scores
- **Minimum Acceptable**: 6.0/10
- **Target Score**: 7.5/10
- **Excellence Threshold**: 8.5/10

## Troubleshooting

### Common Issues
1. **No models enabled**: Check model server status and configuration
2. **Database connection failed**: Ensure Redis and Neo4j are running
3. **Slow response times**: Check model server resources
4. **High error rates**: Review model configuration and prompts

### Getting Help
- Check logs in `testing/results/logs/`
- Review configuration in `testing/model_testing_config.yaml`
- Run setup script again: `python testing/setup_testing_environment.py`
"""

    guide_path = Path("testing/QUICK_START_GUIDE.md")
    with open(guide_path, "w") as f:
        f.write(guide_content)

    print(f"  ✅ Created {guide_path}")
    return True


def main():
    """Main setup function."""
    print_banner()

    # Run all checks
    deps_ok = check_python_dependencies()
    db_ok = check_database_connections()
    available_models = check_local_models()
    openrouter_ok = check_openrouter_config()

    # Update configuration
    config_ok = update_config_file(available_models, openrouter_ok)

    # Create directory structure
    dirs_ok = create_results_directory()

    # Generate documentation
    guide_ok = generate_quick_start_guide()

    # Summary
    print("\n" + "=" * 80)
    print("SETUP SUMMARY")
    print("=" * 80)

    print(f"Python Dependencies: {'✅' if deps_ok else '❌'}")
    print(f"Database Connections: {'✅' if db_ok else '❌'}")
    print(
        f"Local Models: {'✅' if available_models else '❌'} ({len(available_models)} available)"
    )
    print(f"OpenRouter API: {'✅' if openrouter_ok else '❌'}")
    print(f"Configuration Updated: {'✅' if config_ok else '❌'}")
    print(f"Directory Structure: {'✅' if dirs_ok else '❌'}")
    print(f"Quick Start Guide: {'✅' if guide_ok else '❌'}")

    if all([deps_ok, db_ok, (available_models or openrouter_ok), config_ok]):
        print("\n🎉 SETUP COMPLETE!")
        print("Ready to run TTA single-player storytelling tests")
        print("\n💡 Next steps:")
        print("  1. Review testing/QUICK_START_GUIDE.md")
        print("  2. Run: python testing/run_single_player_tests.py --mode status")
        print("  3. Run: python testing/run_single_player_tests.py --mode quick")
    else:
        print("\n⚠️  SETUP INCOMPLETE")
        print("Please address the issues above before running tests")
        print("\n💡 Common fixes:")
        if not deps_ok:
            print("  - Install missing Python packages")
        if not db_ok:
            print("  - Start Redis and Neo4j services")
        if not available_models and not openrouter_ok:
            print("  - Set up at least one model (local or OpenRouter)")


if __name__ == "__main__":
    main()
