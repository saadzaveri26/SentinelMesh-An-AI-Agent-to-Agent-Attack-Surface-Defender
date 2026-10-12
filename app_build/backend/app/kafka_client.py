import os
import json
import time
import threading
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError, KafkaConnectionError

servers = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

producer = None
_consumer_thread = None


def get_producer() -> KafkaProducer:
    global producer
    if producer is None:
        producer = KafkaProducer(
            bootstrap_servers=servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
    return producer


def publish(topic: str, payload: dict):
    get_producer().send(topic, value=payload)
    get_producer().flush()


def _consume_loop(topics: list[str], group: str, handler):
    c = None
    while c is None:
        try:
            c = KafkaConsumer(
                *topics,
                bootstrap_servers=servers,
                group_id=group,
                auto_offset_reset="earliest",
                value_deserializer=lambda x: json.loads(x.decode("utf-8")),
            )
        except (KafkaError, KafkaConnectionError):
            time.sleep(1)
    for msg in c:
        handler(msg.value)


def start_consumer(topics: list[str], group: str, handler):
    global _consumer_thread
    _consumer_thread = threading.Thread(
        target=_consume_loop, args=(topics, group, handler), daemon=True
    )
    _consumer_thread.start()
