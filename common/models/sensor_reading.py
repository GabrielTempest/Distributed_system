from dataclasses import dataclass, field
from typing import List
from pydantic import BaseModel
from common.models import DisasterType, MeasurementType, AlertLevel, Measurement, Location, SensorMetadata

@dataclass
class SensorReading(BaseModel):
    sensor_id: str
    area_id: str
    timestamp: str
    disaster_type: DisasterType
    current_measurement: List[Measurement]
    alert_level: AlertLevel
    location: Location
    metadata: SensorMetadata