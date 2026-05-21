import random
from datetime import datetime
from common.models import SensorReading, AlertLevel, Measurement, Location, SensorMetadata
from common.producer.sensors import SENSORS

def generate_weather_event(sensor_id: str = None, 
                           current_measurement: float = None, 
                           forecast_measurement: float = None,
                           measurement_unit: str = None,
                           ) -> SensorReading:
    if sensor_id is None:
        sensor_id = random.choice(list(SENSORS.keys()))
    else:
        if sensor_id not in SENSORS:
            raise ValueError(f"Sensor with ID '{sensor_id}' is not registered.")
    sensor = SENSORS[sensor_id]
    # Rainfall & Alert level
    rainfall = random.uniform(0, 300)
    if rainfall >= 150:
        level = AlertLevel.CRITICAL
    elif rainfall >= 100:
        level = AlertLevel.WARNING
    elif rainfall >= 50:
        level = AlertLevel.MONITORING
    else:
        level = AlertLevel.INFO
    # Battery drains slowly
    sensor["battery"] = max(sensor["battery"] - random.uniform(0, 0.2), 0)
    # signal changes
    signal = random.randint(0, 100)

    return SensorReading(
        sensor_id=sensor_id,
        area_id=sensor["area"],
        timestamp=datetime.now(tz=sensor["timezone"]),

        disaster_type=sensor["disaster_type"],
        measurement_type=sensor["measurement_type"],

        current_measurement=Measurement(
            value=rainfall,
            unit=sensor["measurement_unit"]
        ),

        forecast_measurement=Measurement(
            value=rainfall + random.uniform(20, 60),
            unit=sensor["measurement_unit"]
        ),

        alert_level=level,

        location=Location(
            latitude=sensor["lat"],
            longitude=sensor["lon"]
        ),

        metadata=SensorMetadata(
            battery=round(sensor["battery"], 1),
            signal_strength=signal
        )
    )