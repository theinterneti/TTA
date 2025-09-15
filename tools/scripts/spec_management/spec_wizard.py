#!/usr/bin/env python3
"""
TTA Specification Creation Wizard

Interactive CLI tool for creating new TTA specifications using standardized templates.
Guides users through the specification creation process with validation and best practices.
"""

import re
import sys
from datetime import datetime
from pathlib import Path

try:
    import click
    import yaml
    from jinja2 import Template
except ImportError as e:
    print(f"Missing required dependency: {e}")
    print("Please install with: pip install click pyyaml jinja2")
    sys.exit(1)


class SpecificationWizard:
    """Interactive wizard for creating TTA specifications."""

    def __init__(self):
        self.template_dir = Path(__file__).parent.parent.parent / ".kiro" / "templates"
        self.specs_dir = Path(__file__).parent.parent.parent / ".kiro" / "specs"

        self.categories = [
            "therapeutic-systems",
            "web-interfaces",
            "infrastructure",
            "ai-orchestration",
            "shared-components",
        ]

        self.status_options = [
            ("📋 PLANNED", "Specification is planned but implementation not started"),
            ("🚧 IN_PROGRESS", "Implementation is in progress"),
            ("✅ OPERATIONAL", "Implementation is complete and operational"),
            ("❌ OUTDATED", "Specification needs updates to match implementation"),
        ]

        self.priority_options = ["critical", "high", "medium", "low"]

    def run_interactive_wizard(self) -> dict:
        """Run the interactive specification creation wizard."""
        click.echo("🎯 TTA Specification Creation Wizard")
        click.echo("=" * 50)

        spec_data = {}

        # Basic information
        spec_data["name"] = click.prompt("Specification name", type=str)
        spec_data["slug"] = self._generate_slug(spec_data["name"])

        # Category selection
        click.echo("\nAvailable categories:")
        for i, category in enumerate(self.categories, 1):
            click.echo(f"  {i}. {category}")

        category_idx = (
            click.prompt(
                "Select category", type=click.IntRange(1, len(self.categories))
            )
            - 1
        )
        spec_data["category"] = self.categories[category_idx]

        # Status selection
        click.echo("\nAvailable status options:")
        for i, (status, description) in enumerate(self.status_options, 1):
            click.echo(f"  {i}. {status} - {description}")

        status_idx = (
            click.prompt(
                "Select status", type=click.IntRange(1, len(self.status_options))
            )
            - 1
        )
        spec_data["status_indicator"], spec_data["status_description"] = (
            self.status_options[status_idx]
        )

        # Priority selection
        click.echo("\nAvailable priorities:")
        for i, priority in enumerate(self.priority_options, 1):
            click.echo(f"  {i}. {priority}")

        priority_idx = (
            click.prompt(
                "Select priority", type=click.IntRange(1, len(self.priority_options))
            )
            - 1
        )
        spec_data["priority"] = self.priority_options[priority_idx]

        # Owner and reviewer
        spec_data["owner"] = click.prompt("Specification owner", type=str)
        spec_data["reviewer"] = click.prompt(
            "Initial reviewer", default=spec_data["owner"]
        )

        # Description
        spec_data["description"] = click.prompt("Brief description", type=str)

        # Implementation details
        if spec_data["status_indicator"] in ["✅ OPERATIONAL", "🚧 IN_PROGRESS"]:
            spec_data["implementation_files"] = (
                click.prompt(
                    "Implementation files (comma-separated)", default="", type=str
                ).split(",")
                if click.confirm("Add implementation file references?")
                else []
            )

            spec_data["api_endpoints"] = (
                click.prompt(
                    "API endpoints (comma-separated)", default="", type=str
                ).split(",")
                if click.confirm("Add API endpoint references?")
                else []
            )
        else:
            spec_data["implementation_files"] = []
            spec_data["api_endpoints"] = []

        # Performance requirements
        if click.confirm("Add performance requirements?"):
            spec_data["response_time"] = click.prompt(
                "Response time requirement", default="<1s"
            )
            spec_data["throughput"] = click.prompt(
                "Throughput requirement", default="TBD"
            )
            spec_data["resource_limits"] = click.prompt(
                "Resource constraints", default="TBD"
            )
        else:
            spec_data["response_time"] = "TBD"
            spec_data["throughput"] = "TBD"
            spec_data["resource_limits"] = "TBD"

        # Security requirements
        spec_data["auth_required"] = click.confirm("Authentication required?")
        spec_data["hipaa_compliant"] = click.confirm("HIPAA compliance required?")

        # Generate timestamps and version
        now = datetime.now()
        spec_data["last_updated"] = now.strftime("%Y-%m-%d")
        spec_data["spec_version"] = "1.0.0"
        spec_data["template_last_updated"] = now.strftime("%Y-%m-%d")

        return spec_data

    def create_specification_files(self, spec_data: dict) -> tuple[Path, Path]:
        """Create specification markdown and metadata files."""
        # Create specification directory
        spec_dir = self.specs_dir / spec_data["slug"]
        spec_dir.mkdir(parents=True, exist_ok=True)

        # Create markdown file
        md_path = spec_dir / f"{spec_data['slug']}-specification.md"
        self._create_markdown_file(md_path, spec_data)

        # Create metadata file
        metadata_path = spec_dir / "metadata.yaml"
        self._create_metadata_file(metadata_path, spec_data)

        return md_path, metadata_path

    def _create_markdown_file(self, path: Path, spec_data: dict):
        """Create specification markdown file from template."""
        template_path = self.template_dir / "specification-template.md"

        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        template_content = template_path.read_text(encoding="utf-8")
        template = Template(template_content)

        # Prepare template variables
        template_vars = {
            "SPECIFICATION_NAME": spec_data["name"],
            "STATUS_INDICATOR": spec_data["status_indicator"],
            "STATUS_TEXT": spec_data["status_indicator"],
            "LAST_UPDATED": spec_data["last_updated"],
            "SPEC_VERSION": spec_data["spec_version"],
            "IMPLEMENTATION_REFERENCE": ", ".join(spec_data["implementation_files"])
            or "TBD",
            "SPECIFICATION_OWNER": spec_data["owner"],
            "LAST_REVIEWER": spec_data["reviewer"],
            "BRIEF_DESCRIPTION_OF_SPECIFICATION_PURPOSE": spec_data["description"],
            "LIST_OF_IMPLEMENTATION_FILES": ", ".join(spec_data["implementation_files"])
            or "TBD",
            "LIST_OF_API_ENDPOINTS": ", ".join(spec_data["api_endpoints"]) or "TBD",
            "TEST_COVERAGE_PERCENTAGE": "TBD",
            "PERFORMANCE_REQUIREMENTS": f"Response time: {spec_data['response_time']}, Throughput: {spec_data['throughput']}",
            "BACKEND_INTEGRATION_DETAILS": "TBD",
            "FRONTEND_INTEGRATION_DETAILS": "TBD",
            "DATABASE_SCHEMA_REFERENCES": "TBD",
            "EXTERNAL_API_DEPENDENCIES": "TBD",
            "USER_TYPE": "user",
            "FUNCTIONALITY": "TBD",
            "BENEFIT": "TBD",
            "CONDITION": "TBD",
            "EXPECTED_BEHAVIOR": "TBD",
            "IMPLEMENTATION_FILES": ", ".join(spec_data["implementation_files"])
            or "TBD",
            "SPECIFIC_CODE_REFERENCES": "TBD",
            "TEST_FILE_REFERENCES": "TBD",
            "RESPONSE_TIME_REQUIREMENT": spec_data["response_time"],
            "THROUGHPUT_REQUIREMENT": spec_data["throughput"],
            "RESOURCE_CONSTRAINTS": spec_data["resource_limits"],
            "AUTH_REQUIREMENTS": (
                "Required" if spec_data["auth_required"] else "Not required"
            ),
            "AUTHZ_REQUIREMENTS": "TBD",
            "DATA_PROTECTION_REQUIREMENTS": "TBD",
            "SCALABILITY_REQUIREMENTS": "TBD",
            "AVAILABILITY_REQUIREMENTS": "TBD",
            "RELIABILITY_REQUIREMENTS": "TBD",
            "HIPAA_REQUIREMENTS": (
                "Required" if spec_data["hipaa_compliant"] else "Not applicable"
            ),
            "THERAPEUTIC_COMPLIANCE": "TBD",
            "ACCESSIBILITY_REQUIREMENTS": "WCAG 2.1 AA compliance",
            "ARCHITECTURE_DESCRIPTION": "TBD",
            "COMPONENT_INTERACTION_DETAILS": "TBD",
            "DATA_FLOW_DESCRIPTION": "TBD",
            "UNIT_TEST_FILES": "TBD",
            "COVERAGE_TARGET": "80",
            "CRITICAL_TEST_SCENARIOS": "TBD",
            "INTEGRATION_TEST_FILES": "TBD",
            "EXTERNAL_TEST_DEPENDENCIES": "TBD",
            "PERFORMANCE_TEST_REFERENCES": "TBD",
            "E2E_TEST_SCENARIOS": "TBD",
            "USER_JOURNEY_TESTS": "TBD",
            "ACCEPTANCE_TEST_MAPPING": "TBD",
            "ENVIRONMENT_VARIABLES": "TBD",
            "RUNTIME_DEPENDENCIES": "TBD",
            "DEV_DEPENDENCIES": "TBD",
            "EXTERNAL_SERVICE_DEPENDENCIES": "TBD",
            "CONFIGURATION_FILES": "TBD",
            "SCHEMA_FILES": "TBD",
            "MIGRATION_SCRIPTS": "TBD",
            "KPI_METRICS": "TBD",
            "HEALTH_CHECK_URLS": "TBD",
            "ALERT_THRESHOLDS": "TBD",
            "LOG_LEVEL_CONFIGURATION": "TBD",
            "LOG_FORMAT_SPECIFICATIONS": "TBD",
            "LOG_AGGREGATION_SETUP": "TBD",
            "CHANGE_DESCRIPTION": "Initial specification creation",
            "CHANGE_IMPACT": "New specification",
            "MIGRATION_INSTRUCTIONS": "N/A",
            "PREVIOUS_VERSION": "N/A",
            "PREVIOUS_CHANGE_SUMMARY": "N/A",
            "RELATED_SPECIFICATION_LINKS": "TBD",
            "DEPENDENCY_SPECIFICATIONS": "TBD",
            "DEPENDENT_SPECIFICATIONS": "TBD",
            "API_DOC_LINKS": "TBD",
            "CODE_DOC_LINKS": "TBD",
            "USER_GUIDE_LINKS": "TBD",
            "TEMPLATE_LAST_UPDATED": spec_data["template_last_updated"],
        }

        rendered_content = template.render(**template_vars)
        path.write_text(rendered_content, encoding="utf-8")

    def _create_metadata_file(self, path: Path, spec_data: dict):
        """Create specification metadata YAML file from template."""
        template_path = self.template_dir / "specification-metadata.yaml"

        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        template_content = template_path.read_text(encoding="utf-8")
        template = Template(template_content)

        # Prepare template variables
        template_vars = {
            "SPECIFICATION_NAME": spec_data["name"],
            "SPEC_VERSION": spec_data["spec_version"],
            "STATUS_INDICATOR": spec_data["status_indicator"],
            "CATEGORY": spec_data["category"],
            "PRIORITY": spec_data["priority"],
            "SPECIFICATION_OWNER": spec_data["owner"],
            "LAST_REVIEWER": spec_data["reviewer"],
            "LAST_UPDATED": spec_data["last_updated"],
            "NEXT_REVIEW_DATE": "TBD",
            "IMPLEMENTATION_STATUS": "not-started",
            "COMPLETION_PERCENTAGE": 0,
            "IMPLEMENTATION_FILE_PATH": "TBD",
            "FILE_TYPE": "source",
            "COVERAGE_PERCENTAGE": 0,
            "API_ENDPOINT_PATH": "TBD",
            "HTTP_METHOD": "GET",
            "ENDPOINT_STATUS": "planned",
            "COVERAGE_TARGET": 80,
            "CURRENT_COVERAGE": 0,
            "RESPONSE_TIME_REQUIREMENT": spec_data["response_time"],
            "THROUGHPUT_REQUIREMENT": spec_data["throughput"],
            "RESOURCE_CONSTRAINTS": spec_data["resource_limits"],
            "AUTH_REQUIRED": spec_data["auth_required"],
            "HIPAA_COMPLIANT": spec_data["hipaa_compliant"],
            "DATA_CLASSIFICATION": "internal",
            "VERSION": spec_data["spec_version"],
            "CHANGE_DATE": spec_data["last_updated"],
            "CHANGE_DESCRIPTION": "Initial specification creation",
            "CHANGE_IMPACT": "New specification",
            "MIGRATION_NOTES": "N/A",
            "COMPLETENESS_SCORE": 50,
            "ALIGNMENT_SCORE": 100,
            "LAST_VALIDATION_DATE": spec_data["last_updated"],
            "CI_CHECKS_ENABLED": True,
            "AUTO_VERSION_BUMP": False,
            "TEMPLATE_LAST_UPDATED": spec_data["template_last_updated"],
        }

        rendered_content = template.render(**template_vars)
        path.write_text(rendered_content, encoding="utf-8")

    def _generate_slug(self, name: str) -> str:
        """Generate URL-friendly slug from specification name."""
        slug = re.sub(r"[^\w\s-]", "", name.lower())
        slug = re.sub(r"[-\s]+", "-", slug)
        return slug.strip("-")


@click.command()
@click.option("--name", help="Specification name (skip interactive mode)")
@click.option(
    "--category",
    type=click.Choice(
        [
            "therapeutic-systems",
            "web-interfaces",
            "infrastructure",
            "ai-orchestration",
            "shared-components",
        ]
    ),
    help="Specification category",
)
@click.option("--owner", help="Specification owner")
@click.option(
    "--interactive/--no-interactive", default=True, help="Run in interactive mode"
)
def main(name, category, owner, interactive):
    """Create a new TTA specification using the standardized template."""
    wizard = SpecificationWizard()

    try:
        if interactive or not all([name, category, owner]):
            spec_data = wizard.run_interactive_wizard()
        else:
            # Non-interactive mode with provided parameters
            spec_data = {
                "name": name,
                "slug": wizard._generate_slug(name),
                "category": category,
                "owner": owner,
                "reviewer": owner,
                "status_indicator": "📋 PLANNED",
                "status_description": "Specification is planned but implementation not started",
                "priority": "medium",
                "description": "TBD",
                "implementation_files": [],
                "api_endpoints": [],
                "response_time": "TBD",
                "throughput": "TBD",
                "resource_limits": "TBD",
                "auth_required": False,
                "hipaa_compliant": False,
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "spec_version": "1.0.0",
                "template_last_updated": datetime.now().strftime("%Y-%m-%d"),
            }

        # Create specification files
        md_path, metadata_path = wizard.create_specification_files(spec_data)

        click.echo("\n✅ Specification created successfully!")
        click.echo(f"📄 Markdown file: {md_path}")
        click.echo(f"📊 Metadata file: {metadata_path}")
        click.echo("\n📝 Next steps:")
        click.echo("1. Edit the specification file to add detailed requirements")
        click.echo("2. Update implementation references as development progresses")
        click.echo(
            f"3. Run validation: python scripts/spec_management/spec_validator.py {md_path}"
        )

    except KeyboardInterrupt:
        click.echo("\n❌ Specification creation cancelled.")
        sys.exit(1)
    except Exception as e:
        click.echo(f"\n❌ Error creating specification: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
