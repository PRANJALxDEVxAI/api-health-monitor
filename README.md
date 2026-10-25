# API Health Monitor

A Python desktop application for monitoring API endpoints, measuring response times, and evaluating API health through a simple graphical dashboard.

## Features

- **API monitoring:** Send HTTP requests to configured endpoints.
- **Response-time measurement:** Measure request duration in milliseconds.
- **Health evaluation:** Classify endpoints as Healthy, Degraded, or Down.
- **Desktop dashboard:** View endpoint information through a CustomTkinter GUI.
- **Endpoint management:** Add and remove monitored endpoints.
- **Persistent configuration:** Save endpoint names and URLs locally in a JSON file.
- **Timeout and error handling:** Handle timeouts and request-related failures.
- **Background checks:** Perform monitoring requests without blocking the main GUI thread.

## Tech Stack

- Python
- Requests
- CustomTkinter
- JSON
- Threading

## Health Classification

The application uses the following rules:

| Condition | Health status |
|---|---|
| Endpoint is unreachable or request fails | Down |
| HTTP status code is 500 or higher | Down |
| HTTP status code is 400–499 | Degraded |
| Response time exceeds 2,000 ms | Degraded |
| HTTP status code is 200–399 and response time is within the threshold | Healthy |

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/api-health-monitor.git
cd api-health-monitor
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

If you use Command Prompt instead:

```bat
.venv\Scripts\activate.bat
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the application

```bash
python main.py
```

Add your API endpoints in the application and use the monitoring controls to check their status.

## Project Structure

```text
api-health-monitor/
├── main.py                 # Application entry point
├── frontend.py             # Desktop GUI and endpoint management
├── requirements.txt        # Python dependencies
├── test_monitor.py         # Manual monitoring test
└── src/
    ├── __init__.py
    ├── monitor.py          # HTTP requests and response-time measurement
    └── health_check.py     # Health classification rules
```

The application stores endpoint configuration locally in `apis.json`. This file is generated at runtime and is not required to be committed to the repository.

## Testing

A basic manual test is available in `test_monitor.py`.

Run it with:

```bash
python test_monitor.py
```

The test checks a sample HTTP endpoint and prints its monitoring result and calculated health status. It requires an internet connection.

## Current Scope

This is Version 1 of the project. It focuses on endpoint management, basic HTTP health checks, response-time measurement, a desktop dashboard, and local JSON persistence.

## Future Improvements

- Automatic periodic monitoring
- Historical response-time tracking
- Health-status history and charts
- Exportable monitoring reports
- Configurable timeout and health thresholds

## Author

**Pranjal Gupta**

Built as a Python project to practise API integration, exception handling, desktop GUI development, threading, and JSON persistence.
