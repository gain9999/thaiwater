---
name: egat
description: Fetch hydro dam and reservoir data from EGAT (Electricity Generating Authority of Thailand — การไฟฟ้าฝ่ายผลิตแห่งประเทศไทย)
---

Fetch and display EGAT dam and hydro reservoir data.
The user asked: $ARGUMENTS

## How to respond

1. Identify which data type the user wants.
2. Use Bash to call accessible JSON endpoints and present results in a clean table.
3. For real-time dam readings, note the SignalR limitation and direct the user to the HTML situation pages.

---

## System overview

EGAT operates Thailand's largest hydro dams (Bhumibol, Sirikit, Vajiralongkorn, etc.) and publishes water situation data across two sites:

| System | URL | Auth | Description |
|---|---|---|---|
| Water Situation | `https://water.egat.co.th` | No | Dam situation pages with embedded chart data |
| egatwater App | `https://egatwater.egat.co.th` | No | Interactive dashboard + CCTV |
| REST API | `https://api-egatwater.egat.co.th/api/` | No (static data) | Dam static info via JSON; real-time via SignalR |

---

## 1. REST API — api-egatwater.egat.co.th

**Base URL:** `https://api-egatwater.egat.co.th/api/`

### Dam list (public, no auth)

```bash
# All 69 EGAT dams — static info (capacity, coordinates, basin)
curl -sL "https://api-egatwater.egat.co.th/api/dam" \
  -H "User-Agent: Mozilla/5.0" -H "Accept: application/json"
```

Response fields per dam:

| Field | Description | Unit |
|---|---|---|
| `DAM_ID` | Dam ID (e.g. `1`) | — |
| `DAM_NAMT` | Dam name (Thai) | — |
| `STORAGE_MAX` | Maximum storage capacity | MCM |
| `STORAGE_NORMAL` | Normal high water level storage | MCM |
| `STORAGE_MIN` | Dead storage / minimum | MCM |
| `EFFECTIVE` | Effective storage (usable) | MCM |
| `BMAIN_ID` | Main basin ID | — |
| `SOURCE` | Water source / river name (Thai) | — |
| `lat` / `lon` | Coordinates | — |

**Note on real-time data:** Live storage, inflow, and outflow readings are delivered via SignalR WebSocket, not simple HTTP polling. The JSON API does not expose a REST endpoint for real-time readings — use the HTML situation pages below.

---

## 2. Water Situation Pages — water.egat.co.th

Public HTML pages, no auth required. Data is embedded in the page as FusionCharts XML — parse with `python3` or extract manually.

```bash
# Current dam situation (storage volume by dam)
curl -sL "http://water.egat.co.th/situation/situation_vol.php" \
  -H "User-Agent: Mozilla/5.0"

# Daily inflow table
curl -sL "http://water.egat.co.th/inflowDaily.php" \
  -H "User-Agent: Mozilla/5.0"

# Storage + inflow summary
curl -sL "http://water.egat.co.th/store_inflow.php" \
  -H "User-Agent: Mozilla/5.0"

# Storage + release summary
curl -sL "http://water.egat.co.th/store_release.php" \
  -H "User-Agent: Mozilla/5.0"
```

To extract the embedded chart data:
```bash
curl -sL "http://water.egat.co.th/situation/situation_vol.php" \
  -H "User-Agent: Mozilla/5.0" | \
  python3 -c "
import sys, re
html = sys.stdin.read()
charts = re.findall(r'<chart[^>]*>.*?</chart>', html, re.DOTALL)
for c in charts:
    print(c[:500])
"
```

### Daily table image

```bash
# Today's dam daily situation table (JPEG image — contains storage, inflow, outflow for all major dams)
curl -sL "http://water.egat.co.th/img/daily_table/image_1.jpg" -o egat_daily_table.jpg
```

---

## 3. egatwater Dashboard — egatwater.egat.co.th

Browser-only dashboard (React SPA, uses SignalR for live data):

| URL | Description |
|---|---|
| `https://egatwater.egat.co.th/` | Main live dashboard |
| `https://egatwater.egat.co.th/RealTimeCCTV` | Live CCTV cameras at dam sites |
| `https://egatwater.egat.co.th/DamDetail/{DAM_ID}` | Per-dam detail view |

---

## 4. Hydro Power Plants — ichpp.egat.co.th

EGAT's hydro power plant monitoring portal:

```
https://ichpp.egat.co.th/
```

Covers installed capacity, generation output, and plant-level status for all EGAT hydro plants. No public API — browse only.

---

## Key EGAT dams

| Dam ID | Name (TH) | River | Region |
|---|---|---|---|
| 1 | เขื่อนภูมิพล | Ping | North |
| 2 | เขื่อนสิริกิติ์ | Nan | North |
| 3 | เขื่อนวชิราลงกรณ | Kwai Yai | West |
| 4 | เขื่อนศรีนครินทร์ | Kwai Yai | West |
| 5 | เขื่อนรัชชประภา | Tapi | South |
| 6 | เขื่อนสิรินธร | Mun | Northeast |

---

## About EGAT Hydro

การไฟฟ้าฝ่ายผลิตแห่งประเทศไทย (EGAT) operates Thailand's major multi-purpose dams primarily for power generation, with secondary roles in flood control and water supply. Total hydro capacity exceeds 3,600 MW across 9 large dams and numerous smaller plants.

- Water situation: http://water.egat.co.th
- egatwater dashboard: https://egatwater.egat.co.th
- REST API base: https://api-egatwater.egat.co.th/api/
