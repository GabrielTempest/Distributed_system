import json
from collections import defaultdict, deque
from datetime import datetime, timezone, timedelta
from common.kafka_client import make_producer, make_consumer, send
from common.config import TOPIC_ALERT_LOCAL, TOPIC_ALERT_NEIGHBOR, TOPIC_ALERT_HEAD, TOPIC_LOG_EVENTS, NEIGHBORS

recent_alerts = defaultdict(lambda: deque(maxlen=10))

def log(producer, level, message, metadata=None):
    entry = {
        "level": level, "source": "alert_service", "message": message,
        "metadata": metadata or {}, "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    send(producer, TOPIC_LOG_EVENTS, key="alert_service", value=entry)

def main():
    consumer = make_consumer("alert_service_group", [TOPIC_ALERT_LOCAL])
    producer = make_producer()
    print("Alert service running...")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None or msg.error():
                continue
            alert = json.loads(msg.value())
            area = alert["area_id"]
            sev = alert["severity"]

            now = datetime.now(timezone.utc)
            recent_alerts[area].append(now)
            recent_count = sum(1 for t in recent_alerts[area] if now - t < timedelta(minutes=1))

            print(f"[LOCAL ALERT] {area} | {sev} | {alert['message']}")
            log(producer, "INFO", f"Notified citizens of {area}", {"alert": alert})

            if sev in ("high", "critical") or recent_count >= 3:
                for neighbor in NEIGHBORS.get(area, []):
                    n_alert = {**alert, "escalation_level": "neighbor", "area_id": neighbor,
                               "message": f"[Neighbor warning from {area}] {alert['message']}"}
                    send(producer, TOPIC_ALERT_NEIGHBOR, key=neighbor, value=n_alert)
                    print(f"  → Escalated to neighbor {neighbor}")

            if sev == "critical":
                h_alert = {**alert, "escalation_level": "head"}
                send(producer, TOPIC_ALERT_HEAD, key="head", value=h_alert)
                print(f"  → Escalated to HEAD/EOC")
                log(producer, "ERROR", f"Critical alert escalated to head from {area}", {"alert": h_alert})

            producer.poll(0)
    except KeyboardInterrupt:
        consumer.close()
        producer.flush()

if __name__ == "__main__":
    main()