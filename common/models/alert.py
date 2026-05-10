from dataclasses import dataclass, field
from typing import List

@dataclass
class Measurement:
    value: float
    unit: str

@dataclass
class Alert:
    alert_id: str
    area_id: str
    timestamp: str
    disaster_type: str
    forecast_measurement: Measurement
    confidence_score: float
    alert_level: str          # INFO, LOW, MEDIUM, HIGH, CRITICAL
    title: str
    message: str
    recommended_actions: List[str]