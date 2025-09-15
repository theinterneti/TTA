#!/usr/bin/env python3
"""
TTA Specification Validator

This script validates .kiro specification files against the standardized template
and metadata requirements. It checks for required sections, status indicators,
implementation references, and metadata completeness.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml


class SpecificationValidator:
    """Validates TTA specification files against standards."""
    
    def __init__(self):
        self.required_sections = [
            "# .* Specification",
            r"\*\*Status\*\*:",
            r"\*\*Version\*\*:",
            r"\*\*Implementation\*\*:",
            r"\*\*Owner\*\*:",
            "## Overview",
            "## Implementation Status",
            "## Requirements",
            "## Technical Design",
            "## Testing Strategy",
            "## Validation Checklist"
        ]
        
        self.valid_status_indicators = [
            "✅ OPERATIONAL",
            "🚧 IN_PROGRESS", 
            "❌ OUTDATED",
            "📋 PLANNED"
        ]
        
        self.valid_categories = [
            "therapeutic-systems",
            "web-interfaces", 
            "infrastructure",
            "ai-orchestration",
            "shared-components"
        ]
    
    def validate_specification_file(self, spec_path: Path) -> Tuple[bool, List[str]]:
        """
        Validate a specification markdown file.
        
        Args:
            spec_path: Path to the specification file
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        if not spec_path.exists():
            return False, [f"Specification file does not exist: {spec_path}"]
        
        try:
            content = spec_path.read_text(encoding='utf-8')
        except Exception as e:
            return False, [f"Failed to read specification file: {e}"]
        
        # Check required sections
        missing_sections = self._check_required_sections(content)
        if missing_sections:
            issues.extend([f"Missing required section: {section}" for section in missing_sections])
        
        # Check status indicator
        status_issues = self._check_status_indicator(content)
        issues.extend(status_issues)
        
        # Check version format
        version_issues = self._check_version_format(content)
        issues.extend(version_issues)
        
        # Check implementation references
        impl_issues = self._check_implementation_references(content)
        issues.extend(impl_issues)
        
        # Check validation checklist
        checklist_issues = self._check_validation_checklist(content)
        issues.extend(checklist_issues)
        
        return len(issues) == 0, issues
    
    def validate_metadata_file(self, metadata_path: Path) -> Tuple[bool, List[str]]:
        """
        Validate a specification metadata YAML file.
        
        Args:
            metadata_path: Path to the metadata file
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        if not metadata_path.exists():
            return False, [f"Metadata file does not exist: {metadata_path}"]
        
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = yaml.safe_load(f)
        except Exception as e:
            return False, [f"Failed to parse metadata YAML: {e}"]
        
        # Check required fields
        required_fields = [
            "specification.name",
            "specification.version", 
            "specification.status",
            "specification.category",
            "specification.owner",
            "specification.last_updated"
        ]
        
        for field in required_fields:
            if not self._get_nested_value(metadata, field):
                issues.append(f"Missing required field: {field}")
        
        # Validate status value
        status = self._get_nested_value(metadata, "specification.status")
        if status and status not in self.valid_status_indicators:
            issues.append(f"Invalid status indicator: {status}")
        
        # Validate category
        category = self._get_nested_value(metadata, "specification.category")
        if category and category not in self.valid_categories:
            issues.append(f"Invalid category: {category}")
        
        # Check version format (semantic versioning)
        version = self._get_nested_value(metadata, "specification.version")
        if version and not re.match(r'^\d+\.\d+\.\d+$', version):
            issues.append(f"Invalid version format (should be semantic versioning): {version}")
        
        return len(issues) == 0, issues
    
    def _check_required_sections(self, content: str) -> List[str]:
        """Check for required sections in specification content."""
        missing_sections = []
        
        for section_pattern in self.required_sections:
            if not re.search(section_pattern, content, re.MULTILINE | re.IGNORECASE):
                missing_sections.append(section_pattern)
        
        return missing_sections
    
    def _check_status_indicator(self, content: str) -> List[str]:
        """Check status indicator format and validity."""
        issues = []
        
        status_match = re.search(r'\*\*Status\*\*:\s*([^\n]+)', content)
        if not status_match:
            issues.append("Status indicator not found")
            return issues
        
        status_line = status_match.group(1).strip()
        
        # Extract status indicator (emoji + text)
        status_indicator = None
        for valid_status in self.valid_status_indicators:
            if valid_status in status_line:
                status_indicator = valid_status
                break
        
        if not status_indicator:
            issues.append(f"Invalid status indicator. Must be one of: {', '.join(self.valid_status_indicators)}")
        
        return issues
    
    def _check_version_format(self, content: str) -> List[str]:
        """Check version format (semantic versioning)."""
        issues = []
        
        version_match = re.search(r'\*\*Version\*\*:\s*([^\n]+)', content)
        if not version_match:
            issues.append("Version not found")
            return issues
        
        version = version_match.group(1).strip()
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            issues.append(f"Invalid version format (should be semantic versioning): {version}")
        
        return issues
    
    def _check_implementation_references(self, content: str) -> List[str]:
        """Check for implementation references."""
        issues = []
        
        impl_match = re.search(r'\*\*Implementation\*\*:\s*([^\n]+)', content)
        if not impl_match:
            issues.append("Implementation reference not found")
            return issues
        
        impl_ref = impl_match.group(1).strip()
        if impl_ref in ["{IMPLEMENTATION_REFERENCE}", "", "TBD", "TODO"]:
            issues.append("Implementation reference is placeholder or empty")
        
        return issues
    
    def _check_validation_checklist(self, content: str) -> List[str]:
        """Check validation checklist completeness."""
        issues = []
        
        # Find validation checklist section
        checklist_match = re.search(r'## Validation Checklist\s*\n(.*?)(?=\n##|\n---|\Z)', content, re.DOTALL)
        if not checklist_match:
            issues.append("Validation checklist section not found")
            return issues
        
        checklist_content = checklist_match.group(1)
        
        # Count checklist items
        checklist_items = re.findall(r'- \[ \]', checklist_content)
        if len(checklist_items) < 5:
            issues.append(f"Validation checklist should have at least 5 items, found {len(checklist_items)}")
        
        return issues
    
    def _get_nested_value(self, data: Dict, key_path: str) -> Optional[str]:
        """Get nested value from dictionary using dot notation."""
        keys = key_path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current


def main():
    """Main entry point for specification validator."""
    parser = argparse.ArgumentParser(description="Validate TTA specification files")
    parser.add_argument("paths", nargs="+", help="Paths to specification files or directories")
    parser.add_argument("--metadata", action="store_true", help="Validate metadata files instead of markdown")
    parser.add_argument("--recursive", "-r", action="store_true", help="Recursively search directories")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    validator = SpecificationValidator()
    total_files = 0
    valid_files = 0
    all_issues = []
    
    for path_str in args.paths:
        path = Path(path_str)
        
        if path.is_file():
            files_to_check = [path]
        elif path.is_dir():
            if args.recursive:
                pattern = "*.yaml" if args.metadata else "*.md"
                files_to_check = list(path.rglob(pattern))
            else:
                pattern = "*.yaml" if args.metadata else "*.md"
                files_to_check = list(path.glob(pattern))
        else:
            print(f"Error: Path does not exist: {path}")
            continue
        
        for file_path in files_to_check:
            total_files += 1
            
            if args.metadata:
                is_valid, issues = validator.validate_metadata_file(file_path)
            else:
                is_valid, issues = validator.validate_specification_file(file_path)
            
            if is_valid:
                valid_files += 1
                if args.verbose:
                    print(f"✅ {file_path}")
            else:
                print(f"❌ {file_path}")
                for issue in issues:
                    print(f"   - {issue}")
                all_issues.extend(issues)
    
    # Summary
    print(f"\nValidation Summary:")
    print(f"Total files checked: {total_files}")
    print(f"Valid files: {valid_files}")
    print(f"Invalid files: {total_files - valid_files}")
    print(f"Total issues: {len(all_issues)}")
    
    # Exit with error code if any files are invalid
    sys.exit(0 if valid_files == total_files else 1)


if __name__ == "__main__":
    main()
