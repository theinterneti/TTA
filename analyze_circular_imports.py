#!/usr/bin/env python3
"""
Circular Import Dependency Analysis Tool

This script analyzes the codebase to identify circular import dependencies
and provides recommendations for resolving them.
"""

import os
import sys
import ast
import re
from typing import Dict, Set, List, Tuple
from collections import defaultdict, deque
from pathlib import Path

class ImportAnalyzer:
    """Analyzes Python files for import dependencies."""
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.imports = defaultdict(set)  # module -> set of imported modules
        self.reverse_imports = defaultdict(set)  # module -> set of modules that import it
        self.file_to_module = {}  # file path -> module name
        self.module_to_file = {}  # module name -> file path
        
    def analyze_directory(self, directory: str = "src") -> None:
        """Analyze all Python files in the given directory."""
        src_path = self.root_path / directory
        
        if not src_path.exists():
            print(f"Directory {src_path} does not exist")
            return
            
        # First pass: map files to modules
        for py_file in src_path.rglob("*.py"):
            if py_file.name == "__init__.py":
                # For __init__.py files, use the parent directory as module name
                module_name = self._path_to_module(py_file.parent, src_path)
            else:
                module_name = self._path_to_module(py_file.with_suffix(""), src_path)
            
            self.file_to_module[str(py_file)] = module_name
            self.module_to_file[module_name] = str(py_file)
        
        # Second pass: analyze imports
        for py_file in src_path.rglob("*.py"):
            self._analyze_file(py_file)
    
    def _path_to_module(self, path: Path, src_path: Path) -> str:
        """Convert file path to module name."""
        relative_path = path.relative_to(src_path)
        return str(relative_path).replace(os.sep, ".")
    
    def _analyze_file(self, file_path: Path) -> None:
        """Analyze imports in a single Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            current_module = self.file_to_module[str(file_path)]
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imported_module = alias.name
                        if self._is_internal_module(imported_module):
                            self.imports[current_module].add(imported_module)
                            self.reverse_imports[imported_module].add(current_module)
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imported_module = node.module
                        if self._is_internal_module(imported_module):
                            self.imports[current_module].add(imported_module)
                            self.reverse_imports[imported_module].add(current_module)
                    
                    # Handle relative imports
                    if node.level > 0:
                        base_module = self._resolve_relative_import(current_module, node.level)
                        if node.module:
                            imported_module = f"{base_module}.{node.module}"
                        else:
                            imported_module = base_module
                        
                        if self._is_internal_module(imported_module):
                            self.imports[current_module].add(imported_module)
                            self.reverse_imports[imported_module].add(current_module)
        
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
    
    def _is_internal_module(self, module_name: str) -> bool:
        """Check if a module is internal to the project."""
        return (module_name.startswith("src.") or 
                module_name.startswith("components.") or
                module_name.startswith("player_experience.") or
                module_name in self.module_to_file)
    
    def _resolve_relative_import(self, current_module: str, level: int) -> str:
        """Resolve relative import to absolute module name."""
        parts = current_module.split(".")
        if level >= len(parts):
            return ""
        return ".".join(parts[:-level])
    
    def find_circular_dependencies(self) -> List[List[str]]:
        """Find all circular dependencies using DFS."""
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(module: str, path: List[str]) -> None:
            if module in rec_stack:
                # Found a cycle
                cycle_start = path.index(module)
                cycle = path[cycle_start:] + [module]
                cycles.append(cycle)
                return
            
            if module in visited:
                return
            
            visited.add(module)
            rec_stack.add(module)
            path.append(module)
            
            for imported_module in self.imports.get(module, set()):
                dfs(imported_module, path.copy())
            
            rec_stack.remove(module)
        
        for module in self.imports:
            if module not in visited:
                dfs(module, [])
        
        return cycles
    
    def analyze_module_complexity(self) -> Dict[str, int]:
        """Analyze module complexity based on import count."""
        complexity = {}
        for module in self.imports:
            import_count = len(self.imports[module])
            reverse_import_count = len(self.reverse_imports[module])
            complexity[module] = import_count + reverse_import_count
        return complexity
    
    def suggest_refactoring(self, cycles: List[List[str]]) -> List[str]:
        """Suggest refactoring strategies for circular dependencies."""
        suggestions = []
        
        for cycle in cycles:
            suggestions.append(f"\nCircular dependency detected: {' -> '.join(cycle)}")
            
            # Analyze the cycle to suggest solutions
            if len(cycle) == 3:  # Simple A -> B -> A cycle
                suggestions.append("  Suggested solutions:")
                suggestions.append("  1. Extract common interfaces/abstractions")
                suggestions.append("  2. Use dependency injection")
                suggestions.append("  3. Move shared code to a separate module")
            
            elif any("models" in module for module in cycle):
                suggestions.append("  Suggested solutions:")
                suggestions.append("  1. Move model definitions to a separate models module")
                suggestions.append("  2. Use forward references (TYPE_CHECKING)")
                suggestions.append("  3. Separate data models from business logic")
            
            elif any("services" in module for module in cycle):
                suggestions.append("  Suggested solutions:")
                suggestions.append("  1. Create abstract service interfaces")
                suggestions.append("  2. Use dependency injection container")
                suggestions.append("  3. Implement observer pattern for service communication")
            
            else:
                suggestions.append("  Suggested solutions:")
                suggestions.append("  1. Refactor to use dependency injection")
                suggestions.append("  2. Create abstract interfaces")
                suggestions.append("  3. Move shared functionality to utilities")
        
        return suggestions

def main():
    """Main analysis function."""
    print("Circular Import Dependency Analysis")
    print("=" * 50)
    
    # Get the project root directory
    current_dir = Path(__file__).parent
    project_root = current_dir
    
    # Initialize analyzer
    analyzer = ImportAnalyzer(str(project_root))
    
    # Analyze the codebase
    print("Analyzing codebase...")
    analyzer.analyze_directory("src")
    
    print(f"Found {len(analyzer.imports)} modules")
    print(f"Total import relationships: {sum(len(imports) for imports in analyzer.imports.values())}")
    
    # Find circular dependencies
    print("\nSearching for circular dependencies...")
    cycles = analyzer.find_circular_dependencies()
    
    if cycles:
        print(f"\n🚨 CRITICAL: Found {len(cycles)} circular dependencies!")
        print("=" * 60)
        
        for i, cycle in enumerate(cycles, 1):
            print(f"\nCircular Dependency #{i}:")
            print("  " + " -> ".join(cycle))
            
            # Show file paths for better understanding
            print("  File paths:")
            for module in cycle[:-1]:  # Exclude the duplicate last module
                file_path = analyzer.module_to_file.get(module, "Unknown")
                print(f"    {module}: {file_path}")
        
        # Provide refactoring suggestions
        suggestions = analyzer.suggest_refactoring(cycles)
        print("\n" + "=" * 60)
        print("REFACTORING SUGGESTIONS:")
        for suggestion in suggestions:
            print(suggestion)
        
        # Analyze module complexity
        print("\n" + "=" * 60)
        print("MODULE COMPLEXITY ANALYSIS:")
        complexity = analyzer.analyze_module_complexity()
        sorted_modules = sorted(complexity.items(), key=lambda x: x[1], reverse=True)
        
        print("Top 10 most complex modules (by import relationships):")
        for module, score in sorted_modules[:10]:
            imports_count = len(analyzer.imports.get(module, set()))
            reverse_count = len(analyzer.reverse_imports.get(module, set()))
            print(f"  {module}: {score} total ({imports_count} imports, {reverse_count} imported by)")
        
        return False  # Indicate failure
    
    else:
        print("\n✅ No circular dependencies found!")
        
        # Still show complexity analysis
        print("\nMODULE COMPLEXITY ANALYSIS:")
        complexity = analyzer.analyze_module_complexity()
        sorted_modules = sorted(complexity.items(), key=lambda x: x[1], reverse=True)
        
        print("Top 5 most complex modules:")
        for module, score in sorted_modules[:5]:
            imports_count = len(analyzer.imports.get(module, set()))
            reverse_count = len(analyzer.reverse_imports.get(module, set()))
            print(f"  {module}: {score} total ({imports_count} imports, {reverse_count} imported by)")
        
        return True  # Indicate success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
