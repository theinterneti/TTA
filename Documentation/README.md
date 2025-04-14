# TTA Documentation

## Documentation Structure

The TTA project documentation is organized into three main sections:

1. **Core Documentation** (this repository)
   ```
   docs/
   ├── setup/              # Setup and installation guides
   │   ├── ai-dev.md      # AI development setup
   │   ├── content-dev.md # Content development setup
   │   └── installation/  # Installation guides
   │
   ├── docker/             # Docker and container documentation
   │   ├── README.md      # Docker overview
   │   ├── orchestration.md # Container orchestration
   │   ├── codecarbon.md  # CodeCarbon integration
   │   └── environments/  # Environment-specific configs
   │
   ├── devcontainer/       # VS Code devcontainer documentation
   │   ├── setup.md       # Devcontainer setup
   │   └── troubleshooting.md # Troubleshooting guide
   │
   ├── architecture/      # System architecture
   │   ├── ai/           # AI system design
   │   ├── content/      # Content system design
   │   └── integration/  # Integration patterns
   │
   ├── development/      # Development guides
   │   ├── workflow/     # Development workflows
   │   ├── standards/    # Coding standards
   │   └── testing/      # Testing guidelines
   │
   └── api/             # API documentation
       ├── ml-models/   # ML model APIs
       └── content/     # Content management APIs
   ```

2. **AI Framework** (tta.dev/docs/)
   ```
   docs/
   ├── models/          # ML model documentation
   ├── training/        # Training pipelines
   ├── patterns/        # Technical patterns
   └── api/            # API references
   ```

3. **Therapeutic Content** (TTA.prototype/docs/)
   ```
   docs/
   ├── content/        # Content development
   ├── ux/            # User experience
   ├── integration/   # AI integration
   └── management/    # Content management
   ```

## Documentation Standards

1. **File Organization**
   - Use clear, descriptive filenames
   - Group related documents in directories
   - Include README.md in each directory

2. **Content Structure**
   - Start with a clear overview
   - Use consistent headings
   - Include practical examples
   - Link to related documents

3. **Code Examples**
   - Use language-specific syntax highlighting
   - Include comments for complex code
   - Provide complete, working examples

4. **Updates**
   - Keep documentation in sync with code
   - Mark outdated sections clearly
   - Include last update date
