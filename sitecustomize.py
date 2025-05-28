import sys
import types
missing = [
    "yaml"
    "sqlalchemy"
    "pydantic_settings"
    "email_validator"
    "openai"
    "zmq"
    "httpx"
    "pytest"
    "jose"
    "discord"
    "dotenv"
    "passlib"
]
for name in missing:
    if name not in sys.modules:
        module = types.ModuleType(name)
        sys.modules[name] = module
        if name == "sqlalchemy":
            submods = ["orm", "engine", "ext", "sql"]
            for sub in submods:
                sys.modules[f"{name}.{sub}"] = types.ModuleType(f"{name}.{sub}")

# Prevent expensive imports during unittest discovery
placeholder_packages = [
    "core"
    "legion.orchestrator"
    "interface.api.v1.endpoints"
    "interface.core"
    "interface.db"
    "interface.models"
]
for pkg in placeholder_packages:
    if pkg not in sys.modules:
        sys.modules[pkg] = types.ModuleType(pkg)
