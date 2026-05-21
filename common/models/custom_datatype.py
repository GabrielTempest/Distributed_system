from pydantic.dataclasses import dataclass
from pydantic import BaseModel

@dataclass
class Measurement(BaseModel):
    measurement_type: str
    value: float
    unit: str

@dataclass
class Location(BaseModel):
    latitude: float
    longitude: float

@dataclass
class SensorMetadata(BaseModel):
    battery: int
    signal_strength: int

@dataclass
class ProcessorInfo(BaseModel):
    model_version: str