from confluent_kafka import Producer, Consumer
from common.config import KAFKA_BROKERS
import json

def make_producer():
    return Producer({
        "bootstrap.servers": KAFKA_BROKERS,
        "client.id": "dew-producer",
        "acks": "all",
    })

def make_consumer(group_id: str, topics: list[str]):
    c = Consumer({
        "bootstrap.servers": KAFKA_BROKERS,
        "group.id": group_id,
        "auto.offset.reset": "earliest",
        "enable.auto.commit": True,
    })
    c.subscribe(topics)
    return c

def send(producer, topic: str, key: str, value: dict):
    producer.produce(
        topic,
        key=key.encode("utf-8"),
        value=json.dumps(value, default=str).encode("utf-8"),
    )
    producer.poll(0)