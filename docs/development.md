# Development Guide

## Environment Setup

### Virtual Environment

Legion uses a Python virtual environment to isolate dependencies. We provide scripts to make this setup easier:

```bash
# First-time setup
./scripts/dev_setup.sh

# For subsequent activations
source scripts/activate_once.sh
```

#### Preventing Duplicate Virtual Environment Activations

If you see multiple virtual environment prefixes in your shell prompt like `(venv) (venv)` or `((.venv) )`, you're experiencing a duplicate activation. This happens when:

1. Your IDE (VS Code, PyCharm) automatically activates the virtual environment
2. You manually activate it again via `source .venv/bin/activate`

This doesn't break functionality but can cause confusion. To avoid this:

- Always use our `source scripts/activate_once.sh` script, which checks if the environment is already active
- Or, disable automatic virtual environment activation in your IDE:
  - **VS Code**: Settings → Python › Terminal: Activate Environment → set to Off
  - **PyCharm**: Settings → Tools → Terminal → Activate virtualenv → uncheck

#### Fixing Duplicate Prompt Issues

If you're already seeing duplicate environment indicators in your prompt, you can fix it using one of these methods:

```bash
# Option 1: Complete environment reset (recommended)
source scripts/reset_venv.sh
# Then activate cleanly
source scripts/activate_once.sh

# Option 2: Use the auto-cleanup in activate_once.sh
# Our script detects and fixes double prompts
source scripts/activate_once.sh
```

Our improved `activate_once.sh` script will now detect duplicate prompt indicators and attempt to clean them up automatically.

### Sanity Checks

If you need to verify your environment:

```bash
# Deactivate any active environments
deactivate

# Use our safe activation script 
source scripts/activate_once.sh

# Verify the environment
echo "$VIRTUAL_ENV"  # Should show /path/to/Legion/.venv
which python        # Should show /path/to/Legion/.venv/bin/python
python -V           # Should show Python 3.x.x
```

## Development Workflow

### Validation

Before submitting changes, run the validation suite:

```bash
# Type checking
mypy legion/

# Style checking
flake8 legion/

# Tests
pytest -xvs tests/
```

Address any errors before submitting pull requests.

### Documentation

Update docs when making significant changes. The project uses Markdown for documentation.

## Troubleshooting

### Virtual Environment Issues

If you encounter issues with your virtual environment:

#### Complete Environment Reset

Use our reset script if you're experiencing persistent issues:

```bash
source scripts/reset_venv.sh
```

This will:
- Deactivate any active virtual environments
- Reset your shell prompt to remove duplicate indicators
- Provide instructions for cleanly activating the environment

#### Manual Reset

If needed, you can perform these steps manually:

1. Deactivate any active environments: `deactivate`
2. Remove the existing environment if needed: `rm -rf .venv`
3. Run the setup script again: `./scripts/dev_setup.sh` 