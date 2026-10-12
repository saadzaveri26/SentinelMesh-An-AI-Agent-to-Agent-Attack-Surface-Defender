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

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app_build", "backend")))

from app.models import Base, Agent, Message, TrustEdge
from app.main import app
from app.db import get_db


def setup_db():
    eng = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=eng)
    sm = sessionmaker(bind=eng)
    return sm()


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

    m1 = Message(sender_id=a1.id, receiver_id=a2.id, content="benign task", threat_score=0.05, flagged=False)
    m2 = Message(sender_id=a2.id, receiver_id=a1.id, content="attack payload", threat_score=0.95, flagged=True)
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

    m1 = Message(sender_id=a1.id, receiver_id=a2.id, content="benign hello", threat_score=0.1, flagged=False)
    m2 = Message(sender_id=a2.id, receiver_id=a1.id, content="prompt injection ignore previous instructions", threat_score=0.98, flagged=True)
    db.add_all([m1, m2])
    db.commit()

    res = client.get("/api/dashboard/incidents")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["sender"] == "agent-y"
    assert data[0]["receiver"] == "agent-x"
    assert data[0]["threat_score"] == 0.98
    assert "prompt injection" in data[0]["content_preview"]
    app.dependency_overrides.clear()
