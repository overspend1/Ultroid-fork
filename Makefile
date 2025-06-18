# Ultroid Docker Makefile
# Easy management commands for Docker deployment

.PHONY: help build start stop restart logs shell clean update backup session deploy status stats health

# Default target
help:
	@echo "🐳 Ultroid Docker Management"
	@echo "============================="
	@echo ""
	@echo "📋 Available commands:"
	@echo "  make build     - Build Docker images"
	@echo "  make start     - Start all services"
	@echo "  make stop      - Stop all services"
	@echo "  make restart   - Restart Ultroid bot"
	@echo "  make logs      - View bot logs"
	@echo "  make shell     - Access bot shell"
	@echo "  make clean     - Clean up containers"
	@echo "  make update    - Update and restart"
	@echo "  make backup    - Backup database"
	@echo "  make session   - Generate session string"
	@echo "  make deploy    - Full deployment"
	@echo ""
	@echo "🔍 Status commands:"
	@echo "  make status    - Show service status"
	@echo "  make stats     - Show resource usage"
	@echo "  make health    - Health check"

# Build Docker images
build:
	@echo "🔨 Building Ultroid Docker image..."
	docker-compose build

# Start all services
start:
	@echo "🚀 Starting Ultroid services..."
	docker-compose up -d

# Stop all services
stop:
	@echo "⏹️ Stopping Ultroid services..."
	docker-compose down

# Restart Ultroid bot
restart:
	@echo "🔄 Restarting Ultroid bot..."
	docker-compose restart ultroid

# View logs
logs:
	@echo "📝 Showing Ultroid logs..."
	docker-compose logs -f ultroid

# Access shell
shell:
	@echo "🐚 Accessing Ultroid shell..."
	docker-compose exec ultroid bash

# Clean up
clean:
	@echo "🧹 Cleaning up containers and images..."
	docker-compose down --rmi all --volumes --remove-orphans

# Update and restart
update:
	@echo "⬆️ Updating Ultroid..."
	git pull
	docker-compose build
	docker-compose up -d

# Backup database
backup:
	@echo "💾 Backing up database..."
	mkdir -p backups
	docker-compose exec redis redis-cli BGSAVE
	docker cp ultroid-redis:/data/dump.rdb backups/redis-backup-$(shell date +%Y%m%d-%H%M%S).rdb
	@echo "✅ Backup completed in backups/ directory"

# Generate session string
session:
	@echo "🔑 Generating session string..."
	./generate-session.sh

# Full deployment
deploy:
	@echo "🚀 Starting full deployment..."
	./docker-deploy.sh

# Service status
status:
	@echo "📊 Service status:"
	docker-compose ps

# Resource stats
stats:
	@echo "� Resource usage:"
	docker stats --no-stream

# Health check
health:
	@echo "🔍 Health check:"
	@echo "Services:"
	@docker-compose ps
	@echo ""
	@echo "Ultroid status:"
	@docker-compose logs --tail=5 ultroid
	python3 run_tests.py --install-deps

# Install bot dependencies
install:
	@echo "📦 Installing bot dependencies..."
	pip3 install -r requirements.txt

# Run all tests
test:
	@echo "🧪 Running all tests..."
	python3 run_tests.py

# Run core tests
test-core:
	@echo "🧪 Running core tests..."
	python3 run_tests.py --directory "tests/test_core"

# Run plugin tests
test-plugins:
	@echo "🧪 Running plugin tests..."
	python3 run_tests.py --directory "tests/test_plugins"
	pytest tests/test_plugins.py -v

# Run database tests
test-database: test-deps
	@echo "🧪 Running database tests..."
	pytest tests/test_database.py -v -m "not slow"

# Run update tests
test-updates: test-deps
	@echo "🧪 Running update tests..."
	pytest tests/test_updates.py -v

# Run tests with coverage
coverage: test-deps
	@echo "📊 Running tests with coverage..."
	pytest tests/ --cov=pyUltroid --cov-report=html --cov-report=term-missing --cov-fail-under=70
	@echo "📊 Coverage report available at htmlcov/index.html"

# Lint code
lint:
	@echo "🔍 Running linting checks..."
	python -m flake8 pyUltroid/ plugins/ --max-line-length=88 --ignore=E203,W503,F401
	python -m pylint pyUltroid/ --disable=C0114,C0115,C0116,R0903,R0913

# Format code
format:
	@echo "✨ Formatting code..."
	python -m black pyUltroid/ plugins/ tests/ --line-length=88
	python -m isort pyUltroid/ plugins/ tests/ --profile=black

# Run all quality checks
check: lint
	@echo "✅ Running all quality checks..."
	python -m mypy pyUltroid/ --ignore-missing-imports

# Clean temporary files
clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .coverage htmlcov/ .mypy_cache
	@echo "✅ Cleanup complete!"

# Quick test for specific component
test-quick:
	@echo "🚀 Quick test runner available:"
	@echo "Usage: python quick_test.py [component]"
	@echo "Example: python quick_test.py core"

# Test with specific markers
test-unit:
	pytest tests/ -m "unit" -v

test-integration:
	pytest tests/ -m "integration" -v

test-slow:
	pytest tests/ -m "slow" -v

# Development setup
dev-setup: install test-deps
	@echo "🔧 Development environment setup complete!"
	@echo "💡 Run 'make test' to verify everything works"

# CI/CD simulation
ci: test-deps lint test coverage
	@echo "🎯 CI/CD checks complete!"
