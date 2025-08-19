"""
Automated API documentation generation.

This module provides comprehensive API documentation generation including
OpenAPI specifications, endpoint documentation, and interactive API explorers.
"""

import json
import yaml
import inspect
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, get_type_hints
from dataclasses import dataclass, field
from enum import Enum
import ast

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel

from ..monitoring.logging_config import get_logger


logger = get_logger(__name__)


class DocumentationFormat(str, Enum):
    """Documentation output formats."""
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"
    YAML = "yaml"
    OPENAPI = "openapi"


@dataclass
class EndpointDocumentation:
    """Documentation for a single API endpoint."""
    path: str
    method: str
    summary: str
    description: str
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    request_body: Optional[Dict[str, Any]] = None
    responses: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    examples: List[Dict[str, Any]] = field(default_factory=list)
    security: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    deprecated: bool = False


@dataclass
class SchemaDocumentation:
    """Documentation for data schemas."""
    name: str
    description: str
    properties: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    required: List[str] = field(default_factory=list)
    example: Optional[Dict[str, Any]] = None


class APIDocumentationGenerator:
    """Generates comprehensive API documentation."""
    
    def __init__(self, app: FastAPI, output_dir: str = "./docs/api"):
        self.app = app
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Documentation metadata
        self.metadata = {
            "title": "Player Experience Interface API",
            "version": "1.0.0",
            "description": "Comprehensive API for the TTA Player Experience Interface",
            "contact": {
                "name": "TTA Development Team",
                "email": "dev@tta.example.com"
            },
            "license": {
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT"
            }
        }
    
    def generate_all_documentation(self) -> Dict[str, str]:
        """Generate all types of API documentation."""
        generated_files = {}
        
        try:
            # Generate OpenAPI specification
            openapi_file = self.generate_openapi_spec()
            generated_files["openapi"] = str(openapi_file)
            
            # Generate Markdown documentation
            markdown_file = self.generate_markdown_docs()
            generated_files["markdown"] = str(markdown_file)
            
            # Generate HTML documentation
            html_file = self.generate_html_docs()
            generated_files["html"] = str(html_file)
            
            # Generate endpoint reference
            endpoint_file = self.generate_endpoint_reference()
            generated_files["endpoints"] = str(endpoint_file)
            
            # Generate schema documentation
            schema_file = self.generate_schema_docs()
            generated_files["schemas"] = str(schema_file)
            
            logger.info(f"Generated API documentation files: {list(generated_files.keys())}")
            
        except Exception as e:
            logger.error(f"Error generating API documentation: {e}", exc_info=True)
        
        return generated_files
    
    def generate_openapi_spec(self) -> Path:
        """Generate OpenAPI 3.0 specification."""
        openapi_schema = get_openapi(
            title=self.metadata["title"],
            version=self.metadata["version"],
            description=self.metadata["description"],
            routes=self.app.routes,
        )
        
        # Add additional metadata
        openapi_schema["info"].update({
            "contact": self.metadata["contact"],
            "license": self.metadata["license"],
            "termsOfService": "https://tta.example.com/terms",
        })
        
        # Add servers
        openapi_schema["servers"] = [
            {
                "url": "http://localhost:8080",
                "description": "Development server"
            },
            {
                "url": "https://api.tta.example.com",
                "description": "Production server"
            }
        ]
        
        # Add security schemes
        openapi_schema["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        }
        
        # Add tags
        openapi_schema["tags"] = [
            {
                "name": "Authentication",
                "description": "User authentication and authorization"
            },
            {
                "name": "Players",
                "description": "Player profile management"
            },
            {
                "name": "Characters",
                "description": "Character creation and management"
            },
            {
                "name": "Worlds",
                "description": "World selection and customization"
            },
            {
                "name": "Sessions",
                "description": "Therapeutic session management"
            },
            {
                "name": "Chat",
                "description": "Real-time chat interface"
            },
            {
                "name": "Progress",
                "description": "Progress tracking and analytics"
            }
        ]
        
        # Save as JSON
        json_file = self.output_dir / "openapi.json"
        with open(json_file, 'w') as f:
            json.dump(openapi_schema, f, indent=2)
        
        # Save as YAML
        yaml_file = self.output_dir / "openapi.yaml"
        with open(yaml_file, 'w') as f:
            yaml.dump(openapi_schema, f, default_flow_style=False)
        
        return json_file
    
    def generate_markdown_docs(self) -> Path:
        """Generate Markdown API documentation."""
        markdown_content = self._generate_markdown_content()
        
        markdown_file = self.output_dir / "api_reference.md"
        with open(markdown_file, 'w') as f:
            f.write(markdown_content)
        
        return markdown_file
    
    def _generate_markdown_content(self) -> str:
        """Generate the content for Markdown documentation."""
        content = []
        
        # Header
        content.append(f"# {self.metadata['title']}")
        content.append(f"Version: {self.metadata['version']}")
        content.append(f"Generated: {datetime.utcnow().isoformat()}")
        content.append("")
        content.append(self.metadata['description'])
        content.append("")
        
        # Table of Contents
        content.append("## Table of Contents")
        content.append("")
        content.append("- [Authentication](#authentication)")
        content.append("- [Endpoints](#endpoints)")
        content.append("- [Data Models](#data-models)")
        content.append("- [Error Handling](#error-handling)")
        content.append("- [Rate Limiting](#rate-limiting)")
        content.append("- [Examples](#examples)")
        content.append("")
        
        # Authentication
        content.append("## Authentication")
        content.append("")
        content.append("The API uses JWT (JSON Web Token) authentication. Include the token in the Authorization header:")
        content.append("")
        content.append("```")
        content.append("Authorization: Bearer <your-jwt-token>")
        content.append("```")
        content.append("")
        
        # Endpoints
        content.append("## Endpoints")
        content.append("")
        
        # Get OpenAPI schema for endpoint details
        openapi_schema = get_openapi(
            title=self.metadata["title"],
            version=self.metadata["version"],
            description=self.metadata["description"],
            routes=self.app.routes,
        )
        
        # Group endpoints by tags
        endpoints_by_tag = {}
        for path, path_item in openapi_schema.get("paths", {}).items():
            for method, operation in path_item.items():
                if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    tags = operation.get("tags", ["Untagged"])
                    for tag in tags:
                        if tag not in endpoints_by_tag:
                            endpoints_by_tag[tag] = []
                        endpoints_by_tag[tag].append({
                            "path": path,
                            "method": method.upper(),
                            "operation": operation
                        })
        
        # Generate documentation for each tag
        for tag, endpoints in endpoints_by_tag.items():
            content.append(f"### {tag}")
            content.append("")
            
            for endpoint in endpoints:
                path = endpoint["path"]
                method = endpoint["method"]
                operation = endpoint["operation"]
                
                content.append(f"#### {method} {path}")
                content.append("")
                
                # Summary and description
                if "summary" in operation:
                    content.append(f"**Summary:** {operation['summary']}")
                    content.append("")
                
                if "description" in operation:
                    content.append(operation["description"])
                    content.append("")
                
                # Parameters
                if "parameters" in operation:
                    content.append("**Parameters:**")
                    content.append("")
                    content.append("| Name | Type | Required | Description |")
                    content.append("|------|------|----------|-------------|")
                    
                    for param in operation["parameters"]:
                        name = param.get("name", "")
                        param_type = param.get("schema", {}).get("type", "string")
                        required = "Yes" if param.get("required", False) else "No"
                        description = param.get("description", "")
                        content.append(f"| {name} | {param_type} | {required} | {description} |")
                    
                    content.append("")
                
                # Request body
                if "requestBody" in operation:
                    content.append("**Request Body:**")
                    content.append("")
                    request_body = operation["requestBody"]
                    if "application/json" in request_body.get("content", {}):
                        schema = request_body["content"]["application/json"].get("schema", {})
                        content.append("```json")
                        content.append(json.dumps(self._generate_example_from_schema(schema), indent=2))
                        content.append("```")
                        content.append("")
                
                # Responses
                if "responses" in operation:
                    content.append("**Responses:**")
                    content.append("")
                    
                    for status_code, response in operation["responses"].items():
                        content.append(f"**{status_code}:** {response.get('description', '')}")
                        
                        if "content" in response and "application/json" in response["content"]:
                            schema = response["content"]["application/json"].get("schema", {})
                            content.append("")
                            content.append("```json")
                            content.append(json.dumps(self._generate_example_from_schema(schema), indent=2))
                            content.append("```")
                        
                        content.append("")
                
                content.append("---")
                content.append("")
        
        # Data Models
        content.append("## Data Models")
        content.append("")
        
        if "components" in openapi_schema and "schemas" in openapi_schema["components"]:
            for schema_name, schema in openapi_schema["components"]["schemas"].items():
                content.append(f"### {schema_name}")
                content.append("")
                
                if "description" in schema:
                    content.append(schema["description"])
                    content.append("")
                
                if "properties" in schema:
                    content.append("**Properties:**")
                    content.append("")
                    content.append("| Property | Type | Required | Description |")
                    content.append("|----------|------|----------|-------------|")
                    
                    required_props = schema.get("required", [])
                    for prop_name, prop_schema in schema["properties"].items():
                        prop_type = prop_schema.get("type", "object")
                        is_required = "Yes" if prop_name in required_props else "No"
                        description = prop_schema.get("description", "")
                        content.append(f"| {prop_name} | {prop_type} | {is_required} | {description} |")
                    
                    content.append("")
                
                # Example
                content.append("**Example:**")
                content.append("")
                content.append("```json")
                content.append(json.dumps(self._generate_example_from_schema(schema), indent=2))
                content.append("```")
                content.append("")
        
        # Error Handling
        content.append("## Error Handling")
        content.append("")
        content.append("The API uses standard HTTP status codes and returns error details in JSON format:")
        content.append("")
        content.append("```json")
        content.append(json.dumps({
            "error": "ValidationError",
            "message": "Invalid input data",
            "details": {
                "field": "email",
                "issue": "Invalid email format"
            }
        }, indent=2))
        content.append("```")
        content.append("")
        
        # Rate Limiting
        content.append("## Rate Limiting")
        content.append("")
        content.append("The API implements rate limiting to ensure fair usage:")
        content.append("")
        content.append("- **Per IP:** 100 requests per minute")
        content.append("- **Per User:** 1000 requests per hour")
        content.append("- **Burst Capacity:** 10 requests")
        content.append("")
        content.append("Rate limit headers are included in responses:")
        content.append("")
        content.append("```")
        content.append("X-RateLimit-Limit: 100")
        content.append("X-RateLimit-Remaining: 95")
        content.append("X-RateLimit-Reset: 1640995200")
        content.append("```")
        content.append("")
        
        return "\n".join(content)
    
    def _generate_example_from_schema(self, schema: Dict[str, Any]) -> Any:
        """Generate example data from JSON schema."""
        if "example" in schema:
            return schema["example"]
        
        schema_type = schema.get("type", "object")
        
        if schema_type == "object":
            example = {}
            properties = schema.get("properties", {})
            
            for prop_name, prop_schema in properties.items():
                example[prop_name] = self._generate_example_from_schema(prop_schema)
            
            return example
        
        elif schema_type == "array":
            items_schema = schema.get("items", {"type": "string"})
            return [self._generate_example_from_schema(items_schema)]
        
        elif schema_type == "string":
            if "format" in schema:
                if schema["format"] == "email":
                    return "user@example.com"
                elif schema["format"] == "date-time":
                    return "2023-01-01T00:00:00Z"
                elif schema["format"] == "uuid":
                    return "123e4567-e89b-12d3-a456-426614174000"
            return "string"
        
        elif schema_type == "integer":
            return 42
        
        elif schema_type == "number":
            return 3.14
        
        elif schema_type == "boolean":
            return True
        
        else:
            return None
    
    def generate_html_docs(self) -> Path:
        """Generate HTML API documentation."""
        html_content = self._generate_html_content()
        
        html_file = self.output_dir / "api_reference.html"
        with open(html_file, 'w') as f:
            f.write(html_content)
        
        return html_file
    
    def _generate_html_content(self) -> str:
        """Generate HTML content for API documentation."""
        # Convert markdown to HTML (simplified)
        markdown_content = self._generate_markdown_content()
        
        # Basic HTML wrapper
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.metadata['title']} - API Documentation</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        
        h1, h2, h3, h4 {{
            color: #2c3e50;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }}
        
        code {{
            background-color: #f8f9fa;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Monaco', 'Consolas', monospace;
        }}
        
        pre {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            border-left: 4px solid #007bff;
        }}
        
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
        }}
        
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        
        th {{
            background-color: #f8f9fa;
            font-weight: 600;
        }}
        
        .endpoint {{
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }}
        
        .method {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 3px;
            font-weight: bold;
            color: white;
            margin-right: 10px;
        }}
        
        .method.get {{ background-color: #28a745; }}
        .method.post {{ background-color: #007bff; }}
        .method.put {{ background-color: #ffc107; color: #000; }}
        .method.delete {{ background-color: #dc3545; }}
        .method.patch {{ background-color: #6f42c1; }}
        
        .toc {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        
        .toc ul {{
            list-style-type: none;
            padding-left: 0;
        }}
        
        .toc li {{
            margin: 5px 0;
        }}
        
        .toc a {{
            text-decoration: none;
            color: #007bff;
        }}
        
        .toc a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div id="content">
        {self._markdown_to_html(markdown_content)}
    </div>
    
    <script>
        // Add syntax highlighting and interactive features
        document.addEventListener('DOMContentLoaded', function() {{
            // Add method classes to endpoint headers
            const headers = document.querySelectorAll('h4');
            headers.forEach(header => {{
                const text = header.textContent;
                const methodMatch = text.match(/^(GET|POST|PUT|DELETE|PATCH)\\s/);
                if (methodMatch) {{
                    const method = methodMatch[1].toLowerCase();
                    const methodSpan = document.createElement('span');
                    methodSpan.className = `method ${{method}}`;
                    methodSpan.textContent = method.toUpperCase();
                    
                    const path = text.replace(methodMatch[0], '');
                    header.innerHTML = '';
                    header.appendChild(methodSpan);
                    header.appendChild(document.createTextNode(path));
                }}
            }});
        }});
    </script>
</body>
</html>
        """
        
        return html_content
    
    def _markdown_to_html(self, markdown: str) -> str:
        """Convert markdown to HTML (simplified implementation)."""
        # This is a very basic markdown to HTML converter
        # In production, use a proper markdown library like python-markdown
        
        html = markdown
        
        # Headers
        html = html.replace('# ', '<h1>').replace('\n# ', '</h1>\n<h1>')
        html = html.replace('## ', '<h2>').replace('\n## ', '</h2>\n<h2>')
        html = html.replace('### ', '<h3>').replace('\n### ', '</h3>\n<h3>')
        html = html.replace('#### ', '<h4>').replace('\n#### ', '</h4>\n<h4>')
        
        # Code blocks
        import re
        html = re.sub(r'```(\w+)?\n(.*?)\n```', r'<pre><code>\2</code></pre>', html, flags=re.DOTALL)
        
        # Inline code
        html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
        
        # Bold
        html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', html)
        
        # Tables (basic)
        lines = html.split('\n')
        in_table = False
        result_lines = []
        
        for line in lines:
            if '|' in line and not in_table:
                in_table = True
                result_lines.append('<table>')
                result_lines.append('<tr>')
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                for cell in cells:
                    result_lines.append(f'<th>{cell}</th>')
                result_lines.append('</tr>')
            elif '|' in line and in_table:
                if '---' in line:
                    continue  # Skip separator line
                result_lines.append('<tr>')
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                for cell in cells:
                    result_lines.append(f'<td>{cell}</td>')
                result_lines.append('</tr>')
            elif in_table and '|' not in line:
                in_table = False
                result_lines.append('</table>')
                result_lines.append(line)
            else:
                result_lines.append(line)
        
        if in_table:
            result_lines.append('</table>')
        
        html = '\n'.join(result_lines)
        
        # Paragraphs
        html = re.sub(r'\n\n', '</p>\n<p>', html)
        html = '<p>' + html + '</p>'
        
        # Clean up empty paragraphs
        html = re.sub(r'<p>\s*</p>', '', html)
        html = re.sub(r'<p>\s*(<h[1-6]>)', r'\1', html)
        html = re.sub(r'(</h[1-6]>)\s*</p>', r'\1', html)
        
        return html
    
    def generate_endpoint_reference(self) -> Path:
        """Generate detailed endpoint reference."""
        endpoints = self._extract_endpoint_documentation()
        
        reference_content = self._generate_endpoint_reference_content(endpoints)
        
        reference_file = self.output_dir / "endpoint_reference.md"
        with open(reference_file, 'w') as f:
            f.write(reference_content)
        
        return reference_file
    
    def _extract_endpoint_documentation(self) -> List[EndpointDocumentation]:
        """Extract detailed endpoint documentation from the FastAPI app."""
        endpoints = []
        
        openapi_schema = get_openapi(
            title=self.metadata["title"],
            version=self.metadata["version"],
            description=self.metadata["description"],
            routes=self.app.routes,
        )
        
        for path, path_item in openapi_schema.get("paths", {}).items():
            for method, operation in path_item.items():
                if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    endpoint = EndpointDocumentation(
                        path=path,
                        method=method.upper(),
                        summary=operation.get("summary", ""),
                        description=operation.get("description", ""),
                        parameters=operation.get("parameters", []),
                        request_body=operation.get("requestBody"),
                        responses=operation.get("responses", {}),
                        security=operation.get("security", []),
                        tags=operation.get("tags", []),
                        deprecated=operation.get("deprecated", False)
                    )
                    endpoints.append(endpoint)
        
        return endpoints
    
    def _generate_endpoint_reference_content(self, endpoints: List[EndpointDocumentation]) -> str:
        """Generate content for endpoint reference."""
        content = []
        
        content.append("# API Endpoint Reference")
        content.append(f"Generated: {datetime.utcnow().isoformat()}")
        content.append("")
        
        # Group by tags
        endpoints_by_tag = {}
        for endpoint in endpoints:
            tags = endpoint.tags if endpoint.tags else ["Untagged"]
            for tag in tags:
                if tag not in endpoints_by_tag:
                    endpoints_by_tag[tag] = []
                endpoints_by_tag[tag].append(endpoint)
        
        for tag, tag_endpoints in endpoints_by_tag.items():
            content.append(f"## {tag}")
            content.append("")
            
            for endpoint in tag_endpoints:
                content.append(f"### {endpoint.method} {endpoint.path}")
                content.append("")
                
                if endpoint.deprecated:
                    content.append("⚠️ **DEPRECATED** - This endpoint is deprecated and may be removed in future versions.")
                    content.append("")
                
                if endpoint.summary:
                    content.append(f"**Summary:** {endpoint.summary}")
                    content.append("")
                
                if endpoint.description:
                    content.append(endpoint.description)
                    content.append("")
                
                # Security requirements
                if endpoint.security:
                    content.append("**Security:** Requires authentication")
                    content.append("")
                
                # Parameters
                if endpoint.parameters:
                    content.append("**Parameters:**")
                    content.append("")
                    
                    for param in endpoint.parameters:
                        param_name = param.get("name", "")
                        param_in = param.get("in", "")
                        param_type = param.get("schema", {}).get("type", "string")
                        param_required = param.get("required", False)
                        param_desc = param.get("description", "")
                        
                        content.append(f"- **{param_name}** ({param_in}, {param_type})")
                        if param_required:
                            content.append("  - Required: Yes")
                        content.append(f"  - Description: {param_desc}")
                        content.append("")
                
                # Request body
                if endpoint.request_body:
                    content.append("**Request Body:**")
                    content.append("")
                    
                    if "content" in endpoint.request_body:
                        for content_type, content_schema in endpoint.request_body["content"].items():
                            content.append(f"Content-Type: `{content_type}`")
                            content.append("")
                            
                            if "schema" in content_schema:
                                schema = content_schema["schema"]
                                content.append("```json")
                                content.append(json.dumps(self._generate_example_from_schema(schema), indent=2))
                                content.append("```")
                                content.append("")
                
                # Responses
                if endpoint.responses:
                    content.append("**Responses:**")
                    content.append("")
                    
                    for status_code, response in endpoint.responses.items():
                        content.append(f"**{status_code}** - {response.get('description', '')}")
                        content.append("")
                        
                        if "content" in response:
                            for content_type, content_schema in response["content"].items():
                                if "schema" in content_schema:
                                    schema = content_schema["schema"]
                                    content.append("```json")
                                    content.append(json.dumps(self._generate_example_from_schema(schema), indent=2))
                                    content.append("```")
                                    content.append("")
                
                content.append("---")
                content.append("")
        
        return "\n".join(content)
    
    def generate_schema_docs(self) -> Path:
        """Generate data schema documentation."""
        schemas = self._extract_schema_documentation()
        
        schema_content = self._generate_schema_content(schemas)
        
        schema_file = self.output_dir / "data_schemas.md"
        with open(schema_file, 'w') as f:
            f.write(schema_content)
        
        return schema_file
    
    def _extract_schema_documentation(self) -> List[SchemaDocumentation]:
        """Extract schema documentation from the FastAPI app."""
        schemas = []
        
        openapi_schema = get_openapi(
            title=self.metadata["title"],
            version=self.metadata["version"],
            description=self.metadata["description"],
            routes=self.app.routes,
        )
        
        if "components" in openapi_schema and "schemas" in openapi_schema["components"]:
            for schema_name, schema_def in openapi_schema["components"]["schemas"].items():
                schema_doc = SchemaDocumentation(
                    name=schema_name,
                    description=schema_def.get("description", ""),
                    properties=schema_def.get("properties", {}),
                    required=schema_def.get("required", []),
                    example=self._generate_example_from_schema(schema_def)
                )
                schemas.append(schema_doc)
        
        return schemas
    
    def _generate_schema_content(self, schemas: List[SchemaDocumentation]) -> str:
        """Generate content for schema documentation."""
        content = []
        
        content.append("# Data Schema Reference")
        content.append(f"Generated: {datetime.utcnow().isoformat()}")
        content.append("")
        content.append("This document describes all data schemas used in the Player Experience Interface API.")
        content.append("")
        
        for schema in schemas:
            content.append(f"## {schema.name}")
            content.append("")
            
            if schema.description:
                content.append(schema.description)
                content.append("")
            
            if schema.properties:
                content.append("### Properties")
                content.append("")
                content.append("| Property | Type | Required | Description |")
                content.append("|----------|------|----------|-------------|")
                
                for prop_name, prop_def in schema.properties.items():
                    prop_type = prop_def.get("type", "object")
                    is_required = "Yes" if prop_name in schema.required else "No"
                    description = prop_def.get("description", "")
                    
                    # Handle complex types
                    if prop_type == "array" and "items" in prop_def:
                        items_type = prop_def["items"].get("type", "object")
                        prop_type = f"array[{items_type}]"
                    elif "$ref" in prop_def:
                        ref_name = prop_def["$ref"].split("/")[-1]
                        prop_type = f"[{ref_name}](#{ref_name.lower()})"
                    
                    content.append(f"| {prop_name} | {prop_type} | {is_required} | {description} |")
                
                content.append("")
            
            if schema.example:
                content.append("### Example")
                content.append("")
                content.append("```json")
                content.append(json.dumps(schema.example, indent=2))
                content.append("```")
                content.append("")
            
            content.append("---")
            content.append("")
        
        return "\n".join(content)


class OpenAPIGenerator:
    """Specialized OpenAPI specification generator."""
    
    def __init__(self, app: FastAPI):
        self.app = app
    
    def generate_enhanced_openapi(self) -> Dict[str, Any]:
        """Generate enhanced OpenAPI specification with additional metadata."""
        schema = get_openapi(
            title="Player Experience Interface API",
            version="1.0.0",
            description="Comprehensive API for therapeutic text adventure player experience",
            routes=self.app.routes,
        )
        
        # Add enhanced metadata
        schema["info"]["x-logo"] = {
            "url": "https://tta.example.com/logo.png",
            "altText": "TTA Logo"
        }
        
        # Add external documentation
        schema["externalDocs"] = {
            "description": "Full Documentation",
            "url": "https://docs.tta.example.com"
        }
        
        # Add custom extensions
        schema["x-api-id"] = "player-experience-api"
        schema["x-audience"] = "developers"
        schema["x-maturity"] = "stable"
        
        return schema