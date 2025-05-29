<!-- File: docs/ENVIRONMENT_SETUP.md -->

# Environment Setup

This guide lists required tooling for working with the Legion repository. Install these dependencies in your development environment before running tests or pre‑commit hooks.

## Required Tools

- **GitHub CLI (`gh`)** – used for automation and release scripts.
- **pre‑commit** – runs formatting and lint checks.
- **pytest** – executes the test suite.

## Installation Steps

The following example uses Debian/Ubuntu commands. Adapt as needed for your OS.

```bash
# GitHub CLI
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | \
  dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | \
  tee /etc/apt/sources.list.d/github-cli.list
apt update && apt install gh -y

# Python tooling
pip install pre-commit pytest pytest-cov
pre-commit install
```

Ensure these commands succeed before attempting `pre-commit run` or `pytest`.
