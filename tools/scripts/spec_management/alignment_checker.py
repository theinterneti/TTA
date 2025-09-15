#!/usr/bin/env python3
"""
TTA Specification-Implementation Alignment Checker

This script checks alignment between code implementations and their corresponding
specifications. It identifies when code changes lack specification updates and
when specifications reference non-existent implementations.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

import yaml


class AlignmentChecker:
    """Checks alignment between specifications and implementations."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.specs_dir = self.project_root / ".kiro" / "specs"
        self.src_dir = self.project_root / "src"
        self.tests_dir = self.project_root / "tests"
        
        # Critical therapeutic systems that require specification alignment
        self.critical_systems = [
            "therapeutic_systems",
            "therapeutic_safety",
            "crisis_detection",
            "safety_validation",
            "emotional_safety"
        ]
    
    def check_alignment(self, changed_files: List[str] = None) -> Tuple[bool, List[str]]:
        """
        Check specification-implementation alignment.
        
        Args:
            changed_files: List of changed files to check (for pre-commit mode)
            
        Returns:
            Tuple of (is_aligned, list_of_issues)
        """
        issues = []
        
        if changed_files:
            # Pre-commit mode: check only changed files
            code_issues = self._check_changed_files_alignment(changed_files)
            issues.extend(code_issues)
        else:
            # Full mode: comprehensive alignment check
            spec_issues = self._check_specification_references()
            impl_issues = self._check_implementation_coverage()
            issues.extend(spec_issues)
            issues.extend(impl_issues)
        
        return len(issues) == 0, issues
    
    def _check_changed_files_alignment(self, changed_files: List[str]) -> List[str]:
        """Check alignment for changed files in pre-commit mode."""
        issues = []
        
        # Separate code files and spec files
        code_files = []
        spec_files = []
        
        for file_path in changed_files:
            path = Path(file_path)
            
            if path.suffix == '.py' and (str(path).startswith('src/') or str(path).startswith('tests/')):
                code_files.append(path)
            elif path.suffix == '.md' and str(path).startswith('.kiro/specs/'):
                spec_files.append(path)
        
        # Check if critical therapeutic systems are modified without spec updates
        critical_code_changes = self._identify_critical_changes(code_files)
        if critical_code_changes and not spec_files:
            issues.append(
                f"Critical therapeutic system files modified without specification updates: "
                f"{', '.join(str(f) for f in critical_code_changes)}"
            )
        
        # Check if specifications reference valid implementations
        for spec_file in spec_files:
            spec_issues = self._validate_spec_references(spec_file)
            issues.extend(spec_issues)
        
        return issues
    
    def _identify_critical_changes(self, code_files: List[Path]) -> List[Path]:
        """Identify changes to critical therapeutic systems."""
        critical_changes = []
        
        for file_path in code_files:
            file_str = str(file_path)
            
            # Check if file is in critical systems
            for critical_system in self.critical_systems:
                if critical_system in file_str:
                    critical_changes.append(file_path)
                    break
        
        return critical_changes
    
    def _check_specification_references(self) -> List[str]:
        """Check that specification references point to existing implementations."""
        issues = []
        
        for spec_file in self.specs_dir.rglob("*.md"):
            spec_issues = self._validate_spec_references(spec_file)
            issues.extend(spec_issues)
        
        return issues
    
    def _validate_spec_references(self, spec_file: Path) -> List[str]:
        """Validate implementation references in a specification file."""
        issues = []
        
        try:
            content = spec_file.read_text(encoding='utf-8')
        except Exception as e:
            return [f"Failed to read specification {spec_file}: {e}"]
        
        # Extract implementation file references
        impl_refs = self._extract_implementation_references(content)
        
        for ref in impl_refs:
            if ref in ["TBD", "TODO", "{IMPLEMENTATION_REFERENCE}"]:
                continue  # Skip placeholder references
            
            # Check if referenced file exists
            ref_path = self.project_root / ref
            if not ref_path.exists():
                issues.append(f"Specification {spec_file.name} references non-existent file: {ref}")
        
        # Extract API endpoint references
        api_refs = self._extract_api_references(content)
        
        for api_ref in api_refs:
            if api_ref in ["TBD", "TODO", "{API_ENDPOINT}"]:
                continue  # Skip placeholder references
            
            # Check if API endpoint is implemented (basic check)
            if not self._check_api_endpoint_exists(api_ref):
                issues.append(f"Specification {spec_file.name} references unimplemented API endpoint: {api_ref}")
        
        return issues
    
    def _extract_implementation_references(self, content: str) -> List[str]:
        """Extract implementation file references from specification content."""
        references = []
        
        # Look for file path patterns
        file_patterns = [
            r'src/[^\s\)]+\.py',
            r'tests/[^\s\)]+\.py',
            r'web-interfaces/[^\s\)]+\.(tsx?|jsx?)',
            r'\.kiro/[^\s\)]+\.md'
        ]
        
        for pattern in file_patterns:
            matches = re.findall(pattern, content)
            references.extend(matches)
        
        # Look for explicit implementation references
        impl_matches = re.findall(r'\*\*Implementation\*\*:\s*([^\n]+)', content)
        for match in impl_matches:
            # Split by comma and clean up
            refs = [ref.strip() for ref in match.split(',')]
            references.extend(refs)
        
        return list(set(references))  # Remove duplicates
    
    def _extract_api_references(self, content: str) -> List[str]:
        """Extract API endpoint references from specification content."""
        references = []
        
        # Look for API endpoint patterns
        api_patterns = [
            r'/api/[^\s\)]+',
            r'/v\d+/[^\s\)]+',
            r'localhost:\d+/[^\s\)]+',
            r'GET|POST|PUT|DELETE|PATCH\s+/[^\s\)]+'
        ]
        
        for pattern in api_patterns:
            matches = re.findall(pattern, content)
            references.extend(matches)
        
        return list(set(references))  # Remove duplicates
    
    def _check_api_endpoint_exists(self, endpoint: str) -> bool:
        """Check if an API endpoint is implemented (basic heuristic check)."""
        # Remove HTTP method if present
        endpoint_path = re.sub(r'^(GET|POST|PUT|DELETE|PATCH)\s+', '', endpoint)
        
        # Remove localhost:port prefix
        endpoint_path = re.sub(r'^https?://[^/]+', '', endpoint_path)
        
        # Search for endpoint patterns in source code
        search_patterns = [
            f'@app.{method}("{endpoint_path}"' for method in ['get', 'post', 'put', 'delete', 'patch']
        ] + [
            f'router.{method}("{endpoint_path}"' for method in ['get', 'post', 'put', 'delete', 'patch']
        ] + [
            f'"{endpoint_path}"',
            f"'{endpoint_path}'"
        ]
        
        # Search in source files
        for py_file in self.src_dir.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                for pattern in search_patterns:
                    if pattern in content:
                        return True
            except Exception:
                continue
        
        return False
    
    def _check_implementation_coverage(self) -> List[str]:
        """Check that critical implementations have corresponding specifications."""
        issues = []
        
        # Find all therapeutic system implementations
        therapeutic_files = []
        for py_file in self.src_dir.rglob("*.py"):
            if any(critical in str(py_file) for critical in self.critical_systems):
                therapeutic_files.append(py_file)
        
        # Check if each has a corresponding specification
        for impl_file in therapeutic_files:
            if not self._has_corresponding_specification(impl_file):
                issues.append(f"Critical implementation lacks specification: {impl_file}")
        
        return issues
    
    def _has_corresponding_specification(self, impl_file: Path) -> bool:
        """Check if an implementation file has a corresponding specification."""
        # Generate possible specification names based on file path
        relative_path = impl_file.relative_to(self.src_dir)
        
        possible_spec_names = [
            relative_path.stem.replace('_', '-'),
            relative_path.parent.name.replace('_', '-'),
            f"{relative_path.parent.name}-{relative_path.stem}".replace('_', '-')
        ]
        
        # Check if any specification references this file
        for spec_file in self.specs_dir.rglob("*.md"):
            try:
                content = spec_file.read_text(encoding='utf-8')
                if str(impl_file) in content or impl_file.name in content:
                    return True
            except Exception:
                continue
        
        return False
    
    def generate_alignment_report(self) -> Dict:
        """Generate comprehensive alignment report."""
        is_aligned, issues = self.check_alignment()
        
        # Get specification statistics
        total_specs = len(list(self.specs_dir.rglob("*.md")))
        specs_with_impl = 0
        specs_with_valid_refs = 0
        
        for spec_file in self.specs_dir.rglob("*.md"):
            try:
                content = spec_file.read_text(encoding='utf-8')
                impl_refs = self._extract_implementation_references(content)
                
                if impl_refs and not all(ref in ["TBD", "TODO", "{IMPLEMENTATION_REFERENCE}"] for ref in impl_refs):
                    specs_with_impl += 1
                    
                    # Check if references are valid
                    valid_refs = True
                    for ref in impl_refs:
                        if ref not in ["TBD", "TODO", "{IMPLEMENTATION_REFERENCE}"]:
                            ref_path = self.project_root / ref
                            if not ref_path.exists():
                                valid_refs = False
                                break
                    
                    if valid_refs:
                        specs_with_valid_refs += 1
                        
            except Exception:
                continue
        
        return {
            "alignment_status": "aligned" if is_aligned else "misaligned",
            "total_issues": len(issues),
            "issues": issues,
            "statistics": {
                "total_specifications": total_specs,
                "specifications_with_implementation": specs_with_impl,
                "specifications_with_valid_references": specs_with_valid_refs,
                "alignment_percentage": round((specs_with_valid_refs / total_specs * 100) if total_specs > 0 else 0, 2)
            }
        }


def main():
    """Main entry point for alignment checker."""
    parser = argparse.ArgumentParser(description="Check TTA specification-implementation alignment")
    parser.add_argument("files", nargs="*", help="Files to check (for pre-commit mode)")
    parser.add_argument("--pre-commit", action="store_true", help="Run in pre-commit mode")
    parser.add_argument("--report", action="store_true", help="Generate comprehensive alignment report")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    checker = AlignmentChecker()
    
    if args.report:
        # Generate comprehensive report
        report = checker.generate_alignment_report()
        
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print("TTA Specification-Implementation Alignment Report")
            print("=" * 60)
            print(f"Status: {report['alignment_status'].upper()}")
            print(f"Total Issues: {report['total_issues']}")
            print(f"Alignment Percentage: {report['statistics']['alignment_percentage']}%")
            print()
            
            if report['issues']:
                print("Issues Found:")
                for issue in report['issues']:
                    print(f"  - {issue}")
                print()
            
            print("Statistics:")
            stats = report['statistics']
            print(f"  Total Specifications: {stats['total_specifications']}")
            print(f"  Specifications with Implementation: {stats['specifications_with_implementation']}")
            print(f"  Specifications with Valid References: {stats['specifications_with_valid_references']}")
    else:
        # Check alignment for specific files or all files
        changed_files = args.files if args.pre_commit else None
        is_aligned, issues = checker.check_alignment(changed_files)
        
        if args.json:
            result = {
                "aligned": is_aligned,
                "issues": issues
            }
            print(json.dumps(result, indent=2))
        else:
            if is_aligned:
                print("✅ Specification-implementation alignment check passed")
            else:
                print("❌ Specification-implementation alignment issues found:")
                for issue in issues:
                    print(f"  - {issue}")
        
        # Exit with error code if not aligned
        sys.exit(0 if is_aligned else 1)


if __name__ == "__main__":
    main()
