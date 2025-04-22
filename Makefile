# Legion Makefile
.PHONY: test deploy logs clean

test:
	@echo "Running full test suite..."
	./scripts/test.sh

deploy:
	@echo "Running deployment..."
	./scripts/deploy.sh

logs:
	@ls -lh scripts/logs/
	@tail -n 40 scripts/logs/* || true

clean:
	@echo "Cleaning logs..."
	rm -rf scripts/logs/* 