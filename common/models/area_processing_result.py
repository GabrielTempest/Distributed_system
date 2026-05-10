from dataclasses import dataclass, field
from typing import List

@dataclass
class Measurement:
    value: float
    unit: str
    confidence: float = 0.0

@dataclass
class ProcessorInfo:
    model_version: str

@dataclass
class AreaProcessingResult:
    area_id: str
    timestamp: str
    disaster_type: str
    current_average_measurement: Measurement
    forecast_average_measurement: Measurement
    alert_level: str          # INFO, LOW, MEDIUM, HIGH, CRITICAL
    anomaly_sensors: List[str]
    processor_info: ProcessorInfo