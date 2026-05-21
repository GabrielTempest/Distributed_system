from enum import Enum
from pydantic.dataclasses import dataclass

@dataclass
class DisasterType(str, Enum):
    FLOOD = "FLOOD"
    TYPHOON = "TYPHOON"
    HEATWAVE = "HEATWAVE"

@dataclass
class AlertLevel(str, Enum):
    INFO = "INFO"
    MONITORING = "MONITORING"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"