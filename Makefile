.PHONY: help webapp-install webapp-dev dev

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

webapp-install: ## Install webapp dependencies
	cd webapp && npm install

webapp-dev: webapp-install ## Start webapp development server
	cd webapp && npm run dev

dev: webapp-dev ## Alias for webapp-dev
