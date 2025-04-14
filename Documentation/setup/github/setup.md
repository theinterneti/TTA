# GitHub Repository Setup Instructions

## Repository Organization

The TTA project consists of three repositories:

1. **TTA (meta-repository)**
   - Purpose: Integration and deployment management
   - Contains: Docker templates, setup scripts, documentation

2. **tta.dev (AI development framework)**
   - Purpose: Reusable AI development tools and patterns
   - Focus: Technical implementation of AI features

3. **TTA.prototype (Therapeutic Text Adventure)**
   - Purpose: TTA-specific implementation
   - Focus: Therapeutic content and user experience

## Initial Setup

1. Create a new repository on GitHub:
   - Go to https://github.com/new
   - Name: `TTA`
   - Description: `TTA meta-repository for managing tta.dev and TTA.prototype`
   - Choose public or private as needed
   - Do NOT initialize with README, .gitignore, or license

2. Add the remote and push:
   ```bash
   git remote add origin https://github.com/theinterneti/TTA.git
   git push -u origin main
   ```

3. Initialize the submodules:
   ```bash
   ./setup.sh
   ```

## Development Workflow

### AI Development (tta.dev)
1. Focus on reusable components
2. Document technical patterns
3. Maintain backward compatibility
4. Consider cross-project applicability

### TTA Implementation (TTA.prototype)
1. Focus on therapeutic content
2. Implement user experience
3. Use tools from tta.dev
4. Document content decisions

## Branching Strategy

### tta.dev
- main: Stable AI development tools
- feature/*: New AI capabilities
- fix/*: Technical fixes

### TTA.prototype
- main: Production-ready TTA
- content/*: New therapeutic content
- feature/*: TTA-specific features