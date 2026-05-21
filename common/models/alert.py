from dataclasses import dataclass, field
from typing import List
from pydantic import BaseModel
from common.models import Measurement, DisasterType, AlertLevel

@dataclass
class Alert(BaseModel):
    alert_id: str
    area_id: str
    timestamp: str
    disaster_type: DisasterType
    alert_level: AlertLevel
    title: str
    message: str
    recommended_actions: List[str]