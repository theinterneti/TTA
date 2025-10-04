# Makefile for TTA Comprehensive Test Battery
# Provides convenient commands for running comprehensive tests

.PHONY: help test-all test-standard test-adversarial test-load test-pipeline test-dashboard
.PHONY: test-quick test-full test-ci clean setup check-deps

# Default target
help:
	@echo "TTA Comprehensive Test Battery"
	@echo "=============================="
	@echo ""
	@echo "Available targets:"
	@echo "  help           - Show this help message"
	@echo "  setup          - Install dependencies and check environment"
	@echo "  check-deps     - Check if required services are running"
	@echo ""
	@echo "Test Execution:"
	@echo "  test-all       - Run all test categories with detailed reporting"
	@echo "  test-quick     - Run basic tests (standard only)"
	@echo "  test-full      - Run all tests with metrics and detailed reports"
	@echo "  test-ci        - Run tests suitable for CI/CD (no interactive components)"
	@echo ""
	@echo "Individual Test Categories:"
	@echo "  test-standard  - Run standard functionality tests"
	@echo "  test-adversarial - Run security and edge case tests"
	@echo "  test-load      - Run load and stress tests"
	@echo "  test-pipeline  - Run data pipeline validation"
	@echo "  test-dashboard - Run dashboard verification"
	@echo ""
	@echo "Utilities:"
	@echo "  clean          - Clean up test results and logs"
	@echo "  dry-run        - Show what would be executed without running"

# Setup and dependency checking
setup:
	@echo "Setting up TTA Comprehensive Test Battery..."
	pip install pytest pytest-asyncio aioredis neo4j psutil websockets aiohttp pyyaml
	@echo "Creating required directories..."
	mkdir -p testing/results/comprehensive_battery
	mkdir -p testing/logs
	@echo "Setup complete!"

check-deps:
	@echo "Checking dependencies..."
	@python -c "import redis; print('✓ Redis client available')" 2>/dev/null || echo "✗ Redis client not available"
	@python -c "import neo4j; print('✓ Neo4j driver available')" 2>/dev/null || echo "✗ Neo4j driver not available"
	@python -c "import psutil; print('✓ psutil available')" 2>/dev/null || echo "✗ psutil not available"
	@echo "Checking services..."
	@python -c "import redis; r=redis.Redis(); r.ping(); print('✓ Redis server running')" 2>/dev/null || echo "✗ Redis server not accessible"
	@echo "Dependency check complete!"

# Main test execution targets
test-all:
	@echo "Running all comprehensive tests..."
	python run_comprehensive_tests.py --all --detailed-report --log-level INFO

test-quick:
	@echo "Running quick test suite (standard tests only)..."
	python run_comprehensive_tests.py --categories standard --log-level WARNING

test-full:
	@echo "Running full comprehensive test suite with metrics..."
	python run_comprehensive_tests.py --all --detailed-report --metrics --log-level INFO

test-ci:
	@echo "Running CI-friendly test suite..."
	python run_comprehensive_tests.py --all --detailed-report --log-level WARNING --output-dir ./ci-results

# Individual test category targets
test-standard:
	@echo "Running standard functionality tests..."
	python run_comprehensive_tests.py --categories standard --detailed-report

test-adversarial:
	@echo "Running adversarial/security tests..."
	python run_comprehensive_tests.py --categories adversarial --detailed-report --log-level DEBUG

test-load:
	@echo "Running load and stress tests..."
	python run_comprehensive_tests.py --categories load_stress --detailed-report --metrics

test-pipeline:
	@echo "Running data pipeline validation..."
	python run_comprehensive_tests.py --categories data_pipeline --detailed-report

test-dashboard:
	@echo "Running dashboard verification..."
	python run_comprehensive_tests.py --categories dashboard --detailed-report --metrics

# Development and debugging targets
dry-run:
	@echo "Dry run - showing what would be executed..."
	python run_comprehensive_tests.py --all --dry-run

test-debug:
	@echo "Running tests in debug mode..."
	python run_comprehensive_tests.py --categories standard --log-level DEBUG --log-file debug.log

# Custom configuration targets
test-dev:
	@echo "Running tests with development configuration..."
	python run_comprehensive_tests.py --all --config config/comprehensive_test_config.yaml --max-concurrent 3

test-staging:
	@echo "Running tests for staging environment..."
	python run_comprehensive_tests.py --all --detailed-report --neo4j-uri bolt://staging-neo4j:7687 --redis-url redis://staging-redis:6379

# Utility targets
clean:
	@echo "Cleaning up test results and logs..."
	rm -rf testing/results/comprehensive_battery/*
	rm -rf testing/logs/*
	rm -f debug.log
	rm -rf ci-results/
	@echo "Cleanup complete!"

view-results:
	@echo "Recent test results:"
	@ls -la testing/results/comprehensive_battery/ 2>/dev/null || echo "No results found"

view-logs:
	@echo "Recent log files:"
	@ls -la testing/logs/ 2>/dev/null || echo "No logs found"

# Performance testing targets
test-performance:
	@echo "Running performance-focused tests..."
	python run_comprehensive_tests.py --categories load_stress --metrics --max-concurrent 10

test-security:
	@echo "Running security-focused tests..."
	python run_comprehensive_tests.py --categories adversarial --detailed-report

# Continuous integration targets
test-pr:
	@echo "Running tests suitable for pull request validation..."
	python run_comprehensive_tests.py --categories standard adversarial --detailed-report --timeout 180

test-nightly:
	@echo "Running comprehensive nightly test suite..."
	python run_comprehensive_tests.py --all --detailed-report --metrics --timeout 900

# Docker-based testing (if using containers)
test-docker:
	@echo "Running tests in Docker environment..."
	docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

# Report generation
generate-report:
	@echo "Generating standalone report from latest results..."
	python -c "from utils.report_generator import TestReportGenerator; import asyncio; asyncio.run(TestReportGenerator().generate_comprehensive_report([]))"

# Configuration validation
validate-config:
	@echo "Validating configuration file..."
	python -c "import yaml; yaml.safe_load(open('config/comprehensive_test_config.yaml'))"
	@echo "Configuration is valid!"

# Environment-specific shortcuts
local: test-all
dev: test-dev
staging: test-staging
ci: test-ci
quick: test-quick
full: test-full
