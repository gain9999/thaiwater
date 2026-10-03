---
name: google-flood-hub
description: >-
  Queries the Google Flood Forecasting API (floodforecasting.googleapis.com) and extracts live Google Flood Hub river gauge alerts, hydrodynamic thresholds, discharge time series (hydrographs), return-period risk levels (Severe, Extreme), and inundation polygons. Use when asked to check flood risks, query river gauge forecasts, inspect discharge rates, find flood danger warnings in Thailand or globally, or interact with Google Flood Hub data.
---

# Google Flood Forecasting API & Flood Hub Skill

This skill provides comprehensive instructions, code patterns, and workflows for querying the Google Flood Forecasting One Platform API (`floodforecasting.googleapis.com/v1`) to retrieve real-time riverine flood alerts, return-period thresholds, discharge forecasts (hydrographs), and inundation maps.

---

## 1. Overview & Core Architecture

* **Service Host**: `https://floodforecasting.googleapis.com/v1`
* **Public Web Interface**: [https://sites.research.google/floods/](https://sites.research.google/floods/) (Flood Hub)
* **Official Documentation**: [https://developers.google.com/flood-forecasting](https://developers.google.com/flood-forecasting)
* **Authentication**: Requires a Google Cloud API Key with the Flood Forecasting API enabled on the GCP Project.
* **Underlying Model**: Google's AI Hydrological Model (*Nature* 627, 2024: "Global flood forecasting with machine learning") covering gauged and ungauged river basins across 80+ countries.

---

## 1b. Operational use — Chao Phraya corridor check (2026-10)

The working key on this VM is `/home/droid/.floodhub-api-key` (mode 600; never commit the value).
Nearest HYBAS reaches to the monitored RID stations (probe with `:searchGaugesByArea`, then
`:queryGaugeForecasts`):

| RID station | HYBAS reach |
|---|---|
| C.2 Nakhon Sawan | `hybas_4121104200` (15.715N 100.152E) |
| C.13 tail of Chao Phraya Dam | `hybas_4121582620` (15.185N 100.202E) |

Corridor reference points used by the helper: C.2 (15.7047, 100.1083), C.13 (15.16384, 100.18792),
C.3 Bang Phutsa (14.8850, 100.4010), C.7A Bang Kaeo (14.5620, 100.4400), CPY011 Ayutthaya
(14.36913, 100.52861).

- **Never mix Flood Hub numbers with RID/thaiwater numbers in one figure.** The HYBAS reaches are
  model units and diverge from the gauges (≈1,150 vs 2,340 m³/s at C.13) — quote Flood Hub only as
  shape/severity against Flood Hub's own return-period thresholds, with the gauge value given
  alongside and labelled separately.
- C.13 sits immediately below Chao Phraya Dam, so the dam release dominates its short-term level; a
  Flood Hub recession there is not a prediction of the release schedule.
- This project uses Flood Hub (not WeatherNext 3) for the C.13 station-linked corridor work; WN3 stays
  in use for basin-rain cross-checks.
- The corridor helper script (latest status, thresholds and 7-day discharge per point; writes
  `out/floodhub/*.json`) lives in the VM working copy only — ask before adding it to the repo.

---

## 2. API Endpoints Reference

### Key Endpoints

| Endpoint | Method | Purpose |
| :--- | :--- | :--- |
| `/v1/floodStatus:searchLatestFloodStatusByArea` | `POST` | Search gauges and active flood alerts by Country/Region Code (e.g. `TH`) or geographical polygon `loop`. |
| `/v1/floodStatus:queryLatestFloodStatusByGaugeIds` | `GET` | Retrieve latest flood status for up to 20,000 gauge IDs. |
| `/v1/gauges:searchGaugesByArea` | `POST` | Search gauge metadata by country code or loop. |
| `/v1/gauges:batchGet` | `GET` | Retrieve gauge metadata (coordinates, river name, site name). |
| `/v1/gaugeModels:batchGet` | `GET` | Retrieve hydrodynamic model return-period thresholds (`warningLevel`, `dangerLevel`, `extremeDangerLevel`) in $\text{m}^3/\text{s}$ or meters. |
| `/v1/gauges:queryGaugeForecasts` | `GET` | Retrieve complete 7-day hydrograph forecast time series (`forecastRanges` with lead-time values). |
| `/v1/flashFloods:search` | `POST` | Retrieve active and forecasted flash flood risk boundaries. |
| `/v1/serializedPolygons/{polygon_id}` | `GET` | Retrieve KML inundation polygons for flood hazard mapping. |

---

## 3. Severity & Return-Period Thresholds

The API categorizes river reach flooding into discrete severity levels:
- `NO_FLOODING`: Discharge/water level is within normal baseline.
- `ABOVE_NORMAL`: Flow exceeds typical seasonal mean.
- `SEVERE`: Flow breaches the **Warning / Danger Level** (~2- to 5-year return period).
- `EXTREME`: Flow breaches the **Extreme Danger Level** (~5- to 20+-year return period; high impact deluge).

---

## 4. Standard Python Workflows

### Environment
```bash
pip install requests pandas numpy
```

### Complete Query Recipe: Extract High-Risk Gauges for a Country
```python
import json
import numpy as np
import requests

API_KEY = "YOUR_GOOGLE_CLOUD_API_KEY"
BASE_URL = "https://floodforecasting.googleapis.com/v1"


def get_country_flood_alerts(region_code="TH"):
  """Searches all active flood statuses and identifies Severe/Extreme gauges."""
  url = f"{BASE_URL}/floodStatus:searchLatestFloodStatusByArea?key={API_KEY}"
  all_statuses = []
  page_token = None

  while True:
    payload = {
        "regionCode": region_code,
        "includeNonQualityVerified": True,
        "pageSize": 20000,
    }
    if page_token:
      payload["pageToken"] = page_token

    res = requests.post(url, json=payload)
    res.raise_for_status()
    data = res.json()
    statuses = data.get("floodStatuses", [])
    all_statuses.extend(statuses)
    page_token = data.get("nextPageToken")
    if not page_token:
      break

  high_risk = [
      s for s in all_statuses if s.get("severity") in ("EXTREME", "SEVERE")
  ]
  return all_statuses, high_risk


def get_gauge_thresholds(gauge_ids):
  """Batch gets model thresholds for a list of gauges."""
  model_names = [f"gaugeModels/{gid}" for gid in gauge_ids]
  url = (
      f"{BASE_URL}/gaugeModels:batchGet?key={API_KEY}&"
      + "&".join([f"names={n}" for n in model_names])
  )
  res = requests.get(url)
  res.raise_for_status()
  return {m["gaugeId"]: m for m in res.json().get("gaugeModels", [])}


def get_gauge_hydrographs(gauge_ids):
  """Queries 7-day discharge forecast time series for a list of gauges."""
  url = (
      f"{BASE_URL}/gauges:queryGaugeForecasts?key={API_KEY}&"
      + "&".join([f"gaugeIds={gid}" for gid in gauge_ids])
  )
  res = requests.get(url)
  res.raise_for_status()
  return res.json().get("forecasts", {})
```

### Parsing Peak Discharge & Exceedance Ratios
```python
def analyze_flood_crest(gauge_id, forecasts_data, models_data):
  """Extracts current discharge, peak crest value, peak date, and danger ratio."""
  gm = models_data.get(gauge_id, {})
  thresh = gm.get("thresholds", {})
  danger_level = thresh.get("dangerLevel")
  extreme_level = thresh.get("extremeDangerLevel")

  fc = forecasts_data.get(gauge_id, {}).get("forecasts", [])
  if not fc:
    return None

  latest_fc = fc[-1]  # Most recent model run
  ranges = latest_fc.get("forecastRanges", [])
  if not ranges:
    return None

  current_val = ranges[0].get("value")
  vals = [r.get("value", 0.0) for r in ranges]
  max_idx = int(np.argmax(vals))
  peak_val = vals[max_idx]
  peak_time = ranges[max_idx].get("forecastStartTime")

  ratio = (peak_val / extreme_level) if (extreme_level and extreme_level > 0) else None

  return {
      "gauge_id": gauge_id,
      "current_discharge_cms": current_val,
      "peak_discharge_cms": peak_val,
      "peak_time_iso": peak_time,
      "danger_threshold": danger_level,
      "extreme_threshold": extreme_level,
      "extreme_exceedance_ratio": ratio,
  }
```

---

## 5. Spatial Bounding Box & Coordinate Queries
If querying a specific viewport or sub-region (e.g., Central Thailand `14.0°N–15.5°N, 100.0°E–101.0°E`), either:
1. Filter the returned list by `gaugeLocation.latitude` and `gaugeLocation.longitude`.
2. Or supply a spherical polygon `loop` in `searchLatestFloodStatusByArea`:
```json
{
  "loop": {
    "vertices": [
      {"latitude": 14.0, "longitude": 100.0},
      {"latitude": 15.5, "longitude": 100.0},
      {"latitude": 15.5, "longitude": 101.0},
      {"latitude": 14.0, "longitude": 101.0}
    ]
  },
  "includeNonQualityVerified": true
}
```

---

## 6. Best Practices & Rules
* **Explicit Date Range**: Always confirm and state the forecast time range and timezone (e.g. Bangkok ICT `UTC+7`) at the very beginning of reports.
* **Non-Hallucinated Discharge**: Quote real float values in $\text{m}^3/\text{s}$ directly from `forecastRanges` and official thresholds from `gaugeModels`.
* **Lead Time Understanding**: Re-runs are generated multiple times daily as satellite inputs and upstream streamflow data update. Check `issuedTime` to ensure the forecast is fresh.
