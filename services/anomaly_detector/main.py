import json
import statistics
from collections import defaultdict, deque
from datetime import datetime, timezone
from common.kafka_client import make_producer, make_consumer, send
from common.config import (
    TOPIC_SENSOR_RAW, TOPIC_SENSOR_VALIDATED, TOPIC_ALERT_LOCAL, TOPIC_LOG_EVENTS,
    ROLLING_WINDOW, ANOMALY_STDDEV_MULT,
    TEMP_CRITICAL, SEISMIC_CRITICAL, WATER_CRITICAL,
)

windows = defaultdict(lambda: deque(maxlen=ROLLING_WINDOW))

CRITICAL_THRESHOLDS = {
    "temperature": TEMP_CRITICAL,
    "seismic": SEISMIC_CRITICAL,
    "water_level": WATER_CRITICAL,
}

def log(producer, level, message, metadata=None):
    entry = {
        "level": level,
        "source": "anomaly_detector",
        "message": message,
        "metadata": metadata or {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    send(producer, TOPIC_LOG_EVENTS, key="anomaly_detector", value=entry)

def is_anomaly(sensor_id: str, value: float) -> bool:
    w = windows[sensor_id]
    if len(w) < 5:
        w.append(value)
        return False
    mean = statistics.mean(w)
    try:
        std = statistics.stdev(w)
    except statistics.StatisticsError:
        std = 0
    w.append(value)
    if std == 0:
        return False
    return abs(value - mean) > ANOMALY_STDDEV_MULT * std

def severity_of(sensor_type: str, value: float) -> str | None:
    threshold = CRITICAL_THRESHOLDS.get(sensor_type)
    if threshold is None:
        return None
    if value >= threshold * 1.5:
        return "critical"
    if value >= threshold:
        return "high"
    if value >= threshold * 0.8:
        return "medium"
    return None

def main():
    consumer = make_consumer("anomaly_detector_group", [TOPIC_SENSOR_RAW])
    producer = make_producer()
    print("Anomaly detector running...")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None or msg.error():
                continue

            reading = json.loads(msg.value())
            value = reading.get("value")
            sid = reading["sensor_id"]
            stype = reading["sensor_type"]

            if value is None:
                log(producer, "WARN", f"Null value from {sid}", {"sensor_id": sid})
                continue

            anomaly = is_anomaly(sid, value)
            if anomaly:
                log(producer, "WARN", f"Anomaly: {sid} value={value:.2f}", {"reading": reading})

            send(producer, TOPIC_SENSOR_VALIDATED, key=reading["area_id"], value={**reading, "is_anomaly": anomaly})

            sev = severity_of(stype, value)
            if sev:
                alert = {
                    "area_id": reading["area_id"],
                    "alert_type": stype,
                    "severity": sev,
                    "message": f"{stype} reading {value:.2f} exceeded threshold",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "escalation_level": "local",
                }
                send(producer, TOPIC_ALERT_LOCAL, key=reading["area_id"], value=alert)
                log(producer, "ERROR", f"Alert raised: {sev} in {reading['area_id']}", {"alert": alert})

            producer.poll(0)
    except KeyboardInterrupt:
        consumer.close()
        producer.flush()

if __name__ == "__main__":
    main()