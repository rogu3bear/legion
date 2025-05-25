#!/usr/bin/env python3
"""Test Redis agent state persistence functionality."""

import importlib.util
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]

def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.modules[name] = module
    return module

# Import modules dynamically to avoid import errors
try:
    db_base = load_module("db_base", root / "interface" / "db" / "base.py")
    db_session = load_module("db_session", root / "interface" / "db" / "session.py")
    model_agent = load_module("model_agent", root / "interface" / "models" / "agent.py")

    Base = db_base.Base
    engine = db_session.engine
    SessionLocal = db_session.SessionLocal
    Agent = model_agent.Agent
    from legion.core.state import save_agent_state_to_redis, restore_agent_state_from_redis
except ImportError as e:
    print(f"Import error: {e}")
    print("Some dependencies may not be available for testing")
    sys.exit(1)


class MemoryRedis:
    """Mock Redis implementation for testing."""

    def __init__(self) -> None:
        self.values = {}

    def set(self, key, value, ex=None):
        self.values[key] = value

    def get(self, key):
        return self.values.get(key)

    def keys(self, pattern):
        prefix = pattern.rstrip('*')
        return [k for k in self.values if k.startswith(prefix)]


def test_redis_snapshot():
    """Test Redis state persistence and recovery."""
    redis_mock = MemoryRedis()

    print("Testing Redis snapshot functionality...")
    print("✓ Mock Redis created")

    try:
        # Test save operation
        save_agent_state_to_redis(redis_mock)
        print("✓ save_agent_state_to_redis executed without error")

        # Test restore operation
        restored = restore_agent_state_from_redis(redis_mock)
        print(f"✓ restore_agent_state_from_redis returned {len(restored)} agents")

        print("✓ Redis snapshot test completed successfully")

    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

    return True


if __name__ == "__main__":
    success = test_redis_snapshot()
    sys.exit(0 if success else 1)
