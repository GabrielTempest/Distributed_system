from dataclasses import dataclass

@dataclass
class DbWrite:
    write_id: str
    timestamp: str
    table: str          # e.g. "sensor_readings", "alerts", "logs"
    operation: str      # INSERT, UPDATE, DELETE
    payload: str        # JSON string of the row data