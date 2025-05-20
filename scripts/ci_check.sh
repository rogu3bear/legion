
set -e

bash scripts/docs_check.sh
=======
#!/usr/bin/env bash
set -e
make lint || true
make test || true
bash scripts/docs_build_check.sh
export PYTHONPATH="tests/stubs:$PYTHONPATH"
python -m unittest \
    tests.api.test_handshake \
    tests.queue.test_priority_impl \
    tests.api.test_agent_register \
    tests.agents.echo.test_run_once -v || exit 1
python -m legion.agents.echo.run_once --stub || true
python -m unittest tests.metrics.test_metrics_agent tests.api.test_metrics_summary -v
python -m legion.integrations.discord_bridge --once || true
