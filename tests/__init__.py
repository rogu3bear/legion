"""Test bootstrap configuring stub modules."""
import sys
import types

# Stub heavy optional dependencies to prevent ImportError during tests
for name in [
    "sqlalchemy",
    "sqlalchemy.orm",
    "pydantic_settings",
    "email_validator",
    "discord",
    "discord.ext",
    "discord.ext.commands",
    "httpx",
    "zmq",
    "yaml",
]:
    if name not in sys.modules:
        module = types.ModuleType(name)
        if name.startswith("yaml"):
            def safe_load(_=None):
                return {}

            module.safe_load = safe_load
        if name == "email_validator":
            def validate_email(*args, **kwargs):
                return {
                    "email": args[0] if args else "test@example.com",
                    "local": "test",
                    "domain": "example.com",
                }

            module.validate_email = validate_email
        sys.modules[name] = module
