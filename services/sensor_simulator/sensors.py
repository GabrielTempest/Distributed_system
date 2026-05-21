import random
import uuid

from datetime import timezone, timedelta

from common.models import DisasterType
from common.config import AREA

# Global sensor registry
SENSORS = {}



def create_sensor(
    area: str,
    disaster_type: DisasterType,
    latitude: float = None,
    longitude: float = None,
    battery: int = None
):
    """
    Create and register a sensor with unique id globally (and core metadata: area, location and timezone, battery).
    """
    sensor_id = f"WS-{uuid.uuid4().hex[:8]}"
    if area.casefold() not in (a.casefold() for a in AREA.keys()):
        raise ValueError(f"Area '{area}' is not registered in config.areas.AREA")
    if latitude is None or longitude is None:
        lat, lon, _ = AREA[area]
        latitude = latitude if latitude is not None else lat + random.uniform(-0.05, 0.05)
        longitude = longitude if longitude is not None else lon + random.uniform(-0.05, 0.05)

    SENSORS[sensor_id] = {
        "area": area,
        "disaster_type": disaster_type,
        "lat": latitude,
        "lon": longitude,
        "timezone": timezone(timedelta(hours=AREA[area][2])),
        "battery": battery if battery is not None else random.randint(70, 100)
    }
    return sensor_id