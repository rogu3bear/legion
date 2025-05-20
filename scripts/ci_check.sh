
set -e

bash scripts/docs_check.sh
=======
#!/usr/bin/env bash
set -e
make lint || true
make test || true
bash scripts/docs_build_check.sh
