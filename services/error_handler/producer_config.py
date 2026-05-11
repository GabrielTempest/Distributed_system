# producer_config.py
from confluent_kafka import Producer

producer = Producer({
    'bootstrap.servers': 'localhost:9092',
    'acks': 'all',          # wait for all replicas to confirm
    'retries': 5,
    'retry.backoff.ms': 500
})