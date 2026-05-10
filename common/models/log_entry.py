from dataclasses import dataclass
from typing import Optional

@dataclass
class LogEntry:
    log_id: str
    timestamp: str
    source: str        # which service sent this e.g. "anomaly-detector", "alert-broadcaster"
    level: str         # INFO, WARNING, ERROR, CRITICAL
    event_type: str    # e.g. "ANOMALY_DETECTED", "ALERT_ISSUED", "SENSOR_TIMEOUT"
    message: str
    area_id: Optional[str] = None
    payload: Optional[str] = None   # JSON string of the original message if needed