# Legion Makefile
.PHONY: dev lint test deploy logs clean test-agents test-core test-discord test-integration test-interface docs_refresh venv

venv:
        @echo "Activating virtual environment..."
        @echo "Note: This needs to be run with 'source', e.g.:"
        @echo "  source scripts/activate_once.sh"
        @echo "or"
        @echo "  source make venv"
        @bash scripts/activate_once.sh

dev:
        @echo "Starting backend and frontend..."
        bash scripts/activate_once.sh && \
        uvicorn interface.main:app --reload &
        npm --prefix ui/frontend run dev

lint:
        @echo "Running linters..."
        bash scripts/activate_once.sh && ruff check .
        npm --prefix ui/frontend run lint --if-present -- --max-warnings 0

test:
        @echo "Tests temporarily skipped"


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
