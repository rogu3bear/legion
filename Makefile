# Legion Makefile
.PHONY: test deploy logs clean test-agents test-core test-discord test-integration test-interface docs_refresh venv dev backend frontend lint

-include .env.ports

PORT_API ?= $(PORT_ALLOCATOR_UI_BACKEND)
PORT_UI ?= $(PORT_ALLOCATOR_UI_FRONTEND)

venv:
	@echo "Activating virtual environment..."
	@echo "Note: This needs to be run with 'source', e.g.:"
	@echo "  source scripts/activate_once.sh"
	@echo "or"
	@echo "  source make venv"
	@bash scripts/activate_once.sh

test: test-agents test-core test-discord test-integration test-interface
	@echo "All tests passed."

test-agents:
	@echo "Running agent tests..."
	@pytest --maxfail=1 --disable-warnings -q tests/agents/ tests/test_architect_agent.py

test-core:
	@echo "Running core tests..."
	@pytest --maxfail=1 --disable-warnings -q tests/core/

test-discord:
	@echo "Running Discord integration tests..."
	@pytest --maxfail=1 --disable-warnings -q tests/discord/

test-integration:
	@echo "Running orchestrator integration tests..."
	@pytest --maxfail=1 --disable-warnings -q tests/integration/ tests/test_orchestrator.py tests/test_orchestrator_lock.py

test-interface:
	@echo "Running interface tests..."
	@pytest --maxfail=1 --disable-warnings -q tests/api/ tests/test_websockets.py tests/test_interface.py

deploy:
	@echo "Running deployment..."
	./scripts/deploy.sh

logs:
	@ls -lh scripts/logs/
	@tail -n 40 scripts/logs/* || true

clean:
	@echo "Cleaning logs..."
	rm -rf scripts/logs/*

docs_refresh:
	@echo "Updating port map in docs..."
	python3 scripts/doc_ports.py

dev: backend frontend

backend:
	uvicorn interface.main:app --port $(PORT_API) --reload

frontend:
	cd ui/frontend && vite --port $(PORT_UI)

lint:
	ruff check .
	npx eslint ui/frontend/src --ext .jsx,.js || true
