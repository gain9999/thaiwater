---
name: ews
description: Fetch early warning data (flash flood, landslide, water level, rainfall, soil moisture) from ews.dwr.go.th — Department of Water Resources Early Warning System
---

Fetch and display early warning station data from the EWS DWR API.
Base URL: `https://ews.dwr.go.th/ews/`

The user asked: $ARGUMENTS

## How to respond

1. Parse the user's request to identify which data they want (see below).
2. Use Bash to call the appropriate endpoint.
3. Present data in a clean table. Translate Thai station names where possible. Highlight alert status prominently (color-coded).
4. If no data type is specified, fetch all stations and show a summary by status.

## Station list (all live readings)

```bash
curl -sL "https://ews.dwr.go.th/ews/web-service/stn" \
  -X POST -H "User-Agent: Mozilla/5.0" \
  -F "action=LoadStation"
```

**No authentication required.** Returns an array of all monitoring stations.

### Station fields

| Field | Description |
|---|---|
| `stn` | Station code (e.g. `STN0001`) — used for graph queries |
| `name` | Station name (Thai) |
| `stn_type` | `RF` = rainfall station, `WL` = water level station |
| `tambon` / `amphoe` / `province` | Sub-district / District / Province |
| `main_basin` / `sub_basin` | Main and sub watershed |
| `latitude` / `longitude` | Coordinates |
| `status` | **0** = normal (gray), **1** = watch (green), **2** = prepare (orange), **3** = critical (red) |
| `warn` | Warning details (null if none) |
| `rain` | Current rainfall (mm) |
| `rain12h` | Rainfall last 12 hours (mm) |
| `rain07h` | Rainfall since 07:00 today (mm) |
| `temp` | Temperature (°C) |
| `wl` | Current water level (m) — `N/A` if not applicable |
| `wl07h` | Water level at 07:00 today (m) |
| `soil` | Soil moisture (%) |
| `date` | Last update datetime |
| `warning_type` | `wl` = water level warning, `RF` = rainfall warning |
| `sub_station` | Array of nearby sub-stations (name, location) |

### Status levels
- **0** — Normal / No data
- **1** — Watch (เฝ้าระวัง) — elevated risk
- **2** — Prepare (เตรียมพร้อม) — high risk
- **3** — Critical (วิกฤติ) — emergency / evacuation

## Graph endpoints (time-series data)

All graph endpoints return an array of `[timestamp_ms, value]` pairs for the last 24 hours.

```bash
# Rainfall (accumulated, 15-min intervals)
curl -sL "https://ews.dwr.go.th/ews/graph/rain_graph.php?FilterSTN=STN0001" -H "User-Agent: Mozilla/5.0"

# Rainfall bar chart (15-min increments)
curl -sL "https://ews.dwr.go.th/ews/graph/rain_15minbar.php?FilterSTN=STN0001" -H "User-Agent: Mozilla/5.0"

# Water level (m)
curl -sL "https://ews.dwr.go.th/ews/graph/wl_graph.php?FilterSTN=STN0001" -H "User-Agent: Mozilla/5.0"

# Soil moisture (%)
curl -sL "https://ews.dwr.go.th/ews/graph/soil_graph.php?FilterSTN=STN0001" -H "User-Agent: Mozilla/5.0"

# Temperature (°C)
curl -sL "https://ews.dwr.go.th/ews/graph/temp_graph.php?FilterSTN=STN0001" -H "User-Agent: Mozilla/5.0"
```

Replace `STN0001` with any station code from the station list.

Graph values of `-9.99` indicate sensor error / no data.

## Warning report page

Open in browser for a human-readable warning report for a station:
```
https://ews.dwr.go.th/ews/warning_report.php?stn=STN0001&type=wl
```
Parameters: `stn` = station code, `type` = `wl` or `RF`

## Useful filtering patterns

```python
import json, subprocess

# Load all stations
result = subprocess.run(
    ["curl", "-sL", "https://ews.dwr.go.th/ews/web-service/stn",
     "-X", "POST", "-H", "User-Agent: Mozilla/5.0",
     "-F", "action=LoadStation"],
    capture_output=True, text=True
)
stations = json.loads(result.stdout)

# Filter by status
critical = [s for s in stations if int(s.get('status', 0)) == 3]
warning  = [s for s in stations if int(s.get('status', 0)) >= 1]

# Filter by province
bkk = [s for s in stations if 'กรุงเทพ' in s.get('province', '')]

# Filter by type
rainfall_stns = [s for s in stations if s.get('stn_type') == 'RF']
waterlevel_stns = [s for s in stations if s.get('stn_type') == 'WL']

# Filter by basin
ping_basin = [s for s in stations if 'ปิง' in s.get('main_basin', '')]
```

## Typical use cases

- **Show all critical stations right now:** fetch station list, filter `status == 3`, show name, province, basin, rainfall, water level
- **Show stations with warnings:** filter `status >= 1`, sort by status descending
- **Show rainfall trend for a station:** call `rain_graph.php`, convert timestamps, display as table
- **Find stations in a province:** filter by `province` field
- **Check soil moisture risk:** sort by `soil` descending — high soil moisture + heavy rain = flash flood risk

## About EWS DWR

ระบบเตือนภัยล่วงหน้า น้ำท่วมฉับพลัน-น้ำป่าไหลหลาก (Early Warning System for Flash Floods and Landslides) operated by the Department of Water Resources (กรมทรัพยากรน้ำ, DWR). Monitors ~800+ stations across Thailand's mountain watersheds with 15-minute data updates.
