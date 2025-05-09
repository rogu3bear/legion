#!/usr/bin/env bash
# Reset virtual environment script
# Completely cleans up the shell environment and prompt

# Attempt to deactivate any active environment
if [[ -n "$VIRTUAL_ENV" ]]; then
  echo "Deactivating current virtual environment: $VIRTUAL_ENV"
  deactivate || true
fi

# Clean up any PS1 duplications by exporting a clean prompt
# Note: This is zsh-compatible but can be customized for your shell
if [[ "$SHELL" == *"zsh"* ]]; then
  # For zsh
  export PS1="%n@%m %1~ %# "
else
  # For bash
  export PS1="\u@\h:\w\$ "
fi

echo "Environment reset complete. Your prompt has been cleaned."
echo "To activate the Legion virtual environment, run: source scripts/activate_once.sh" 