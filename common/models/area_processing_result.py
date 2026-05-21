from dataclasses import dataclass
from typing import List
from pydantic import BaseModel
from common.models import DisasterType, Measurement, AlertLevel, ProcessorInfo


@dataclass
class AreaProcessingResult(BaseModel):
    area_id: str
    timestamp: str
    disaster_type: DisasterType
    current_average_measurement: List[Measurement]
    alert_level: AlertLevel
    processor_info: ProcessorInfo