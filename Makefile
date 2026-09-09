.PHONY: help install dev prod test clean docker docker-push health logs

help:
	@echo "AI Earth Economic Engine - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install        Install dependencies"
	@echo "  make dev           Run development server"
	@echo ""
	@echo "Docker:"
	@echo "  make docker        Build Docker image"
	@echo "  make docker-run    Run Docker container"
	@echo "  make docker-stop   Stop Docker container"
	@echo ""
	@echo "Production:"
	@echo "  make prod          Run production server with Gunicorn"
	@echo "  make logs          Tail application logs"
	@echo "  make health        Check service health"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean         Remove build artifacts and cache"

install:
	pip install -r requirements.txt
	@echo "✅ Dependencies installed"

dev: install
	python app.py

prod: install
	gunicorn --bind 0.0.0.0:8787 --workers 4 --timeout 60 wsgi:app

docker:
	docker build -t ai-earth:latest .
	@echo "✅ Docker image built: ai-earth:latest"

docker-run: docker
	docker run -d \
		--name ai-earth-engine \
		-p 8787:8787 \
		-e AI_EARTH_ADMIN_TOKEN=your-secure-token \
		ai-earth:latest
	@echo "✅ Docker container started on port 8787"

docker-stop:
	docker stop ai-earth-engine || true
	docker rm ai-earth-engine || true
	@echo "✅ Docker container stopped"

compose-up:
	docker-compose up -d
	@echo "✅ Docker Compose services started"

compose-down:
	docker-compose down
	@echo "✅ Docker Compose services stopped"

test:
	python -m pytest tests/ -v --tb=short

health:
	curl -s http://localhost:8787/health | python -m json.tool
	@echo ""

logs:
	tail -f /var/log/ai-earth/error.log 2>/dev/null || echo "Logs directory not found"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .pytest_cache/ .coverage htmlcov/
	@echo "✅ Cleanup complete"

.DEFAULT_GOAL := help
