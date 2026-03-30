#!/usr/bin/env python3
"""

# Logseq: [[TTA.dev/Scripts/Direct_llm_code_generation]]
Direct LLM Code Generation - Fallback for OpenHands

This script provides a simple, reliable alternative to OpenHands for code generation
using direct LLM API calls (OpenRouter, OpenAI, Anthropic).

Usage:
    python scripts/direct_llm_code_generation.py "Create a Redis connection pool manager"
"""

import asyncio
import json
import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / ".env")


class DirectLLMCodeGenerator:
    """Simple code generator using direct LLM API calls."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "openrouter/deepseek/deepseek-chat-v3.1:free",
        base_url: str = "https://openrouter.ai/api/v1",
    ):
        """
        Initialize the code generator.

        Args:
            api_key: API key for the LLM provider (defaults to OPENROUTER_API_KEY env var)
            model: Model identifier (default: DeepSeek Chat V3.1 free)
            base_url: API base URL (default: OpenRouter)
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key required (set OPENROUTER_API_KEY environment variable)"
            )

        self.model = model
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=180.0)

    async def generate_code(
        self,
        task_description: str,
        output_file: Path | None = None,
        context: str | None = None,
    ) -> dict:
        """
        Generate code based on task description.

        Args:
            task_description: Natural language description of the code to generate
            output_file: Optional path to save generated code
            context: Optional additional context (e.g., existing code, requirements)

        Returns:
            dict with keys: 'code', 'explanation', 'filename', 'success'
        """
        # Build prompt
        prompt = self._build_prompt(task_description, context)

        # Call LLM API
        try:
            response = await self._call_llm(prompt)
            result = self._parse_response(response)

            # Save to file if requested
            if output_file and result.get("code"):
                output_file = Path(output_file)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                output_file.write_text(result["code"])
                result["saved_to"] = str(output_file)

            result["success"] = True
            return result

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "code": None,
                "explanation": None,
            }

    def _build_prompt(self, task_description: str, context: str | None = None) -> str:
        """Build the prompt for code generation."""
        prompt = f"""You are an expert Python developer. Generate clean, well-documented code based on the following task.

TASK:
{task_description}

"""
        if context:
            prompt += f"""CONTEXT:
{context}

"""

        prompt += """REQUIREMENTS:
1. Write production-quality Python code
2. Include comprehensive docstrings
3. Add type hints
4. Include error handling
5. Follow PEP 8 style guidelines
6. Add inline comments for complex logic

OUTPUT FORMAT:
Provide your response in the following JSON format:
{
    "filename": "suggested_filename.py",
    "code": "# Complete Python code here",
    "explanation": "Brief explanation of the implementation"
}

Generate the code now:"""

        return prompt

    async def _call_llm(self, prompt: str) -> dict:
        """Call the LLM API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Remove "openrouter/" prefix if present for API call
        model_name = self.model.replace("openrouter/", "")

        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "temperature": 0.7,
            "max_tokens": 4000,
        }

        response = await self.client.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        return response.json()

    def _parse_response(self, response: dict) -> dict:
        """Parse the LLM response."""
        try:
            content = response["choices"][0]["message"]["content"]

            # Try to extract JSON from response
            # Look for JSON block in markdown code fence
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
            elif "```" in content:
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
            else:
                # Try to parse entire content as JSON
                json_str = content.strip()

            # Remove any trailing tokens (like <｜begin▁of▁sentence｜>)
            # Find the last closing brace
            last_brace = json_str.rfind("}")
            if last_brace != -1:
                json_str = json_str[: last_brace + 1]

            result = json.loads(json_str)

            return {
                "filename": result.get("filename", "generated_code.py"),
                "code": result.get("code", ""),
                "explanation": result.get("explanation", ""),
            }

        except (json.JSONDecodeError, KeyError, IndexError) as e:
            # Fallback: return raw content
            return {
                "filename": "generated_code.py",
                "code": content,
                "explanation": f"Raw LLM output (parsing failed: {e})",
            }

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


async def main():
    """Main entry point for CLI usage."""
    if len(sys.argv) < 2:
        sys.exit(1)

    task_description = sys.argv[1]
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    if output_file:
        pass

    generator = DirectLLMCodeGenerator()

    try:
        result = await generator.generate_code(
            task_description=task_description,
            output_file=output_file,
        )

        if result["success"]:
            if "saved_to" in result:
                pass
        else:
            sys.exit(1)

    finally:
        await generator.close()


if __name__ == "__main__":
    asyncio.run(main())
