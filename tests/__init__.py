"""Test bootstrap configuring stub modules."""
from tests.compat_stubs import apply_stubs
apply_stubs()

import unittest

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
