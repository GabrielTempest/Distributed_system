from dataclasses import dataclass, field
from enum import Enum
from typing import List
from pydantic import BaseModel
from common.models import DisasterType, Measurement, AlertLevel, ProcessorInfo


@dataclass
class AreaProcessingResult(BaseModel):
    area_id: str
    timestamp: str
    disaster_type: DisasterType
    current_average_measurement: Measurement
    forecast_average_measurement: Measurement
    alert_level: AlertLevel
    anomaly_sensors: List[str]
    processor_info: ProcessorInfo