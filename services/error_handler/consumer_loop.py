import json
from consumer_config import consumer
from error_classifier import SensorErrorClassifier

classifier = SensorErrorClassifier()
consumer.subscribe(['sensor.zone-1'])

while True:
    msg = consumer.poll(1.0)
    if msg is None:
        continue

    reading = json.loads(msg.value())
    error = classifier.classify(reading)

    if error:
        print(f"[{error.upper()}] Skipping: {reading}")
    else:
        print(f"OK: {reading}")

    consumer.commit(msg)