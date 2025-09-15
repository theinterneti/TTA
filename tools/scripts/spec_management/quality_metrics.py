#!/usr/bin/env python3
"""
TTA Specification Quality Metrics

This module provides quality metrics and scoring for TTA specifications,
including completeness, alignment, and maintenance health indicators.
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import yaml
except ImportError:
    print("Missing required dependency: pyyaml")
    print("Please install with: pip install pyyaml")
    exit(1)


class SpecificationQualityMetrics:
    """Calculate and track specification quality metrics."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.specs_dir = self.project_root / ".kiro" / "specs"
        
        # Quality scoring weights
        self.weights = {
            "completeness": 0.4,
            "alignment": 0.3,
            "freshness": 0.2,
            "validation": 0.1
        }
        
        # Required sections for completeness scoring
        self.required_sections = [
            "Overview",
            "Implementation Status", 
            "Requirements",
            "Technical Design",
            "Testing Strategy",
            "Validation Checklist"
        ]
    
    def calculate_specification_score(self, spec_path: Path) -> Dict:
        """Calculate comprehensive quality score for a specification."""
        if not spec_path.exists():
            return {"error": f"Specification not found: {spec_path}"}
        
        try:
            content = spec_path.read_text(encoding='utf-8')
            metadata = self._load_metadata(spec_path)
        except Exception as e:
            return {"error": f"Failed to read specification: {e}"}
        
        # Calculate individual scores
        completeness_score = self._calculate_completeness_score(content)
        alignment_score = self._calculate_alignment_score(content, metadata)
        freshness_score = self._calculate_freshness_score(content, metadata)
        validation_score = self._calculate_validation_score(content)
        
        # Calculate weighted overall score
        overall_score = (
            completeness_score * self.weights["completeness"] +
            alignment_score * self.weights["alignment"] +
            freshness_score * self.weights["freshness"] +
            validation_score * self.weights["validation"]
        )
        
        return {
            "overall_score": round(overall_score, 2),
            "scores": {
                "completeness": completeness_score,
                "alignment": alignment_score,
                "freshness": freshness_score,
                "validation": validation_score
            },
            "grade": self._score_to_grade(overall_score),
            "recommendations": self._generate_recommendations(
                completeness_score, alignment_score, freshness_score, validation_score
            )
        }
    
    def _calculate_completeness_score(self, content: str) -> float:
        """Calculate completeness score based on required sections and content depth."""
        score = 0.0
        
        # Check for required sections (60% of score)
        sections_found = 0
        for section in self.required_sections:
            if re.search(f"## {section}", content, re.IGNORECASE):
                sections_found += 1
        
        section_score = (sections_found / len(self.required_sections)) * 60
        
        # Check for content depth (40% of score)
        depth_indicators = [
            r"```",  # Code blocks
            r"\*\*[^*]+\*\*:",  # Bold labels
            r"- \[[ x]\]",  # Checklists
            r"WHEN .+ THEN",  # Acceptance criteria
            r"src/[^\s]+\.py",  # Implementation references
            r"localhost:\d+",  # API endpoints
        ]
        
        depth_score = 0
        for indicator in depth_indicators:
            matches = len(re.findall(indicator, content))
            depth_score += min(matches * 2, 10)  # Cap at 10 points per indicator
        
        depth_score = min(depth_score, 40)  # Cap at 40% of total
        
        return min(section_score + depth_score, 100)
    
    def _calculate_alignment_score(self, content: str, metadata: Optional[Dict]) -> float:
        """Calculate alignment score based on implementation references and status."""
        score = 100.0  # Start with perfect score
        
        # Check status indicator validity
        status_match = re.search(r'\*\*Status\*\*:\s*([^\n]+)', content)
        if not status_match:
            score -= 20
        else:
            status = status_match.group(1).strip()
            valid_statuses = ["✅ OPERATIONAL", "🚧 IN_PROGRESS", "❌ OUTDATED", "📋 PLANNED"]
            if not any(valid_status in status for valid_status in valid_statuses):
                score -= 15
        
        # Check implementation references
        impl_match = re.search(r'\*\*Implementation\*\*:\s*([^\n]+)', content)
        if not impl_match:
            score -= 25
        else:
            impl_ref = impl_match.group(1).strip()
            if impl_ref in ["TBD", "TODO", "{IMPLEMENTATION_REFERENCE}", ""]:
                score -= 20
            else:
                # Check if referenced files exist
                refs = [ref.strip() for ref in impl_ref.split(',')]
                missing_refs = 0
                for ref in refs:
                    ref_path = self.project_root / ref
                    if not ref_path.exists():
                        missing_refs += 1
                
                if missing_refs > 0:
                    score -= (missing_refs / len(refs)) * 15
        
        # Check metadata alignment if available
        if metadata:
            spec_status = metadata.get("specification", {}).get("status", "")
            content_status = status_match.group(1).strip() if status_match else ""
            
            if spec_status and content_status and spec_status not in content_status:
                score -= 10
        
        return max(score, 0)
    
    def _calculate_freshness_score(self, content: str, metadata: Optional[Dict]) -> float:
        """Calculate freshness score based on last update and review dates."""
        score = 100.0
        
        # Extract last updated date from content
        updated_match = re.search(r'\*\*Status\*\*:.*\(([^)]+)\)', content)
        if updated_match:
            try:
                updated_str = updated_match.group(1)
                updated_date = datetime.strptime(updated_str, "%Y-%m-%d")
                days_old = (datetime.now() - updated_date).days
                
                # Deduct points based on age
                if days_old > 365:  # Over 1 year
                    score -= 50
                elif days_old > 180:  # Over 6 months
                    score -= 30
                elif days_old > 90:  # Over 3 months
                    score -= 15
                elif days_old > 30:  # Over 1 month
                    score -= 5
                
            except ValueError:
                score -= 20  # Invalid date format
        else:
            score -= 25  # No date found
        
        # Check metadata for additional freshness indicators
        if metadata:
            last_review = metadata.get("specification", {}).get("next_review")
            if last_review == "TBD":
                score -= 10
        
        return max(score, 0)
    
    def _calculate_validation_score(self, content: str) -> float:
        """Calculate validation score based on checklist and test references."""
        score = 0.0
        
        # Check for validation checklist
        checklist_match = re.search(r'## Validation Checklist\s*\n(.*?)(?=\n##|\n---|\Z)', content, re.DOTALL)
        if checklist_match:
            checklist_content = checklist_match.group(1)
            
            # Count checklist items
            checklist_items = len(re.findall(r'- \[ \]', checklist_content))
            if checklist_items >= 7:
                score += 40
            elif checklist_items >= 5:
                score += 30
            elif checklist_items >= 3:
                score += 20
            else:
                score += 10
        
        # Check for test references
        test_patterns = [
            r'tests/[^\s]+\.py',
            r'test_[^\s]+\.py',
            r'pytest',
            r'unittest',
            r'Test Coverage'
        ]
        
        test_refs = 0
        for pattern in test_patterns:
            test_refs += len(re.findall(pattern, content, re.IGNORECASE))
        
        if test_refs >= 5:
            score += 30
        elif test_refs >= 3:
            score += 20
        elif test_refs >= 1:
            score += 10
        
        # Check for acceptance criteria
        acceptance_criteria = len(re.findall(r'WHEN .+ THEN', content))
        if acceptance_criteria >= 5:
            score += 30
        elif acceptance_criteria >= 3:
            score += 20
        elif acceptance_criteria >= 1:
            score += 10
        
        return min(score, 100)
    
    def _load_metadata(self, spec_path: Path) -> Optional[Dict]:
        """Load metadata file for specification if it exists."""
        metadata_path = spec_path.parent / "metadata.yaml"
        
        if not metadata_path.exists():
            return None
        
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception:
            return None
    
    def _score_to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _generate_recommendations(self, completeness: float, alignment: float, 
                                freshness: float, validation: float) -> List[str]:
        """Generate improvement recommendations based on scores."""
        recommendations = []
        
        if completeness < 70:
            recommendations.append("Add missing required sections and increase content depth")
        
        if alignment < 70:
            recommendations.append("Update implementation references and verify file paths")
        
        if freshness < 70:
            recommendations.append("Update specification with recent changes and set review schedule")
        
        if validation < 70:
            recommendations.append("Expand validation checklist and add test references")
        
        if not recommendations:
            recommendations.append("Specification quality is good - maintain current standards")
        
        return recommendations
    
    def generate_quality_report(self) -> Dict:
        """Generate comprehensive quality report for all specifications."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_specifications": 0,
                "average_score": 0.0,
                "grade_distribution": {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
            },
            "specifications": []
        }
        
        total_score = 0.0
        spec_count = 0
        
        for spec_file in self.specs_dir.rglob("*.md"):
            if spec_file.name.startswith("README") or spec_file.name.startswith("SPECIFICATION"):
                continue
            
            spec_result = self.calculate_specification_score(spec_file)
            
            if "error" not in spec_result:
                spec_info = {
                    "name": spec_file.stem,
                    "path": str(spec_file.relative_to(self.project_root)),
                    **spec_result
                }
                
                report["specifications"].append(spec_info)
                total_score += spec_result["overall_score"]
                spec_count += 1
                
                # Update grade distribution
                grade = spec_result["grade"]
                report["summary"]["grade_distribution"][grade] += 1
        
        # Calculate summary statistics
        report["summary"]["total_specifications"] = spec_count
        if spec_count > 0:
            report["summary"]["average_score"] = round(total_score / spec_count, 2)
        
        return report


def main():
    """Main entry point for quality metrics tool."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Calculate TTA specification quality metrics")
    parser.add_argument("--spec", help="Path to specific specification file")
    parser.add_argument("--report", action="store_true", help="Generate comprehensive quality report")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    
    args = parser.parse_args()
    
    metrics = SpecificationQualityMetrics()
    
    if args.spec:
        # Calculate score for specific specification
        spec_path = Path(args.spec)
        result = metrics.calculate_specification_score(spec_path)
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if "error" in result:
                print(f"Error: {result['error']}")
            else:
                print(f"Specification Quality Report: {spec_path.name}")
                print("=" * 50)
                print(f"Overall Score: {result['overall_score']}/100 (Grade: {result['grade']})")
                print()
                print("Component Scores:")
                for component, score in result['scores'].items():
                    print(f"  {component.title()}: {score}/100")
                print()
                print("Recommendations:")
                for rec in result['recommendations']:
                    print(f"  - {rec}")
    
    elif args.report:
        # Generate comprehensive report
        report = metrics.generate_quality_report()
        
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print("TTA Specification Quality Report")
            print("=" * 50)
            print(f"Total Specifications: {report['summary']['total_specifications']}")
            print(f"Average Score: {report['summary']['average_score']}/100")
            print()
            print("Grade Distribution:")
            for grade, count in report['summary']['grade_distribution'].items():
                print(f"  {grade}: {count}")
            print()
            
            # Show top and bottom performers
            specs = sorted(report['specifications'], key=lambda x: x['overall_score'], reverse=True)
            
            if specs:
                print("Top Performers:")
                for spec in specs[:3]:
                    print(f"  {spec['name']}: {spec['overall_score']}/100 ({spec['grade']})")
                print()
                
                if len(specs) > 3:
                    print("Needs Improvement:")
                    for spec in specs[-3:]:
                        print(f"  {spec['name']}: {spec['overall_score']}/100 ({spec['grade']})")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
