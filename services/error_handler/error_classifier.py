from datetime import datetime, timezone, timedelta

class SensorErrorClassifier:

    def classify(self, reading: dict) -> str | None:
        if self._is_network(reading):
            return "network"
        if self._is_offline(reading):
            return "offline"
        if self._is_bad_data(reading):
            return "bad_data"
        return None

    def _is_bad_data(self, r: dict) -> bool:
        if r.get("value") is None:
            return True
        if not (0 <= r["value"] <= 100):
            return True
        return False

    def _is_offline(self, r: dict) -> bool:
        last_seen = r.get("timestamp")
        if not last_seen:
            return True
        age = datetime.now(timezone.utc) - datetime.fromisoformat(last_seen)
        return age > timedelta(minutes=5)

    def _is_network(self, r: dict) -> bool:
        required_fields = {"area_id", "value", "timestamp", "sensor_id"}
        return not required_fields.issubset(r.keys())