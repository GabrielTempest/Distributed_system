from enum import Enum
from typing import Optional
from pydantic.dataclasses import dataclass
from pydantic import BaseModel

@dataclass
class Measurement(BaseModel):
    value: float
    unit: str
    confidence: Optional[float] = None

@dataclass
class Location(BaseModel):
    latitude: float
    longitude: float

@dataclass
class SensorMetadata(BaseModel):
    battery: int
    signal_strength: int
    firmware_version: str

@dataclass
class ProcessorInfo(BaseModel):
    model_version: str