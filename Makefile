# GTA Analytics V2 - Build & Deploy Automation

# Variables
GATEWAY_IMAGE := gta-analytics-gateway
BACKEND_IMAGE := gta-analytics-backend
DOCKER_REGISTRY := registry.fly.io
FLY_ORG := personal

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

.PHONY: help
help: ## Show this help message
	@echo "$(GREEN)GTA Analytics V2 - Available Commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

# =========================
# Local Development
# =========================

.PHONY: build-local
build-local: ## Build Docker images locally
	@echo "$(GREEN)Building Gateway...$(NC)"
	docker build -t $(GATEWAY_IMAGE):latest ./gateway
	@echo "$(GREEN)Building Backend...$(NC)"
	docker build -t $(BACKEND_IMAGE):latest ./backend

.PHONY: up
up: ## Start services with docker-compose
	@echo "$(GREEN)Starting services...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)Services started! Gateway: http://localhost:8000 | Backend: http://localhost:3000$(NC)"

.PHONY: down
down: ## Stop services
	@echo "$(YELLOW)Stopping services...$(NC)"
	docker-compose down

.PHONY: logs
logs: ## View logs
	docker-compose logs -f

.PHONY: logs-gateway
logs-gateway: ## View Gateway logs
	docker-compose logs -f gateway

.PHONY: logs-backend
logs-backend: ## View Backend logs
	docker-compose logs -f backend

.PHONY: restart
restart: down up ## Restart services

.PHONY: clean
clean: ## Remove containers, images, and volumes
	@echo "$(YELLOW)Cleaning up...$(NC)"
	docker-compose down -v --remove-orphans
	docker rmi $(GATEWAY_IMAGE):latest $(BACKEND_IMAGE):latest 2>/dev/null || true

# =========================
# Testing
# =========================

.PHONY: test-gateway
test-gateway: ## Test Gateway health
	@echo "$(GREEN)Testing Gateway...$(NC)"
	curl -s http://localhost:8000/health | jq .
	curl -s http://localhost:8000/stats | jq .

.PHONY: test-backend
test-backend: ## Test Backend health
	@echo "$(GREEN)Testing Backend...$(NC)"
	curl -s http://localhost:3000/health | jq .
	curl -s http://localhost:3000/stats | jq .

.PHONY: test
test: test-gateway test-backend ## Test all services

# =========================
# Fly.io Deployment
# =========================

.PHONY: fly-auth
fly-auth: ## Login to Fly.io
	fly auth login

.PHONY: fly-create-gateway
fly-create-gateway: ## Create Gateway app on Fly.io
	@echo "$(GREEN)Creating Gateway app...$(NC)"
	cd gateway && fly apps create gta-analytics-gateway --org $(FLY_ORG)

.PHONY: fly-create-backend
fly-create-backend: ## Create Backend app on Fly.io
	@echo "$(GREEN)Creating Backend app...$(NC)"
	cd backend && fly apps create gta-analytics-backend --org $(FLY_ORG)
	@echo "$(YELLOW)Creating persistent volume for exports...$(NC)"
	fly volumes create gta_exports --region gru --size 1 --app gta-analytics-backend

.PHONY: fly-secrets
fly-secrets: ## Set secrets on Fly.io (requires .env file)
	@echo "$(YELLOW)Setting secrets for Backend...$(NC)"
	@if [ -f backend/.env ]; then \
		fly secrets set -a gta-analytics-backend \
			OPENAI_API_KEY=$$(grep OPENAI_API_KEY backend/.env | cut -d '=' -f2) \
			OPENROUTER_API_KEY=$$(grep OPENROUTER_API_KEY backend/.env | cut -d '=' -f2) \
			TOGETHER_API_KEY=$$(grep TOGETHER_API_KEY backend/.env | cut -d '=' -f2) \
			SILICONFLOW_API_KEY=$$(grep SILICONFLOW_API_KEY backend/.env | cut -d '=' -f2); \
	else \
		echo "$(YELLOW)No .env file found. Please create backend/.env with API keys.$(NC)"; \
	fi

.PHONY: fly-deploy-gateway
fly-deploy-gateway: ## Deploy Gateway to Fly.io
	@echo "$(GREEN)Deploying Gateway to Fly.io...$(NC)"
	cd gateway && fly deploy --ha=false

.PHONY: fly-deploy-backend
fly-deploy-backend: ## Deploy Backend to Fly.io
	@echo "$(GREEN)Deploying Backend to Fly.io...$(NC)"
	cd backend && fly deploy --ha=false

.PHONY: fly-deploy
fly-deploy: fly-deploy-gateway fly-deploy-backend ## Deploy both services to Fly.io

.PHONY: fly-status
fly-status: ## Check Fly.io deployment status
	@echo "$(GREEN)Gateway Status:$(NC)"
	fly status -a gta-analytics-gateway
	@echo "\n$(GREEN)Backend Status:$(NC)"
	fly status -a gta-analytics-backend

.PHONY: fly-logs-gateway
fly-logs-gateway: ## View Gateway logs on Fly.io
	fly logs -a gta-analytics-gateway

.PHONY: fly-logs-backend
fly-logs-backend: ## View Backend logs on Fly.io
	fly logs -a gta-analytics-backend

.PHONY: fly-ssh-gateway
fly-ssh-gateway: ## SSH into Gateway container
	fly ssh console -a gta-analytics-gateway

.PHONY: fly-ssh-backend
fly-ssh-backend: ## SSH into Backend container
	fly ssh console -a gta-analytics-backend

.PHONY: fly-destroy
fly-destroy: ## Destroy Fly.io apps (CAUTION!)
	@echo "$(YELLOW)WARNING: This will destroy both apps!$(NC)"
	@read -p "Are you sure? (yes/no): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		fly apps destroy gta-analytics-gateway --yes; \
		fly apps destroy gta-analytics-backend --yes; \
	fi

# =========================
# Development Tools
# =========================

.PHONY: shell-gateway
shell-gateway: ## Shell into Gateway container
	docker-compose exec gateway sh

.PHONY: shell-backend
shell-backend: ## Shell into Backend container
	docker-compose exec backend bash

.PHONY: ps
ps: ## Show running containers
	docker-compose ps

.PHONY: stats
stats: ## Show container resource usage
	docker stats --no-stream

# =========================
# Setup
# =========================

.PHONY: setup
setup: ## Initial setup (install dependencies)
	@echo "$(GREEN)Setting up project...$(NC)"
	@command -v docker >/dev/null 2>&1 || { echo "Docker not found. Please install Docker."; exit 1; }
	@command -v docker-compose >/dev/null 2>&1 || { echo "docker-compose not found. Please install docker-compose."; exit 1; }
	@command -v fly >/dev/null 2>&1 || { echo "$(YELLOW)Fly CLI not found. Install from https://fly.io/docs/hands-on/install-flyctl/$(NC)"; }
	@echo "$(GREEN)Setup complete! Run 'make up' to start services.$(NC)"
