import os
import sys
from urllib.parse import urlparse
import types
import unittest.mock as mock
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app_build", "backend")))

if "kafka" not in sys.modules:
    k_mod = types.ModuleType("kafka")
    k_err = types.ModuleType("kafka.errors")
    class _KafkaErr(Exception): pass
    class _KafkaConnErr(Exception): pass
    k_err.KafkaError = _KafkaErr
    k_err.KafkaConnectionError = _KafkaConnErr
    k_mod.KafkaProducer = mock.MagicMock()
    k_mod.KafkaConsumer = mock.MagicMock()
    k_mod.KafkaConsumer.return_value = []
    k_mod.errors = k_err
    sys.modules["kafka"] = k_mod
    sys.modules["kafka.errors"] = k_err

import app.kafka_client as app_kc
app_kc.start_consumer = mock.MagicMock()


TEST_DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg2://sentinel:sentinel_dev_2026@localhost:5432/sentinelmesh_test",
)
LIVE_DB_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg2://sentinel:sentinel_dev_2026@localhost:5432/sentinelmesh",
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

import app.db as app_db
from app.models import Base

app_db.url = TEST_DB_URL
app_db.engine = create_engine(TEST_DB_URL)
app_db.Session = sessionmaker(bind=app_db.engine)
Base.metadata.create_all(bind=app_db.engine)


from sqlalchemy.orm import close_all_sessions

@pytest.fixture(autouse=True)
def clean_test_db():
    assert_test_db(str(app_db.engine.url))
    close_all_sessions()
    with app_db.engine.connect() as conn:
        conn.execute(text("DELETE FROM messages; DELETE FROM trust_edges; DELETE FROM agents;"))
        conn.commit()
    yield
    close_all_sessions()
    with app_db.engine.connect() as conn:
        conn.execute(text("DELETE FROM messages; DELETE FROM trust_edges; DELETE FROM agents;"))
        conn.commit()


