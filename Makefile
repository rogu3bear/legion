# Legion Makefile
.PHONY: test deploy logs clean test-agents test-core test-discord test-integration test-interface docs_refresh

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
