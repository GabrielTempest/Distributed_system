import json

from confluent_kafka import Producer


producer = Producer({
    "bootstrap.servers": (
        "redpanda-1:9092,"
        "redpanda-2:9092,"
        "redpanda-3:9092"
    ),
    "acks": "all",
    "retries": 10,
    "enable.idempotence": True
})


def delivery_report(err, msg):
    if err:
        print(f"Delivery failed: {err}")
    else:
        print(
            f"Delivered to "
            f"{msg.topic()} "
            f"[partition={msg.partition()}]"
        )


def publish_event(topic: str, key: str, event: dict):
    producer.produce(
        topic=topic,
        key=key,
        value=json.dumps(event).encode("utf-8"),
        callback=delivery_report
    )
    producer.flush()