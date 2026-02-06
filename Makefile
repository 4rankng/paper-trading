.PHONY: help webapp-install webapp-dev webapp-build webapp-start dev prod

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

webapp-install: ## Install webapp dependencies
	cd webapp && npm install

webapp-dev: webapp-install ## Start webapp development server
	cd webapp && npm run dev

webapp-build: webapp-install ## Build webapp for production
	cd webapp && npm run build

webapp-start: ## Start webapp production server (requires build first)
	cd webapp && npm run start

dev: webapp-dev ## Alias for webapp-dev

prod: webapp-build webapp-start ## Build and start webapp in production mode
