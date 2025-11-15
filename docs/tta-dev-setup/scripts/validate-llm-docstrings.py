#!/usr/bin/env python3
"""
LLM-Friendly Docstring Validator

Uses an LLM to evaluate if docstrings are clear and understandable to AI agents.
Ensures the Agent-Computer Interface (ACI) is well-designed.

Usage:
    OPENAI_API_KEY=sk-... python scripts/validate-llm-docstrings.py

Requirements:
    - OPENAI_API_KEY environment variable
    - openai package (pip install openai)
"""

import ast
import os
import sys
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    sys.exit(1)


VALIDATION_PROMPT = """You are an expert at evaluating API documentation for AI agents.

Evaluate the following Python function docstring for clarity and usability by an LLM agent.

Function signature:
{signature}

Docstring:
{docstring}

Evaluate on these criteria (score 1-10 for each):
1. Clarity: Is it obvious what the function does?
2. Parameters: Are parameters clearly described with types?
3. Return value: Is the return value and type clear?
4. Examples: Are there usage examples?
5. Errors: Are potential errors described?

Respond in this exact format:
CLARITY: [score]/10 - [brief explanation]
PARAMETERS: [score]/10 - [brief explanation]
RETURN: [score]/10 - [brief explanation]
EXAMPLES: [score]/10 - [brief explanation]
ERRORS: [score]/10 - [brief explanation]
OVERALL: [score]/10
RECOMMENDATION: [Pass/Needs Improvement/Fail]
"""


def extract_functions_from_file(file_path: Path) -> list[tuple[str, str, str]]:
    """Extract function signatures and docstrings from Python file."""
    try:
        with file_path.open() as f:
            tree = ast.parse(f.read())
    except SyntaxError:
        return []

    functions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Get function signature
            args = []
            for arg in node.args.args:
                arg_name = arg.arg
                # Get type annotation if present
                type_hint = ""
                if arg.annotation:
                    type_hint = f": {ast.unparse(arg.annotation)}"
                args.append(f"{arg_name}{type_hint}")

            # Get return type if present
            return_type = ""
            if node.returns:
                return_type = f" -> {ast.unparse(node.returns)}"

            signature = f"def {node.name}({', '.join(args)}){return_type}"

            # Get docstring
            docstring = ast.get_docstring(node) or ""

            functions.append((node.name, signature, docstring))

    return functions


def validate_docstring_with_llm(
    client: OpenAI, func_name: str, signature: str, docstring: str
) -> dict[str, any]:
    """Use LLM to validate docstring clarity."""
    if not docstring:
        return {
            "overall_score": 0,
            "recommendation": "Fail",
            "reason": "No docstring present",
        }

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at evaluating API documentation for AI agents.",
                },
                {
                    "role": "user",
                    "content": VALIDATION_PROMPT.format(
                        signature=signature, docstring=docstring
                    ),
                },
            ],
            temperature=0.0,
        )

        result_text = response.choices[0].message.content

        # Parse the response
        lines = result_text.strip().split("\n")
        overall_score = 0
        recommendation = "Unknown"

        for line in lines:
            if line.startswith("OVERALL:"):
                score_text = line.split(":")[1].strip().split("/")[0]
                overall_score = int(score_text)
            elif line.startswith("RECOMMENDATION:"):
                recommendation = line.split(":")[1].strip()

        return {
            "overall_score": overall_score,
            "recommendation": recommendation,
            "details": result_text,
        }

    except Exception as e:
        return {"overall_score": 0, "recommendation": "Error", "reason": str(e)}


def main() -> int:
    """Main validation function."""

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return 1

    client = OpenAI(api_key=api_key)

    # Find all Python files in src/
    src_dir = Path("src")
    if not src_dir.exists():
        return 1

    python_files = list(src_dir.rglob("*.py"))

    total_functions = 0
    passed = 0
    needs_improvement = 0
    failed = 0

    for file_path in python_files:
        functions = extract_functions_from_file(file_path)

        if not functions:
            continue

        for func_name, signature, docstring in functions:
            total_functions += 1

            result = validate_docstring_with_llm(
                client, func_name, signature, docstring
            )

            recommendation = result.get("recommendation", "Unknown")
            result.get("overall_score", 0)

            if recommendation == "Pass":
                passed += 1
            elif recommendation == "Needs Improvement":
                needs_improvement += 1
            else:
                failed += 1

    # Print summary

    # Determine exit code
    if failed > 0:
        return 1
    if needs_improvement > 0:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
