# consumer_config.py
from confluent_kafka import Consumer

consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'sensor-group',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False   # manual commit
})   # commit only when you're sure it's handled