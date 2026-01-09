#!/usr/bin/env python3
"""

# Logseq: [[TTA.dev/Testing/Setup_testing_environment]]
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


def check_python_dependencies():
    """Check if required Python packages are installed."""

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
        except ImportError:
            missing_packages.append(package)

    return not missing_packages


def check_database_connections():
    """Check database connectivity."""

    # Check Redis
    try:
        import redis

        r = redis.Redis(host="localhost", port=6379, decode_responses=True)
        r.ping()
        redis_ok = True
    except Exception:
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
        neo4j_ok = True
    except Exception:
        neo4j_ok = False

    return redis_ok and neo4j_ok


def check_local_models():
    """Check local model availability."""

    models_to_check = [
        {"name": "Qwen2.5-7B-Instruct", "url": "http://localhost:1234/v1/models"},
        {"name": "Llama-3.1-8B-Instruct", "url": "http://localhost:1235/v1/models"},
    ]

    available_models = []
    for model in models_to_check:
        try:
            response = requests.get(model["url"], timeout=5)
            if response.status_code == 200:
                available_models.append(model["name"])
            else:
                pass
        except Exception:
            pass

    if not available_models:
        pass

    return available_models


def check_openrouter_config():
    """Check OpenRouter configuration."""

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
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
            [m for m in models.get("data", []) if "free" in m.get("id", "").lower()]
            return True
        return False
    except Exception:
        return False


def update_config_file(available_models: list[str], openrouter_ok: bool):
    """Update configuration file based on available resources."""

    config_path = Path("testing/model_testing_config.yaml")

    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        return False

    # Update local model availability
    if "Qwen2.5-7B-Instruct" in available_models:
        config["models"]["local"]["qwen2_5_7b"]["enabled"] = True
    else:
        config["models"]["local"]["qwen2_5_7b"]["enabled"] = False

    if "Llama-3.1-8B-Instruct" in available_models:
        config["models"]["local"]["llama3_1_8b"]["enabled"] = True
    else:
        config["models"]["local"]["llama3_1_8b"]["enabled"] = False

    # Update OpenRouter model availability
    if openrouter_ok:
        config["models"]["openrouter"]["llama3_1_8b_openrouter"]["enabled"] = True
        config["models"]["openrouter"]["mistral_7b"]["enabled"] = True
    else:
        config["models"]["openrouter"]["llama3_1_8b_openrouter"]["enabled"] = False
        config["models"]["openrouter"]["mistral_7b"]["enabled"] = False

    # Save updated configuration
    try:
        with open(config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        return True
    except Exception:
        return False


def create_results_directory():
    """Create results directory structure."""

    results_dir = Path("testing/results")
    results_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectories
    subdirs = ["raw_data", "analysis", "reports", "logs"]
    for subdir in subdirs:
        (results_dir / subdir).mkdir(exist_ok=True)

    # Create .gitignore for results
    gitignore_path = results_dir / ".gitignore"
    if not gitignore_path.exists():
        with open(gitignore_path, "w") as f:
            f.write("# Ignore test results but keep directory structure\n")
            f.write("*.json\n")
            f.write("*.csv\n")
            f.write("*.log\n")
            f.write("!.gitkeep\n")

    return True


def generate_quick_start_guide():
    """Generate a quick start guide."""

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
    create_results_directory()

    # Generate documentation
    generate_quick_start_guide()

    # Summary

    if all([deps_ok, db_ok, (available_models or openrouter_ok), config_ok]):
        pass
    else:
        if not deps_ok:
            pass
        if not db_ok:
            pass
        if not available_models and not openrouter_ok:
            pass


if __name__ == "__main__":
    main()
