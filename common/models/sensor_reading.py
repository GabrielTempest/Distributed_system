from dataclasses import dataclass, field
from pydantic import BaseModel
from common.models import DisasterType, MeasurementType, AlertLevel, Measurement, Location, SensorMetadata

@dataclass
class SensorReading(BaseModel):
    sensor_id: str
    area_id: str
    timestamp: str
    disaster_type: DisasterType
    measurement_type: MeasurementType
    current_measurement: Measurement
    forecast_measurement: Measurement
    alert_level: AlertLevel
    location: Location
    metadata: SensorMetadata