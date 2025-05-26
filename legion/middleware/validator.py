"""Directive validation utilities.

This module reads ``legion/config/directives.yaml`` which defines the
directives available to each agent. The :func:`validate_directive`
function is used by the middleware pipeline documented in
``docs/middleware.md``.
"""

import logging

import yaml

# Assume directives.yaml is in legion/config/directives.yaml
DIRECTIVES_PATH = "legion/config/directives.yaml"

_loaded_directives: dict | None = None  # Cached directives configuration

logger = logging.getLogger(__name__)


def _load_directives_config() -> dict:
    """Load and cache the directives configuration."""
    global _loaded_directives
    if _loaded_directives is None:
        try:
            with open(DIRECTIVES_PATH) as f:
                _loaded_directives = yaml.safe_load(f)
            if not isinstance(_loaded_directives, dict):
                logger.warning("%s did not load as a dictionary", DIRECTIVES_PATH)
                _loaded_directives = {}
        except FileNotFoundError:
            logger.warning("%s not found. Directive validation permissive", DIRECTIVES_PATH)
            _loaded_directives = {}
        except yaml.YAMLError as e:
            logger.warning("Error parsing %s: %s", DIRECTIVES_PATH, e)
            _loaded_directives = {}
    return _loaded_directives


def validate_directive(payload: dict) -> dict:
    """Validate a single directive request.

    Parameters
    ----------
    payload:
        Dictionary with at least ``agent`` and ``directive`` keys.

    Returns
    -------
    dict
        ``{"is_valid": True}`` if permitted or ``{"is_valid": False, "reason": str}``.
    """
    # Load the directive rules once per process; subsequent calls reuse the
    # cached configuration in ``_loaded_directives``.
    directives_config = _load_directives_config()
    agent_name = payload.get("agent")
    directive_name = payload.get("directive")

    if not agent_name or not directive_name:
        result = {
            "is_valid": False,
            "reason": "Missing 'agent' or 'directive' in payload.",
        }
        logger.warning("Directive payload missing keys", extra={"payload": payload})
        return result

    agent_rules = directives_config.get(agent_name, {})
    allowed_directives = agent_rules.get("allowed_directives", [])

    if directive_name in allowed_directives:
        result = {"is_valid": True}
        logger.info("Directive valid", extra={"agent": agent_name, "directive": directive_name})
        return result
    else:
        result = {
            "is_valid": False,
            "reason": f"Directive '{directive_name}' not allowed for agent '{agent_name}'.",
        }
        logger.info("Directive invalid", extra={"agent": agent_name, "directive": directive_name})
        return result
