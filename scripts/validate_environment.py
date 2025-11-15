#!/usr/bin/env python3
"""
TTA Environment Configuration Validator

This script validates the TTA environment configuration to ensure all required
variables are set and properly configured for the model management system.
"""

import os
import re
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from dotenv import load_dotenv
except ImportError:
    sys.exit(1)


class EnvironmentValidator:
    """Validates TTA environment configuration."""

    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.info: list[str] = []

    def validate_file_structure(self) -> bool:
        """Validate environment file structure."""

        required_files = [".env.example"]
        recommended_files = [".env", ".env.local.example"]

        all_good = True

        for file in required_files:
            if not Path(file).exists():
                self.errors.append(f"Required file missing: {file}")
                all_good = False
            else:
                self.info.append(f"✅ Found required file: {file}")

        for file in recommended_files:
            if not Path(file).exists():
                self.warnings.append(f"Recommended file missing: {file}")
            else:
                self.info.append(f"✅ Found recommended file: {file}")

        return all_good

    def validate_required_variables(self, env_vars: dict[str, str]) -> bool:
        """Validate required environment variables."""

        required_vars = [
            "ENVIRONMENT",
            "POSTGRES_DB",
            "POSTGRES_USER",
            "POSTGRES_PASSWORD",
            "REDIS_URL",
            "NEO4J_URI",
            "NEO4J_USER",
            "NEO4J_PASSWORD",
        ]

        all_good = True

        for var in required_vars:
            value = env_vars.get(var)
            if not value:
                self.errors.append(f"Required variable missing or empty: {var}")
                all_good = False
            elif value.startswith("your_") or value.startswith("CHANGE_ME"):
                self.errors.append(f"Variable has placeholder value: {var}")
                all_good = False
            else:
                self.info.append(f"✅ {var} is set")

        return all_good

    def validate_api_keys(self, env_vars: dict[str, str]) -> bool:
        """Validate API key configuration."""

        api_keys = {
            "OPENROUTER_API_KEY": {
                "required": False,
                "pattern": r"^sk-or-v1-[a-f0-9]{64}$",
            },
            "OPENAI_API_KEY": {"required": False, "pattern": r"^sk-[a-zA-Z0-9]{48,}$"},
            "ANTHROPIC_API_KEY": {
                "required": False,
                "pattern": r"^sk-ant-[a-zA-Z0-9\-]{95,}$",
            },
        }

        has_any_key = False
        all_good = True

        for key, config in api_keys.items():
            value = env_vars.get(key)

            if not value or value.startswith("your_"):
                if config["required"]:
                    self.errors.append(f"Required API key missing: {key}")
                    all_good = False
                else:
                    self.warnings.append(f"Optional API key not set: {key}")
            else:
                has_any_key = True
                if re.match(config["pattern"], value):
                    self.info.append(f"✅ {key} format looks valid")
                else:
                    self.warnings.append(f"⚠️  {key} format may be invalid")

        if not has_any_key:
            self.errors.append(
                "No AI model API keys configured. At least one is required for model management."
            )
            all_good = False

        return all_good

    def validate_security_config(self, env_vars: dict[str, str]) -> bool:
        """Validate security configuration."""

        security_vars = {
            "JWT_SECRET_KEY": {"min_length": 32, "required": True},
            "ENCRYPTION_KEY": {"min_length": 24, "required": False},
            "FERNET_KEY": {"min_length": 24, "required": False},
        }

        all_good = True

        for var, config in security_vars.items():
            value = env_vars.get(var)

            if not value:
                if config["required"]:
                    self.errors.append(f"Required security variable missing: {var}")
                    all_good = False
                else:
                    self.warnings.append(f"Optional security variable not set: {var}")
            elif len(value) < config["min_length"]:
                self.errors.append(
                    f"{var} is too short (minimum {config['min_length']} characters)"
                )
                all_good = False
            elif value.startswith("dev_") or value.startswith("CHANGE_ME"):
                if env_vars.get("ENVIRONMENT") == "production":
                    self.errors.append(
                        f"{var} has development/placeholder value in production"
                    )
                    all_good = False
                else:
                    self.warnings.append(f"{var} has development value (OK for dev)")
            else:
                self.info.append(f"✅ {var} is properly configured")

        return all_good

    def validate_feature_flags(self, env_vars: dict[str, str]) -> bool:
        """Validate feature flag configuration."""

        model_management_enabled = (
            env_vars.get("FEATURE_MODEL_MANAGEMENT", "").lower() == "true"
        )

        if not model_management_enabled:
            self.warnings.append("Model management feature is disabled")
        else:
            self.info.append("✅ Model management feature is enabled")

        # Check therapeutic features
        therapeutic_features = [
            "FEATURE_AI_NARRATIVE",
            "FEATURE_CRISIS_SUPPORT",
            "FEATURE_REAL_TIME_MONITORING",
        ]

        for feature in therapeutic_features:
            if env_vars.get(feature, "").lower() == "true":
                self.info.append(f"✅ {feature} is enabled")
            else:
                self.warnings.append(f"{feature} is disabled")

        return True

    def validate_database_urls(self, env_vars: dict[str, str]) -> bool:
        """Validate database URL formats."""

        url_patterns = {
            "REDIS_URL": r"^redis://.*:\d+$",
            "NEO4J_URI": r"^bolt://.*:\d+$",
        }

        all_good = True

        for var, pattern in url_patterns.items():
            value = env_vars.get(var)
            if value and not re.match(pattern, value):
                self.warnings.append(f"{var} format may be invalid: {value}")
            elif value:
                self.info.append(f"✅ {var} format looks valid")

        return all_good

    def validate_environment(self) -> bool:
        """Run all validation checks."""

        # Load environment variables
        load_dotenv()
        env_vars = dict(os.environ)

        # Run all validation checks
        checks = [
            self.validate_file_structure(),
            self.validate_required_variables(env_vars),
            self.validate_api_keys(env_vars),
            self.validate_security_config(env_vars),
            self.validate_feature_flags(env_vars),
            self.validate_database_urls(env_vars),
        ]

        all_passed = all(checks)

        # Print results

        if self.info:
            for _msg in self.info:
                pass

        if self.warnings:
            for _msg in self.warnings:
                pass

        if self.errors:
            for _msg in self.errors:
                pass

        if all_passed and not self.errors:
            pass
        else:
            pass

        if self.warnings:
            pass

        return all_passed and not self.errors

    def print_setup_help(self):
        """Print setup help information."""


def main():
    """Main validation function."""
    validator = EnvironmentValidator()

    try:
        success = validator.validate_environment()

        if not success:
            validator.print_setup_help()
            sys.exit(1)

    except Exception:
        sys.exit(1)


if __name__ == "__main__":
    main()
