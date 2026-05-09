import json
import psycopg2
from psycopg2.extras import Json
from common.kafka_client import make_consumer
from common.config import (
    DB_DSN, TOPIC_SENSOR_VALIDATED, TOPIC_ALERT_LOCAL,
    TOPIC_ALERT_NEIGHBOR, TOPIC_ALERT_HEAD, TOPIC_LOG_EVENTS,
)

def main():
    conn = psycopg2.connect(DB_DSN)
    conn.autocommit = True
    cur = conn.cursor()

    consumer = make_consumer(
        "db_writer_group",
        [TOPIC_SENSOR_VALIDATED, TOPIC_ALERT_LOCAL, TOPIC_ALERT_NEIGHBOR, TOPIC_ALERT_HEAD, TOPIC_LOG_EVENTS],
    )
    print("DB writer running...")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None or msg.error():
                continue

            topic = msg.topic()
            data = json.loads(msg.value())

            if topic == TOPIC_SENSOR_VALIDATED:
                cur.execute(
                    "INSERT INTO sensor_readings (sensor_id, area_id, sensor_type, value, timestamp, is_anomaly) VALUES (%s,%s,%s,%s,%s,%s)",
                    (data["sensor_id"], data["area_id"], data["sensor_type"], data.get("value"), data["timestamp"], data.get("is_anomaly", False)),
                )
            elif topic.startswith("alert."):
                cur.execute(
                    "INSERT INTO alerts (area_id, alert_type, severity, message, timestamp, escalation_level) VALUES (%s,%s,%s,%s,%s,%s)",
                    (data["area_id"], data["alert_type"], data["severity"], data["message"], data["timestamp"], data.get("escalation_level", "local")),
                )
            elif topic == TOPIC_LOG_EVENTS:
                cur.execute(
                    "INSERT INTO logs (level, source, message, metadata, timestamp) VALUES (%s,%s,%s,%s,%s)",
                    (data["level"], data["source"], data["message"], Json(data.get("metadata", {})), data["timestamp"]),
                )
    except KeyboardInterrupt:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()