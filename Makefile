# Test tiers

.PHONY: test test-neo4j test-redis test-integration

# Unit tests only (fast)
test:
	uv run pytest -q

# Include Neo4j integration tests
test-neo4j:
	uv run pytest -q --neo4j

# Include Redis integration tests
test-redis:
	uv run pytest -q --redis

# Full integration (Neo4j + Redis)
test-integration:
	uv run pytest -q --neo4j --redis

# GitHub Integration helpers
.PHONY: github-setup github-check github-validate uv-setup uv-verify

# Setup UV environment
uv-setup:
	@./uv-manager.sh full

# Verify UV environment
uv-verify:
	@./uv-manager.sh verify

# Show UV environment info
uv-info:
	@./uv-manager.sh info

# Check GitHub workflows
github-check:
	@./github-workflow-validator.sh all

# Validate workflow syntax
github-validate:
	@./github-workflow-validator.sh syntax

# Full GitHub integration setup
github-setup: uv-setup
	@echo "✓ UV environment setup complete"
	@echo "→ Installing VS Code extensions..."
	@code --install-extension ms-python.python
	@code --install-extension github.vscode-pull-request-github
	@code --install-extension github.vscode-github-actions
	@code --install-extension eamodio.gitlens
	@echo "✓ Setup complete! Read GITHUB_INTEGRATION_COMPLETE.md for next steps"

# Quick start - everything you need
setup: github-setup
	@echo ""
	@echo "🎉 Setup complete! Try these commands:"
	@echo "  make test              - Run tests"
	@echo "  make github-check      - Check workflows"
	@echo "  ./uv-manager.sh        - Interactive UV manager"
	@echo ""

