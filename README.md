# AIOT lec13 — Taiwan Temperature Forecast Dashboard

A Python project that fetches agricultural weather forecast data from Taiwan's Central Weather Administration (CWA) open data API, stores it in SQLite, and displays it via an interactive web dashboard.

## Features

- **Data Ingestion**: Fetch daily max/min temperature forecasts from CWA API for all Taiwan locations
- **SQLite Storage**: Persistent local database for historical and cached data
- **Interactive Dashboard**: Web UI (Flask + HTML/JS/Tailwind + Leaflet) with:
  - Dynamic Taiwan map showing current temperatures per location
  - Click-to-select cities and view time-series charts (Chart.js)
  - Responsive design with Tailwind CSS

## Project Structure

```
lec13/
├── sqlite.py                  # Data ingestion: fetch from CWA API → sqlitedata.db
├── api_server.py             # Flask backend: serves static frontend + JSON endpoints
├── static/
│   └── index.html            # Frontend: Leaflet map + Chart.js + Tailwind
├── sqlitedata.db             # SQLite database (created at runtime)
├── requirements.txt          # Python dependencies
├── openspec/
│   ├── project.md            # Project context & tech stack
│   ├── AGENTS.md             # OpenSpec workflow for AI assistants
│   ├── scripts/
│   │   └── next_proposal_id.py  # Helper: compute next proposal ID
│   └── proposals/            # Change proposals (01-XXXX format)
└── README.md                 # This file
```

## Tech Stack

- **Python 3.8+** (tested on 3.10/3.11)
- **Data**: requests, urllib3, sqlite3 (stdlib)
- **Backend**: Flask
- **Frontend**: HTML5, JavaScript (Vanilla), Tailwind CSS (CDN), Leaflet (map), Chart.js (charts)
- **Testing**: pytest (optional)

## Installation

1. Clone or navigate to the repo:
   ```powershell
   cd C:\Users\YULUN\Desktop\AIOT\lec13
   ```

2. Create and activate a virtual environment:
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Upgrade pip and install dependencies:
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

## Usage

### Step 1: Fetch and store data

```powershell
python sqlite.py
```

This fetches the latest weather forecast from the CWA API and populates `sqlitedata.db` with temperature records for all locations.

### Step 2: Run the web dashboard

```powershell
python api_server.py
```

Open your browser to `http://127.0.0.1:5000`. You should see:
- A map of Taiwan with temperature markers at each location
- A sidebar showing the selected city's time-series chart
- Interactive Leaflet map (zoom, pan, click markers)

## API Endpoints

- `GET /` — Serves the static dashboard (index.html)
- `GET /api/locations` — JSON list of latest temperatures per location (with lat/lon)
- `GET /api/area?area=<location_name>` — JSON time-series records for a specific location

## Data Schema

### Table: `temperature_daily`

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Auto-increment |
| area | TEXT | Location name (from CWA) |
| date | TEXT | ISO date string (YYYY-MM-DD) |
| maxT | TEXT | Max temperature (°C) |
| minT | TEXT | Min temperature (°C) |

## Configuration

- **API Key**: Stored in `sqlite.py` as `CWA_PARAMS["Authorization"]`. Replace with your own CWA API key if needed.
- **Database**: `sqlitedata.db` in repo root (created on first run).
- **Port**: Flask runs on `http://127.0.0.1:5000` by default (edit in `api_server.py` to change).

## Development & Contributing

- **Proposals**: Create or review change proposals in `openspec/proposals/` using the `01-XXXX` ID format.
- **ID Generation**: Use `python openspec/scripts/next_proposal_id.py` to compute the next proposal ID.
- **Tests**: Add pytest tests in a `tests/` folder if desired.

See `openspec/AGENTS.md` for the full OpenSpec workflow.

## Known Limitations

- Coordinates for locations come from the CWA API; if missing, those locations won't appear on the map but remain queryable via API.
- Frontend uses Tailwind CDN (development setup); for production, build Tailwind CSS locally.
- Flask development server is not suitable for production; use a WSGI server (e.g., Gunicorn, uWSGI) for deployment.

## License

None specified. Adapt as needed for your institution.

## References

- [CWA Open Data API](https://opendata.cwa.gov.tw/)
- [CWA OBS Temp Dashboard](https://www.cwa.gov.tw/V8/C/W/OBS_Temp.html) — inspiration for UI layout
- [Leaflet.js](https://leafletjs.com/) — interactive maps
- [Chart.js](https://www.chartjs.org/) — time-series charts
- [Tailwind CSS](https://tailwindcss.com/) — utility-first styling