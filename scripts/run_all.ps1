$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

function Assert-LastExit {
    param(
        [string]$Action
    )

    if ($LASTEXITCODE -ne 0) {
        throw "$Action failed with exit code $LASTEXITCODE."
    }
}

function Get-PythonVersion {
    param(
        [string]$PythonExe
    )

    $versionText = & $PythonExe -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
    Assert-LastExit "Reading Python version from $PythonExe"
    return [version]$versionText.Trim()
}

function Resolve-BasePython {
    $preferredVersions = @("3.12", "3.11", "3.10", "3.9", "3.8")

    $pyCmd = Get-Command py -ErrorAction SilentlyContinue
    if ($null -ne $pyCmd) {
        foreach ($v in $preferredVersions) {
            $candidate = & py -$v -c "import sys; print(sys.executable)" 2>$null
            if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($candidate)) {
                return $candidate.Trim()
            }
        }
    }

    $fallback = (Get-Command python -ErrorAction SilentlyContinue)
    if ($null -eq $fallback) {
        throw "No Python interpreter found. Install Python 3.8-3.12 and try again."
    }

    return $fallback.Source
}

$basePython = Resolve-BasePython
$baseVersion = Get-PythonVersion -PythonExe $basePython

if ($baseVersion -ge [version]"3.13") {
    throw "Detected Python $baseVersion at '$basePython'. This project pins packages that fail on Python 3.13+. Install/use Python 3.12 and retry."
}

$venvPython = Join-Path $repoRoot ".venv-1\Scripts\python.exe"
$venvNeedsRecreate = $false

if (Test-Path $venvPython) {
    $venvVersion = Get-PythonVersion -PythonExe $venvPython
    if ($venvVersion -ge [version]"3.13") {
        Write-Host "Existing .venv-1 uses Python $venvVersion and is incompatible with pinned dependencies. Recreating venv ..."
        $venvNeedsRecreate = $true
    }
}
else {
    $venvNeedsRecreate = $true
}

if ($venvNeedsRecreate) {
    if (Test-Path ".venv-1") {
        Remove-Item ".venv-1" -Recurse -Force
    }
    Write-Host "Creating virtual environment with Python $baseVersion at .venv-1 ..."
    & $basePython -m venv .venv-1
    Assert-LastExit "Creating virtual environment"
}

Write-Host "Installing/updating Python dependencies ..."
& $venvPython -m pip install --upgrade pip
Assert-LastExit "Upgrading pip"

& $venvPython -m pip install -r requirements.txt
Assert-LastExit "Installing dependencies"

Write-Host "Starting Docker services ..."
docker compose up -d
Assert-LastExit "Starting Docker services"

docker compose ps
Assert-LastExit "Checking Docker services"

function Start-ServiceWindow {
    param(
        [string]$Title,
        [string]$Command
    )

    $psCommand = "Set-Location '$repoRoot'; & '$venvPython' -m $Command"
    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-ExecutionPolicy", "Bypass",
        "-Command", "`$Host.UI.RawUI.WindowTitle = '$Title'; $psCommand"
    ) | Out-Null
}

Write-Host "Launching service windows ..."
Start-ServiceWindow -Title "DB Writer" -Command "services.database_writer.main"
Start-ServiceWindow -Title "Anomaly Detector" -Command "services.anomaly_detector.main"
Start-ServiceWindow -Title "Alert Service" -Command "services.alert_service.main"
Start-ServiceWindow -Title "Sensor Simulator" -Command "services.sensor_simulator.main --rate 1"

Write-Host "All services launched."
Write-Host "To stop infra later: docker compose down"
