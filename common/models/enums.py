from enum import Enum
from pydantic.dataclasses import dataclass

@dataclass
class DisasterType(str, Enum):
    FLOOD = "FLOOD"
    TYPHOON = "TYPHOON"
    LANDSLIDE = "LANDSLIDE"
    WILDFIRE = "WILDFIRE"
    HEATWAVE = "HEATWAVE"

@dataclass
class AlertLevel(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

@dataclass
class MeasurementType(str, Enum):
    WATER_LEVEL = "WATER_LEVEL"
    RAINFALL = "RAINFALL"
    WIND_SPEED = "WIND_SPEED"
    GROUND_VIBRATION = "GROUND_VIBRATION"