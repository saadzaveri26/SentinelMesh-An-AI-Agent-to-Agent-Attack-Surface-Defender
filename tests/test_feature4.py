import os
import sys
import uuid
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

import unittest.mock as mock
import types
k_mod = types.ModuleType("kafka")
k_err = types.ModuleType("kafka.errors")
class _KafkaErr(Exception): pass
class _KafkaConnErr(Exception): pass
k_err.KafkaError = _KafkaErr
k_err.KafkaConnectionError = _KafkaConnErr
k_mod.KafkaProducer = mock.MagicMock()
k_mod.KafkaConsumer = mock.MagicMock()
k_mod.errors = k_err
sys.modules["kafka"] = k_mod
sys.modules["kafka.errors"] = k_err

from urllib.parse import urlparse
from sqlalchemy import text
import app.db as app_db

TEST_DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg2://sentinel:sentinel_dev_2026@localhost:5432/sentinelmesh_test",
)

def assert_test_db(url: str):
    parsed = urlparse(url)
    db_name = parsed.path.lstrip("/")
    if db_name == "sentinelmesh" or not db_name.endswith("_test"):
        raise RuntimeError(
            f"FATAL SAFETY VIOLATION: Tests must use a separate database! "
            f"Attempted to connect to '{db_name}'. Connecting to live database is forbidden."
        )

assert_test_db(TEST_DB_URL)
os.environ["DATABASE_URL"] = TEST_DB_URL

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app_build", "backend")))

from app.models import Base, Agent, Message, TrustEdge
from app.main import app
from app.db import get_db

app_db.url = TEST_DB_URL
app_db.engine = create_engine(TEST_DB_URL)
app_db.Session = sessionmaker(bind=app_db.engine)
Base.metadata.create_all(bind=app_db.engine)


from sqlalchemy.orm import close_all_sessions

def setup_db():
    assert_test_db(str(app_db.engine.url))
    close_all_sessions()
    with app_db.engine.connect() as conn:
        conn.execute(text("DELETE FROM messages; DELETE FROM trust_edges; DELETE FROM agents;"))
        conn.commit()
    return app_db.Session()





def test_dashboard_stats_empty():
    db = setup_db()
    app.dependency_overrides[get_db] = lambda: db
    client = TestClient(app)

    res = client.get("/api/dashboard/stats")
    assert res.status_code == 200
    data = res.json()
    assert data["active_agents"] == 0
    assert data["messages_inspected"] == 0
    assert data["messages_flagged"] == 0
    assert data["trust_edges"] == 0
    app.dependency_overrides.clear()


def test_dashboard_stats_populated():
    db = setup_db()
    app.dependency_overrides[get_db] = lambda: db
    client = TestClient(app)

    a1 = Agent(name="agent-alpha")
    a2 = Agent(name="agent-beta")
    db.add_all([a1, a2])
    db.flush()

    m1 = Message(sender_id=a1.id, receiver_id=a2.id, content="benign task", bert_score=0.05, flagged=False)
    m2 = Message(sender_id=a2.id, receiver_id=a1.id, content="attack payload", bert_score=0.95, flagged=True)
    edge = TrustEdge(source_id=a1.id, target_id=a2.id, score=0.6, interaction_count=5)
    db.add_all([m1, m2, edge])
    db.commit()

    res = client.get("/api/dashboard/stats")
    assert res.status_code == 200
    data = res.json()
    assert data["active_agents"] == 2
    assert data["messages_inspected"] == 2
    assert data["messages_flagged"] == 1
    assert data["trust_edges"] == 1
    app.dependency_overrides.clear()


def test_dashboard_graph():
    db = setup_db()
    app.dependency_overrides[get_db] = lambda: db
    client = TestClient(app)

    a1 = Agent(name="agent-1")
    a2 = Agent(name="agent-2")
    a3 = Agent(name="agent-3")
    db.add_all([a1, a2, a3])
    db.flush()

    e1 = TrustEdge(source_id=a1.id, target_id=a2.id, score=0.75, interaction_count=10)
    e2 = TrustEdge(source_id=a2.id, target_id=a3.id, score=0.40, interaction_count=3)
    e3 = TrustEdge(source_id=a3.id, target_id=a1.id, score=0.15, interaction_count=1)
    db.add_all([e1, e2, e3])
    db.commit()

    res = client.get("/api/dashboard/graph")
    assert res.status_code == 200
    data = res.json()
    assert len(data["nodes"]) == 3
    assert len(data["edges"]) == 3

    node_labels = {n["data"]["label"] for n in data["nodes"]}
    assert node_labels == {"agent-1", "agent-2", "agent-3"}

    edges_by_score = {round(e["data"]["score"], 2): e for e in data["edges"]}
    assert edges_by_score[0.75]["style"]["stroke"] == "#3DDC97"
    assert edges_by_score[0.75]["animated"] is False

    assert edges_by_score[0.40]["style"]["stroke"] == "#E8A33D"
    assert edges_by_score[0.40]["animated"] is False

    assert edges_by_score[0.15]["style"]["stroke"] == "#E5484D"
    assert edges_by_score[0.15]["animated"] is True
    app.dependency_overrides.clear()


def test_dashboard_incidents():
    db = setup_db()
    app.dependency_overrides[get_db] = lambda: db
    client = TestClient(app)

    a1 = Agent(name="agent-x")
    a2 = Agent(name="agent-y")
    db.add_all([a1, a2])
    db.flush()

    t1 = datetime(2026, 10, 12, 10, 0, 0, tzinfo=timezone.utc)
    t2 = datetime(2026, 10, 12, 10, 5, 0, tzinfo=timezone.utc)
    t3 = datetime(2026, 10, 12, 10, 2, 0, tzinfo=timezone.utc)

    m1 = Message(sender_id=a1.id, receiver_id=a2.id, content="benign hello", bert_score=0.1, flagged=False, anomaly_flags=[], timestamp=t1)
    m2 = Message(sender_id=a2.id, receiver_id=a1.id, content="prompt injection ignore previous instructions", bert_score=0.98, flagged=True, anomaly_flags=[], timestamp=t2)
    m3 = Message(sender_id=a1.id, receiver_id=a2.id, content="anomalous first contact", bert_score=0.05, flagged=False, anomaly_flags=["first_time", "rare_pair"], timestamp=t3)
    db.add_all([m1, m2, m3])
    db.commit()

    res = client.get("/api/dashboard/incidents")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2
    assert data[0]["sender"] == "agent-y"
    assert data[0]["receiver"] == "agent-x"
    assert data[0]["bert_score"] == 0.98
    assert data[0]["flagged"] is True
    assert "prompt injection" in data[0]["content_preview"]
    assert data[1]["sender"] == "agent-x"
    assert data[1]["receiver"] == "agent-y"
    assert data[1]["flagged"] is False
    assert data[1]["flag_name"] == "first_time"
    assert data[1]["anomaly_flags"] == ["first_time", "rare_pair"]
    app.dependency_overrides.clear()


if __name__ == "__main__":
    test_dashboard_stats_empty()
    test_dashboard_stats_populated()
    test_dashboard_graph()
    test_dashboard_incidents()
    print("All Feature 4 tests passed!")
