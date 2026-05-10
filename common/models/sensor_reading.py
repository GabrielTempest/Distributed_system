from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Measurement:
    value: float
    unit: str
    confidence: Optional[float] = None

@dataclass
class Location:
    latitude: float
    longitude: float

@dataclass
class SensorMetadata:
    battery: int
    signal_strength: int

@dataclass
class SensorReading:
    sensor_id: str
    area_id: str
    timestamp: str
    disaster_type: str
    current_measurement: Measurement
    forecast_measurement: Measurement
    alert_level: str          # INFO, LOW, MEDIUM, HIGH, CRITICAL
    location: Location
    metadata: SensorMetadata