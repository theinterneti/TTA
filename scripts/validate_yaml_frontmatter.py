#!/usr/bin/env python3
"""
Validate YAML frontmatter in chatmode and workflow files.
"""

import re
from pathlib import Path

import yaml


def extract_yaml_frontmatter(file_path: Path) -> tuple[bool, dict, str]:
    """
    Extract YAML frontmatter from a markdown file.

    Returns:
        (has_frontmatter, parsed_yaml, error_message)
    """
    content = file_path.read_text()

    # Check for YAML frontmatter pattern
    pattern = r"^---\s*\n(.*?)\n---\s*\n"
    match = re.match(pattern, content, re.DOTALL)

    if not match:
        return False, {}, "No YAML frontmatter found"

    yaml_content = match.group(1)

    try:
        parsed = yaml.safe_load(yaml_content)
        return True, parsed, ""
    except yaml.YAMLError as e:
        return True, {}, f"YAML parsing error: {e}"


def validate_chatmode(file_path: Path) -> tuple[bool, list[str]]:
    """
    Validate chatmode YAML frontmatter structure.

    Expected fields:
    - description (string)
    - tools (list of strings)
    - model (string)
    """
    has_yaml, parsed, error = extract_yaml_frontmatter(file_path)

    issues = []

    if not has_yaml:
        issues.append(f"❌ {error}")
        return False, issues

    if error:
        issues.append(f"❌ {error}")
        return False, issues

    # Check required fields
    required_fields = ["description", "tools", "model"]
    for field in required_fields:
        if field not in parsed:
            issues.append(f"❌ Missing required field: {field}")

    # Validate field types
    if "description" in parsed and not isinstance(parsed["description"], str):
        issues.append("❌ 'description' should be a string")

    if "tools" in parsed:
        if not isinstance(parsed["tools"], list):
            issues.append("❌ 'tools' should be a list")
        elif not all(isinstance(tool, str) for tool in parsed["tools"]):
            issues.append("❌ All tools should be strings")

    if "model" in parsed and not isinstance(parsed["model"], str):
        issues.append("❌ 'model' should be a string")

    if not issues:
        issues.append("✅ Valid chatmode YAML")
        issues.append(f"   - Description: {parsed.get('description', 'N/A')[:60]}...")
        issues.append(f"   - Tools: {len(parsed.get('tools', []))} tools defined")
        issues.append(f"   - Model: {parsed.get('model', 'N/A')}")

    return len([i for i in issues if i.startswith("❌")]) == 0, issues


def validate_workflow(file_path: Path) -> tuple[bool, list[str]]:
    """
    Validate workflow YAML frontmatter structure.

    Expected fields:
    - mode (string, typically 'agent')
    - model (string)
    - tools (list of strings)
    - description (string)
    """
    has_yaml, parsed, error = extract_yaml_frontmatter(file_path)

    issues = []

    if not has_yaml:
        issues.append(f"❌ {error}")
        return False, issues

    if error:
        issues.append(f"❌ {error}")
        return False, issues

    # Check required fields
    required_fields = ["mode", "model", "tools", "description"]
    for field in required_fields:
        if field not in parsed:
            issues.append(f"❌ Missing required field: {field}")

    # Validate field types
    if "mode" in parsed and not isinstance(parsed["mode"], str):
        issues.append("❌ 'mode' should be a string")

    if "model" in parsed and not isinstance(parsed["model"], str):
        issues.append("❌ 'model' should be a string")

    if "tools" in parsed:
        if not isinstance(parsed["tools"], list):
            issues.append("❌ 'tools' should be a list")
        elif not all(isinstance(tool, str) for tool in parsed["tools"]):
            issues.append("❌ All tools should be strings")

    if "description" in parsed and not isinstance(parsed["description"], str):
        issues.append("❌ 'description' should be a string")

    if not issues:
        issues.append("✅ Valid workflow YAML")
        issues.append(f"   - Mode: {parsed.get('mode', 'N/A')}")
        issues.append(f"   - Description: {parsed.get('description', 'N/A')[:60]}...")
        issues.append(f"   - Tools: {len(parsed.get('tools', []))} tools defined")
        issues.append(f"   - Model: {parsed.get('model', 'N/A')}")

    return len([i for i in issues if i.startswith("❌")]) == 0, issues


def main():
    """Validate all chatmode and workflow files."""
    repo_root = Path(__file__).parent.parent

    print("=" * 80)
    print("YAML Frontmatter Validation Report")
    print("=" * 80)
    print()

    # Validate chatmodes
    print("📋 CHATMODES (.augment/chatmodes/*.chatmode.md)")
    print("-" * 80)

    chatmodes_dir = repo_root / ".augment" / "chatmodes"
    chatmode_files = sorted(chatmodes_dir.glob("*.chatmode.md"))

    chatmode_results = []
    for chatmode_file in chatmode_files:
        print(f"\n{chatmode_file.name}:")
        valid, issues = validate_chatmode(chatmode_file)
        chatmode_results.append(valid)
        for issue in issues:
            print(f"  {issue}")

    # Validate workflows
    print("\n" + "=" * 80)
    print("🔄 WORKFLOWS (.augment/workflows/*.prompt.md)")
    print("-" * 80)

    workflows_dir = repo_root / ".augment" / "workflows"
    workflow_files = sorted(workflows_dir.glob("*.prompt.md"))

    workflow_results = []
    for workflow_file in workflow_files:
        print(f"\n{workflow_file.name}:")
        valid, issues = validate_workflow(workflow_file)
        workflow_results.append(valid)
        for issue in issues:
            print(f"  {issue}")

    # Summary
    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("-" * 80)

    chatmodes_passed = sum(chatmode_results)
    chatmodes_total = len(chatmode_results)
    workflows_passed = sum(workflow_results)
    workflows_total = len(workflow_results)

    print(f"Chatmodes: {chatmodes_passed}/{chatmodes_total} passed")
    print(f"Workflows: {workflows_passed}/{workflows_total} passed")
    print(
        f"Overall: {chatmodes_passed + workflows_passed}/{chatmodes_total + workflows_total} passed"
    )

    if chatmodes_passed == chatmodes_total and workflows_passed == workflows_total:
        print("\n✅ All YAML frontmatter is valid!")
        return 0
    print("\n❌ Some files have invalid YAML frontmatter")
    return 1


if __name__ == "__main__":
    exit(main())
