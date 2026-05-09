from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Literal

class SensorReading(BaseModel):
    sensor_id: str
    area_id: str
    sensor_type: Literal["temperature", "seismic", "water_level"]
    value: Optional[float]
    timestamp: datetime

class Alert(BaseModel):
    area_id: str
    alert_type: str
    severity: Literal["low", "medium", "high", "critical"]
    message: str
    timestamp: datetime
    escalation_level: Literal["local", "neighbor", "head"] = "local"

class LogEntry(BaseModel):
    level: Literal["INFO", "WARN", "ERROR"]
    source: str
    message: str
    metadata: dict = {}
    timestamp: datetime