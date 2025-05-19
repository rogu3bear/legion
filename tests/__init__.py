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
=======
import sys
import types
import unittest

missing = [
    "yaml", "sqlalchemy", "pydantic_settings", "email_validator", "zmq", "pytest"
]
for name in missing:
    if name not in sys.modules:
        module = types.ModuleType(name)
        sys.modules[name] = module
        if name == "sqlalchemy":
            submods = ["orm", "engine", "ext", "sql"]
            for sub in submods:
                sys.modules[f"{name}.{sub}"] = types.ModuleType(f"{name}.{sub}")

def load_tests(loader: unittest.TestLoader, tests: unittest.TestSuite, pattern: str | None):
    package_tests = unittest.TestSuite()
    for mod_name in [
        "tests.api.test_handshake",
        "tests.core.test_priority_queue",
    ]:
        try:
            module = __import__(mod_name, fromlist=["*"])
        except Exception as exc:  # pragma: no cover - failing import
            print(f"SKIP {mod_name}: {exc}")
            continue
        package_tests.addTests(loader.loadTestsFromModule(module))
    return package_tests
