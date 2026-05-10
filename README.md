# Distributed System - Local Run Guide

This project simulates a distributed early-warning pipeline:

- Sensor simulator publishes raw readings to Redpanda (Kafka-compatible broker).
- Anomaly detector validates readings and raises alerts.
- Alert service escalates alerts to neighbor/head levels.
- Database writer persists sensor, alert, and log events to PostgreSQL.

## Prerequisites

- Docker Desktop is installed and running.
- Windows PowerShell.
- Repository opened at the project root.
- Python environment available at `.venv-1`.

## 1. Start Infrastructure (Redpanda + Postgres)

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
Set-Location E:\VGU_Summer_26-26\Distributed_System\Distributed_system

docker compose up -d
docker compose ps
```

Expected: `redpanda`, `redpanda-console`, and `postgres` are running.

Optional health check:

```powershell
docker compose exec redpanda rpk cluster health
```

Look for `Healthy: true`.

## 2. Activate Python Environment

```powershell
.\.venv-1\Scripts\Activate.ps1
python --version
python -m pip show pytest
```

If activation is blocked, run this once in the terminal first:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

## 3. Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

## 4. Start Application Services (One Terminal per Service)

Terminal A:

```powershell
.\.venv-1\Scripts\Activate.ps1
python -m services.sensor_simulator.main --rate 1
```

Terminal B:

```powershell
.\.venv-1\Scripts\Activate.ps1
python -m services.anomaly_detector.main
```

Terminal C:

```powershell
.\.venv-1\Scripts\Activate.ps1
python -m services.alert_service.main
```

Terminal D:

```powershell
.\.venv-1\Scripts\Activate.ps1
python -m services.database_writer.main
```

## 5. Run Smoke Test (End-to-End)

The smoke test in `tests/test_smoke.py` includes an opt-in live cluster check.

```powershell
$env:RUN_LIVE_SMOKE_TEST = "1"
python -m pytest tests/test_smoke.py -q
```

Expected: test passes after the pipeline writes sensor, alert, and log records.

## 6. Manual Verification (Optional)

Check tables:

```powershell
docker compose exec postgres psql -U dew -d disaster_warning -c "\dt"
```

Check row counts:

```powershell
docker compose exec postgres psql -U dew -d disaster_warning -c "SELECT count(*) FROM sensor_readings;"
docker compose exec postgres psql -U dew -d disaster_warning -c "SELECT count(*) FROM alerts;"
docker compose exec postgres psql -U dew -d disaster_warning -c "SELECT count(*) FROM logs;"
```

Check broker topics:

```powershell
docker compose exec redpanda rpk topic list
```

## Troubleshooting

- `Import "pytest" could not be resolved` in VS Code:
	- Ensure interpreter is set to `.venv-1\Scripts\python.exe`.
	- Install dependencies with `python -m pip install -r requirements.txt`.
- Redpanda not healthy yet:
	- Wait 1 to 2 minutes and run `docker compose exec redpanda rpk cluster health` again.
- Database connection issues:
	- Confirm Postgres is running on host port `5433` and `docker compose ps` shows it up.

## Stop Everything

Stop service terminals with `Ctrl+C`, then bring down containers:

```powershell
docker compose down
```