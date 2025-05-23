import json
import unittest
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from legion.agents.echo import EchoAgent, EventSchema
from memory.db.models import Base, EchoLog
from tests.stubs.fakeredis_stub import StrictRedis


class EchoAgentTests(unittest.TestCase):
    def test_log_inserts_db_and_returns_uuid(self):
        tmp_db = Path("memory/db/test_echo.db")
        engine = create_engine(f"sqlite:///{tmp_db}", connect_args={"check_same_thread": False})
        Base.metadata.create_all(engine)
        agent = EchoAgent(db_url=f"sqlite:///{tmp_db}")
        event = EventSchema(payload={"msg": "hi"})
        uid = agent.log(event)

        session = sessionmaker(bind=engine)()
        rows = session.query(EchoLog).all()
        session.close()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].id, uid)
        self.assertEqual(rows[0].payload, {"msg": "hi"})

    def test_log_with_redis_cache(self):
        tmp_db = Path("memory/db/test_echo2.db")
        engine = create_engine(f"sqlite:///{tmp_db}", connect_args={"check_same_thread": False})
        Base.metadata.create_all(engine)
        fake = StrictRedis()
        agent = EchoAgent(db_url=f"sqlite:///{tmp_db}", redis_url="redis://localhost")
        agent._redis = fake  # inject stub
        event = EventSchema(payload={"msg": "cached"})
        agent.log(event)
        self.assertIn("echo:log", fake.lists)
        logged = json.loads(fake.lists["echo:log"][0])
        self.assertEqual(logged, {"msg": "cached"})


if __name__ == "__main__":
    unittest.main()
