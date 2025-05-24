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

db_base = load_module("db_base", root / "interface" / "db" / "base.py")
db_session = load_module("db_session", root / "interface" / "db" / "session.py")
model_agent = load_module("model_agent", root / "interface" / "models" / "agent.py")

Base = db_base.Base
engine = db_session.engine
SessionLocal = db_session.SessionLocal
Agent = model_agent.Agent
from legion.core.state import save_agent_state_to_redis, restore_agent_state_from_redis


class MemoryRedis:
    def __init__(self) -> None:
        self.values = {}

    def set(self, key, value, ex=None):
        self.values[key] = value

    def get(self, key):
        return self.values.get(key)

    def keys(self, pattern):
        prefix = pattern.rstrip('*')
        return [k for k in self.values if k.startswith(prefix)]


def main() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    session.add_all([Agent(name="a1", model="m"), Agent(name="a2", model="m")])
    session.commit()
    r = MemoryRedis()
    save_agent_state_to_redis(r)

    session.query(Agent).delete()
    session.commit()

    restore_agent_state_from_redis(r)
    count = session.query(Agent).count()
    assert count == 2
    print("redis snapshot test: PASS")


if __name__ == "__main__":
    main()

