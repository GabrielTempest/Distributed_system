import os

KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "localhost:19092")
DB_DSN = "host=127.0.0.1 port=5433 dbname=disaster_warning user=dew password=dew_pass"
# Topics
TOPIC_SENSOR_RAW = "sensor.raw"
TOPIC_SENSOR_VALIDATED = "sensor.validated"
TOPIC_ALERT_LOCAL = "alert.local"
TOPIC_ALERT_NEIGHBOR = "alert.neighbor"
TOPIC_ALERT_HEAD = "alert.head"
TOPIC_LOG_EVENTS = "log.events"
TOPIC_DLQ_PREFIX = "dlq."

# Areas (simulating geographic regions)
AREAS = ["area_1", "area_2", "area_3"]
NEIGHBORS = {
    "area_1": ["area_2"],
    "area_2": ["area_1", "area_3"],
    "area_3": ["area_2"],
}

# Anomaly thresholds
TEMP_CRITICAL = 60.0
SEISMIC_CRITICAL = 5.0
WATER_CRITICAL = 3.0
ROLLING_WINDOW = 20
ANOMALY_STDDEV_MULT = 3.0