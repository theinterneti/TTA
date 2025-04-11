# GitHub Repository Setup Instructions

## Repository Organization

The TTA project consists of three repositories:

1. TTA (meta-repository)
   - Purpose: Integration and deployment management
   - Contains: Docker templates, setup scripts, documentation

2. tta.dev (AI development framework)
   - Purpose: Reusable AI development tools and patterns
   - Focus: Technical implementation of AI features

3. TTA.prototype (Therapeutic Text Adventure)
   - Purpose: TTA-specific implementation
   - Focus: Therapeutic content and user experience

## Initial Setup

1. Create repositories on GitHub:
   ```bash
   # Create the main repository
   git remote add origin https://github.com/theinterneti/TTA.git
   
   # Create the AI development repository
   cd tta.dev
   git remote add origin https://github.com/theinterneti/tta.dev.git
   
   # Create the TTA implementation repository
   cd ../TTA.prototype
   git remote add origin https://github.com/theinterneti/TTA.prototype.git
   ```

2. Push initial code:
   ```bash
   # From the root directory
   git push -u origin main
   git push --recurse-submodules=on-demand
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
