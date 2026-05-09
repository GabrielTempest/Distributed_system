import time
import random
import argparse
from datetime import datetime, timezone
from common.kafka_client import make_producer, send
from common.config import TOPIC_SENSOR_RAW, AREAS

def generate_reading(sensor_id: str, area_id: str, sensor_type: str, fault_mode: str = "none"):
    base = {"temperature": 25.0, "seismic": 1.0, "water_level": 1.0}[sensor_type]
    noise = random.gauss(0, 1)
    value = base + noise

    if fault_mode == "spike":
        if random.random() < 0.05:
            value = base * 5
    elif fault_mode == "nan":
        if random.random() < 0.1:
            value = None
    elif fault_mode == "dead":
        return None

    return {
        "sensor_id": sensor_id,
        "area_id": area_id,
        "sensor_type": sensor_type,
        "value": value,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rate", type=float, default=1.0, help="messages per second per sensor")
    parser.add_argument("--fault-mode", default="none", choices=["none", "spike", "nan", "dead"])
    parser.add_argument("--fault-area", default=None, help="apply fault only to this area")
    args = parser.parse_args()

    producer = make_producer()
    sensors = []
    for area in AREAS:
        for stype in ["temperature", "seismic", "water_level"]:
            sensors.append((f"{area}_{stype}_01", area, stype))

    print(f"Started {len(sensors)} sensors at {args.rate} msg/sec")
    interval = 1.0 / args.rate

    try:
        while True:
            for sid, area, stype in sensors:
                fm = args.fault_mode if (args.fault_area is None or args.fault_area == area) else "none"
                reading = generate_reading(sid, area, stype, fm)
                if reading is None:
                    continue
                send(producer, TOPIC_SENSOR_RAW, key=area, value=reading)
            producer.flush()
            time.sleep(interval)
    except KeyboardInterrupt:
        producer.flush()
        print("\nStopped.")

if __name__ == "__main__":
    main()