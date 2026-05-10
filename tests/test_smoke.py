import os
import time
import uuid
from datetime import datetime, timezone

import pytest

from common.config import AREAS, DB_DSN, TOPIC_SENSOR_RAW
from common.schemas import SensorReading


def test_config_exports_expected_values():
	assert AREAS == ["area_1", "area_2", "area_3"]
	assert TOPIC_SENSOR_RAW == "sensor.raw"


def test_sensor_reading_model_accepts_valid_payload():
	reading = SensorReading(
		sensor_id="area_1_temperature_01",
		area_id="area_1",
		sensor_type="temperature",
		value=25.0,
		timestamp=datetime.now(timezone.utc),
	)

	assert reading.area_id == "area_1"
	assert reading.sensor_type == "temperature"


@pytest.mark.skipif(os.getenv("RUN_LIVE_SMOKE_TEST") != "1", reason="Live cluster smoke test is opt-in")
def test_live_cluster_smoke_end_to_end():
	psycopg2 = pytest.importorskip("psycopg2")
	kafka_client = pytest.importorskip("common.kafka_client")
	make_producer = kafka_client.make_producer
	send = kafka_client.send

	producer = make_producer()
	metadata = producer.list_topics(timeout=10)
	assert metadata.brokers, "Kafka broker metadata was not returned"

	conn = psycopg2.connect(DB_DSN)
	conn.autocommit = True
	cur = conn.cursor()

	try:
		cur.execute(
			"""
			SELECT tablename
			FROM pg_tables
			WHERE schemaname = 'public'
			  AND tablename IN ('sensor_readings', 'alerts', 'logs')
			"""
		)
		tables = {row[0] for row in cur.fetchall()}
		assert tables == {"sensor_readings", "alerts", "logs"}

		smoke_area = f"smoke_{uuid.uuid4().hex[:8]}"
		smoke_sensor = f"{smoke_area}_temperature_01"
		reading = {
			"sensor_id": smoke_sensor,
			"area_id": smoke_area,
			"sensor_type": "temperature",
			"value": 99.0,
			"timestamp": datetime.now(timezone.utc).isoformat(),
		}

		send(producer, TOPIC_SENSOR_RAW, key=smoke_area, value=reading)
		producer.flush(10)

		deadline = time.monotonic() + 45
		while time.monotonic() < deadline:
			cur.execute("SELECT 1 FROM sensor_readings WHERE sensor_id = %s LIMIT 1", (smoke_sensor,))
			sensor_written = cur.fetchone() is not None

			cur.execute(
				"""
				SELECT 1
				FROM alerts
				WHERE area_id = %s AND severity = 'critical' AND escalation_level = 'local'
				LIMIT 1
				""",
				(smoke_area,),
			)
			local_alert_written = cur.fetchone() is not None

			cur.execute(
				"""
				SELECT 1
				FROM alerts
				WHERE area_id = %s AND escalation_level = 'head'
				LIMIT 1
				""",
				(smoke_area,),
			)
			head_alert_written = cur.fetchone() is not None

			cur.execute(
				"""
				SELECT source
				FROM logs
				WHERE message LIKE %s OR message LIKE %s
				ORDER BY id DESC
				LIMIT 10
				""",
				(
					f"%Alert raised: critical in {smoke_area}%",
					f"%Critical alert escalated to head from {smoke_area}%",
				),
			)
			sources = {row[0] for row in cur.fetchall()}
			logs_written = {"anomaly_detector", "alert_service"}.issubset(sources)

			if sensor_written and local_alert_written and head_alert_written and logs_written:
				return

			time.sleep(1)

		pytest.fail("Timed out waiting for the live cluster pipeline to write sensor, alert, and log rows")
	finally:
		cur.close()
		conn.close()
