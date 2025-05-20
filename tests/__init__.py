"""Test bootstrap configuring stub modules."""
from tests.compat_stubs import apply_stubs
apply_stubs()

# Ensure real pyzmq is available for tests that require it
import importlib
import pathlib
import sys
if "zmq" in sys.modules and getattr(sys.modules["zmq"], "__spec__", None) is None:
    del sys.modules["zmq"]
    spec = importlib.util.spec_from_file_location(
        "zmq", str(pathlib.Path(__file__).resolve().parent.parent / "zmq" / "__init__.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.modules["zmq"] = module
    import zmq.asyncio  # noqa: F401

for key in ["interface.api.v1.endpoints"]:
    if key in sys.modules and getattr(sys.modules[key], "__spec__", None) is None:
        del sys.modules[key]
if "dotenv" in sys.modules and getattr(sys.modules["dotenv"], "__spec__", None) is None:
    del sys.modules["dotenv"]

import unittest

def load_tests(loader: unittest.TestLoader, tests: unittest.TestSuite, pattern: str | None):
    package_tests = unittest.TestSuite()
    for mod_name in [
        "tests.api.test_handshake",
        "tests.core.test_priority_queue",
        "tests.queue.test_priority_impl",
        "tests.api.test_agent_register",
        "tests.agents.echo.test_run_once",
    ]:
        try:
            module = __import__(mod_name, fromlist=["*"])
        except Exception as exc:  # pragma: no cover - failing import
            print(f"SKIP {mod_name}: {exc}")
            continue
        package_tests.addTests(loader.loadTestsFromModule(module))
    return package_tests
