---
name: wmsc_rid
description: Fetch reservoir, telemetry station, and flood data from wmsc.rid.go.th — Royal Irrigation Department Smart Water Operations Center (ศูนย์ปฏิบัติการน้ำอัจฉริยะ กรมชลประทาน)
---

Fetch and display RID water data from the Royal Irrigation Department systems.
The user asked: $ARGUMENTS

## How to respond

1. Identify which system and data type the user wants.
2. Use Bash to call the appropriate endpoint and present results in a clean table.
3. For auth-required endpoints, explain what is needed and what public alternatives exist.

---

## System overview

RID Smart Water Operations Center operates several subsystems:

| System | URL | Auth | Description |
|---|---|---|---|
| WMSC Portal | `https://wmsc.rid.go.th/` | No | Main portal with links to all subsystems |
| Telerid API | `https://telerid.rid.go.th/restapi/` | Partial | Live telemetry station data (921 stations) |
| Reservoir App | `https://app.rid.go.th/reservoir/` | No | Reservoir storage summary by region |
| Flood Reports | `https://water.rid.go.th/flood/` | No | Daily/weekly flood situation PDFs and HTML reports |

---

## 1. Telerid Telemetry API — telerid.rid.go.th

**Base URL:** `https://telerid.rid.go.th/restapi/`

### Station list (public, no auth)

```bash
# All 921 telemetry stations (paginated, DRF format)
curl -sL "https://telerid.rid.go.th/restapi/main/station_list/" \
  -H "User-Agent: Mozilla/5.0" -H "Accept: application/json"
```

Response fields:

| Field | Description |
|---|---|
| `id` | Station ID (use for detail queries) |
| `code` | Station code (e.g. `TC.54`, `TG01`) |
| `name` | Station name (Thai) |
| `basin_name` | Main basin (ลุ่มน้ำ) |
| `sub_basin_name` | Sub-basin |
| `province_name` | Province |
| `amphur_name` | District (อำเภอ) |
| `tambon_name` | Sub-district (ตำบล) |
| `project_name` | Irrigation project name |
| `geom` | GeoJSON Point with `coordinates: [lon, lat]` |

Pagination: `count` (total), `next` (URL), `previous` (URL), `results` (array). Default page size is all 921 records (no pagination needed unless specifying `limit`).

### Station tree by basin (public, no auth)

```bash
# All stations organized by basin name, with measurement capability flags
curl -sL "https://telerid.rid.go.th/restapi/main/get_basin_tree/" \
  -H "User-Agent: Mozilla/5.0" -H "Accept: application/json"
```

Returns array of basin objects:
```json
[
  {
    "name": "ลุ่มน้ำเจ้าพระยา",
    "station": [
      {"id": 1, "name": "TC.54", "code": "TC.54", "measure_wl": true, "measure_r": true},
      ...
    ]
  },
  ...
]
```

Fields per station: `id`, `name`, `code`, `measure_wl` (has water level sensor), `measure_r` (has rainfall sensor)

### Filter patterns

```python
import json, subprocess

result = subprocess.run(
    ["curl", "-sL", "https://telerid.rid.go.th/restapi/main/station_list/",
     "-H", "User-Agent: Mozilla/5.0", "-H", "Accept: application/json"],
    capture_output=True, text=True
)
data = json.loads(result.stdout)
stations = data["results"]

# Filter by basin
chao_phraya = [s for s in stations if "เจ้าพระยา" in s.get("basin_name", "")]

# Filter by province
chiang_mai = [s for s in stations if "เชียงใหม่" in s.get("province_name", "")]

# Find stations with water level sensors
wl_stations = [s for s in stations if s.get("measure_wl")]  # only available in basin tree
```

### Auth-required endpoints

These return `{"detail": "Authentication credentials were not provided."}` without a token:

| Endpoint | Description |
|---|---|
| `GET main/station/{id}/` | Live readings for a specific station |
| `GET main/summary_value/` | Summary statistics across all stations |
| `GET main/get_alarm_list/` | Active alarms/alerts |
| `GET main/camera/` | CCTV camera list |
| `GET main/project/` | Irrigation projects |
| `GET forecast/` | Flood forecasts |
| `GET alert/` / `GET alerts/` | Alert records |

---

## 2. Reservoir Storage Summary — app.rid.go.th/reservoir

**Base URL:** `https://app.rid.go.th/reservoir/api/`

No authentication required.

### Regional storage summary (counts by bucket)

```bash
# All middle reservoirs grouped by region, storage-level bucket counts
curl -sL "https://app.rid.go.th/reservoir/api/summarypercent" \
  -H "User-Agent: Mozilla/5.0"

# Large dams only (same structure)
curl -sL "https://app.rid.go.th/reservoir/api/summarypercentdam" \
  -H "User-Agent: Mozilla/5.0"
```

Response fields (`summary_reservoir` array):

| Field | Description |
|---|---|
| `id` | Region ID |
| `treg` | Region name (Thai) |
| `amount_rsv` | Total number of reservoirs in region |
| `col0` | Count at 0% storage |
| `col1_30` | Count at 1–30% storage |
| `col31_50` | Count at 31–50% storage |
| `col51_80` | Count at 51–80% storage |
| `col81_100` | Count at 81–100% storage |
| `col100` | Count at exactly 100% (full) |

### All middle reservoirs — live readings (POST)

```bash
# All medium reservoirs with today's storage data, grouped by region
curl -sL "https://app.rid.go.th/reservoir/api/rsvmiddles" \
  -X POST -H "User-Agent: Mozilla/5.0" \
  -d "status=1"

# Filter by region code (N/NE/C/W/E/S)
curl -sL "https://app.rid.go.th/reservoir/api/rsvmiddles" \
  -X POST -H "User-Agent: Mozilla/5.0" \
  -d "status=1&region=N"

# Filter by storage percent range
curl -sL "https://app.rid.go.th/reservoir/api/rsvmiddles" \
  -X POST -H "User-Agent: Mozilla/5.0" \
  -d "status=1&percent_from=0&percent_to=30"
```

Response structure: `date`, `year_prev`, `region[]` → each region has `region_name_th`, `region_name_en`, `reservoir[]`

Reservoir fields:

| Field | Description | Unit |
|---|---|---|
| `cresv` | Reservoir code (e.g. `rsv403`) | — |
| `nresv` | Reservoir name (Thai) | — |
| `tprov` | Province | — |
| `treg` | Region (Thai) | — |
| `rid` | RID regional office | — |
| `project_name` | Irrigation project name | — |
| `cresv_lat` / `cresv_lng` | Coordinates | — |
| `cap_resv` | Full capacity | MCM |
| `low_qdisc` | Dead storage (unusable volume) | MCM |
| `qdisc_curr` | Current storage | MCM |
| `percent_resv_curr` | Current storage % of capacity | % |
| `qdisc_prev` | Storage same date last year | MCM |
| `percent_resv_prev` | Last year's % | % |
| `jan_info` | Cumulative inflow since Jan 1 | MCM |
| `q_info` | Today's inflow | MCM |
| `q_outfo` | Today's outflow/release | MCM |
| `water_workable` | Usable storage (curr − dead storage) | MCM |

### All large dams — live readings (POST)

```bash
# All large dams with today's data, grouped by region
curl -sL "https://app.rid.go.th/reservoir/api/dams" \
  -X POST -H "User-Agent: Mozilla/5.0" \
  -d "status=1"
```

Response: `date_th`, `year_prev`, `year_curr`, `regions[]` → each region has `region_name`, `dams[]`

Dam fields:

| Field | Description | Unit |
|---|---|---|
| `DAM_ID` | Dam ID | — |
| `DAM_Name` | Dam name (Thai) | — |
| `DAM_Group` | Region group | — |
| `DAM_Lat` / `DAM_Lon` | Coordinates | — |
| `DAM_QMax` | Total reservoir capacity | MCM |
| `DAM_QStore` | Active storage capacity | MCM |
| `DAM_QUsage` | Usable capacity | MCM |
| `DMD_QUse` | Current storage | MCM |
| `PERCENT_DMD_QUse` | Current storage % | % |
| `DMD_QUse_prev` | Storage same date last year | MCM |
| `PERCENT_DMD_QUse_prev` | Last year's % | % |
| `Jan_Curr` | Cumulative inflow since Jan 1 (this year) | MCM |
| `Jan_Prev` | Cumulative inflow since Jan 1 (last year) | MCM |
| `DMD_Inflow` | Today's inflow | m³/s |
| `SUM_Inflow` | Cumulative inflow YTD | MCM |
| `DMD_Outflow` | Today's outflow | m³/s |
| `SUM_Outflow` | Cumulative outflow YTD | MCM |
| `AVG_Year_Inflow` | Average annual inflow | MCM |

### Middle reservoir historical detail

```bash
# Daily data for a specific reservoir over a date range
curl -sL "https://app.rid.go.th/reservoir/api/rsvmiddle?rsvmiddle=rsv403&date_start=2026-01-01&date_end=2026-04-01" \
  -H "User-Agent: Mozilla/5.0"
```

Parameters: `rsvmiddle` (reservoir code e.g. `rsv403`), `date_start` (YYYY-MM-DD), `date_end` (YYYY-MM-DD)

Response: `reservoir_id`, `reservoir_name`, `reservoir_province`, `reservoir_coordinates` (lat/lng), `reservoir_date`, `reservoir_data[]`

Each daily record: `date`, `cap_resv`, `low_qdisc`, `qdisc_curr`, `percent_resv_curr`, `qdisc_prev`, `percent_resv_prev`, `q_info` (inflow), `q_outfo` (outflow), `water_workable`

The URL pattern `https://app.rid.go.th/reservoir/rsvmiddle/detail/{cresv}/{date_start}/{date_end}` is the browser-viewable version of this same data.

### Region list

```bash
curl -sL "https://app.rid.go.th/reservoir/api/region" \
  -H "User-Agent: Mozilla/5.0"
```

Returns 6 regions:

| ID | Code | English Name | Thai Name |
|---|---|---|---|
| 1 | N | North | ภาคเหนือ |
| 2 | NE | Northeast | ภาคตะวันออกเฉียงเหนือ |
| 3 | E | East | ภาคตะวันออก |
| 4 | C | Central | ภาคกลาง |
| 5 | W | West | ภาคตะวันตก |
| 6 | S | South | ภาคใต้ |

---

## 3. Flood Reports — water.rid.go.th

Public, no authentication required.

### Downloadable PDF reports

```bash
# Today's flood situation report (updated daily)
curl -sL "https://water.rid.go.th/flood/flood/daily.pdf" -o daily_flood.pdf

# Weekly flood situation report
curl -sL "https://water.rid.go.th/flood/flood/weekreportnew.pdf" -o weekly_flood.pdf
```

### Interactive HTML situation reports

Open in browser:

| URL | Description |
|---|---|
| `https://water.rid.go.th/flood/plan_new/planup.html` | Upper Chao Phraya water management plan |
| `https://water.rid.go.th/flood/plan_new/planlow.html` | Lower Chao Phraya water management plan |
| `https://water.rid.go.th/flood/flood/res_table.htm` | Historical reservoir table (calendar-based GIF viewer) |

---

## 4. WMSC Portal — wmsc.rid.go.th

The main portal links to dashboards and maps. Open in browser:

| URL | Description |
|---|---|
| `https://wmsc.rid.go.th/` | Main portal |
| `https://bigdata-swoc.rid.go.th/dashboard` | Big data dashboard |
| `https://app.rid.go.th/reservoir/` | Reservoir management app |
| `https://telerid.rid.go.th/` | Telemetry station viewer |

Regional hydrology centers (8 centers):
- `https://hydro-1.rid.go.th/` through `https://hydro-8.rid.go.th/`

---

## Quick reference: basin names in Thai

| English | Thai |
|---|---|
| Chao Phraya | เจ้าพระยา |
| Ping | ปิง |
| Wang | วัง |
| Yom | ยม |
| Nan | น่าน |
| Chi | ชี |
| Mun | มูล |
| Mekong | โขง |
| Mae Klong | แม่กลอง |
| Salween | สาละวิน |
| Tha Chin | ท่าจีน |

---

## About RID WMSC

ศูนย์ปฏิบัติการน้ำอัจฉริยะ (Smart Water Operations Center) is operated by กรมชลประทาน (Royal Irrigation Department, RID) to centralize real-time monitoring of Thailand's irrigation infrastructure: reservoirs, canals, pump stations, floodgates, and telemetry stations across all river basins.

- Portal: https://wmsc.rid.go.th
- Telerid: https://telerid.rid.go.th
- Reservoir app: https://app.rid.go.th/reservoir
- Flood reports: https://water.rid.go.th/flood
