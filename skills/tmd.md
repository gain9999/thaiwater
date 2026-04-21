---
name: tmd
description: Fetch weather forecasts and meteorological observations from tmd.go.th — Thai Meteorological Department (กรมอุตุนิยมวิทยา)
---

Fetch and display weather data from the Thai Meteorological Department (TMD).
TMD provides two separate API systems — one for observations/forecasts, one for high-resolution NWP model output. **Both require registration credentials.**

The user asked: $ARGUMENTS

## How to respond

1. Identify which API and data type the user wants.
2. If credentials are needed and not provided, explain how to register and what placeholder to use.
3. Use Bash to call the endpoint, parse JSON/XML, and present results in a readable table.
4. For image/chart URLs returned by the API, display the URL so the user can open it.

---

## API 1 — Observational & Forecast Data (`data.tmd.go.th/api/`)

**Registration required:** `https://data.tmd.go.th/api/registerPre.php`
After registering you receive a `uid` (user ID) and `ukey` (API key).

### Base call pattern
```bash
curl -sL "https://data.tmd.go.th/api/{APIName}/V{N}/?uid=YOUR_UID&ukey=YOUR_UKEY&format=json"
```

### Available APIs

| API Name | Ver | Description |
|---|---|---|
| `WeatherToday` | V2 | Daily surface observations at 07:00 — temp, humidity, rainfall, wind, pressure |
| `Weather3Hours` | V2 | 3-hourly synoptic observations (01:00, 04:00, 07:00, 10:00, 13:00, 16:00, 19:00, 22:00) from ~122–125 stations |
| `ThailandMonthlyRainfall` | V1 | Monthly rainfall totals and rainy-day counts per station; specify `?year=YYYY` |
| `ThailandClimateNormal` | V1 | Climate normals 1981–2010 (temperature, rainfall statistics) |
| `RainRegions` | V1 | Rainfall observations aggregated by region |
| `Station` | V1 | Full list of TMD meteorological stations (name, location, instruments) |
| `DailySeismicEvent` | V1 | Daily earthquake report — events in Thailand, nearby regions, and globally |

### Example calls

```bash
# Today's surface weather at all stations
curl -sL "https://data.tmd.go.th/api/WeatherToday/V2/?uid=UID&ukey=UKEY&format=json"

# 3-hourly observations
curl -sL "https://data.tmd.go.th/api/Weather3Hours/V2/?uid=UID&ukey=UKEY&format=json"

# Monthly rainfall for 2025
curl -sL "https://data.tmd.go.th/api/ThailandMonthlyRainfall/V1/?uid=UID&ukey=UKEY&format=json&year=2025"

# Climate normals
curl -sL "https://data.tmd.go.th/api/ThailandClimateNormal/V1/?uid=UID&ukey=UKEY&format=json"

# Rainfall by region
curl -sL "https://data.tmd.go.th/api/RainRegions/V1/?uid=UID&ukey=UKEY&format=json"

# All meteorological stations
curl -sL "https://data.tmd.go.th/api/Station/V1/?uid=UID&ukey=UKEY&format=json"

# Today's earthquake report
curl -sL "https://data.tmd.go.th/api/DailySeismicEvent/V1/?uid=UID&ukey=UKEY&format=json"
```

Supports `format=json` or `format=xml`.

---

## API 2 — NWP High-Resolution Forecast (`data.tmd.go.th/nwpapi/`)

**Registration required:** `https://data.tmd.go.th/nwpapi/register`
After registering, generate an OAuth 2.0 access token and include it as a Bearer token.

**Documentation:** `https://data.tmd.go.th/nwpapi/doc/`

### Two domains

| Domain | Resolution | Forecast horizon | Interval |
|---|---|---|---|
| Domain 1 | 9 km | 10 days ahead | 3-hourly |
| Domain 2 | 3 km | 72 hours ahead | Hourly |

### Auth header
```bash
-H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Forecast by coordinates (lat/lon)

```bash
# Hourly forecast at a lat/lon point (Domain 2, 3km)
curl -sL "https://data.tmd.go.th/nwpapi/v1/forecast/location/hourly/at?lat=13.75&lon=100.52&fields=tc,rh,rain,ws10m,wd10m,slp&duration=24" \
  -H "Authorization: Bearer TOKEN"

# Daily forecast at a lat/lon point (Domain 1, 9km)
curl -sL "https://data.tmd.go.th/nwpapi/v1/forecast/location/daily/at?lat=13.75&lon=100.52&fields=tc,rh,rain,ws10m,wd10m&duration=7" \
  -H "Authorization: Bearer TOKEN"
```

### Forecast by place name

```bash
# Hourly by place name
curl -sL "https://data.tmd.go.th/nwpapi/v1/forecast/location/hourly/place?place=Bangkok&fields=tc,rh,rain&duration=24" \
  -H "Authorization: Bearer TOKEN"

# Daily by place name
curl -sL "https://data.tmd.go.th/nwpapi/v1/forecast/location/daily/place?place=Chiang+Mai&fields=tc,rh,rain&duration=7" \
  -H "Authorization: Bearer TOKEN"
```

### Forecast by region

```bash
# Hourly by region code
curl -sL "https://data.tmd.go.th/nwpapi/v1/forecast/location/hourly/region?region=REGION_CODE&fields=tc,rh,rain&duration=24" \
  -H "Authorization: Bearer TOKEN"
```

### Area forecast (bounding box)

```bash
# Hourly for a bounding box (minLat, maxLat, minLon, maxLon)
curl -sL "https://data.tmd.go.th/nwpapi/v1/forecast/area/hourly/bbox?minLat=13.0&maxLat=14.5&minLon=100.0&maxLon=101.5&fields=tc,rain&duration=6" \
  -H "Authorization: Bearer TOKEN"

# By basin (river basin code)
curl -sL "https://data.tmd.go.th/nwpapi/v1/forecast/area/hourly/basin?basin=BASIN_CODE&fields=tc,rain&duration=24" \
  -H "Authorization: Bearer TOKEN"
```

### Common forecast fields (`fields` parameter)

| Field | Description | Unit |
|---|---|---|
| `tc` | Temperature | °C |
| `rh` | Relative humidity | % |
| `rain` | Rainfall | mm |
| `ws10m` | Wind speed at 10m | m/s |
| `wd10m` | Wind direction at 10m | degrees |
| `slp` | Sea level pressure | hPa |
| `psfc` | Surface pressure | hPa |
| `cld` | Cloud cover | % |

---

## Public content (no auth required)

TMD publishes the following without credentials on their website:

| Content | URL |
|---|---|
| 7-day national forecast | `https://www.tmd.go.th/en/forecast/thailand/7days` |
| Weather warnings | `https://www.tmd.go.th/warningpage` |
| Earthquake warnings | `https://www.tmd.go.th/warning-earthquake/earthquakewarning` |
| Heavy rain warnings | `https://www.tmd.go.th/warning-rain/warning-rain` |
| Storm warnings | `https://www.tmd.go.th/warning-strom/warning-strom` |
| Synoptic charts | `https://www.tmd.go.th/supportData/synopticCharts` |
| Tropical cyclone history | `https://www.tmd.go.th/climate/climateStat/TropicalCyclone` |
| Open data portal | `https://data.tmd.go.th/` |
| NWP historical CSV/data | `https://hpc.tmd.go.th/pubData` |
| Storm track shapefile (69yr) | `https://data.tmd.go.th/dataset/stat/stormtrack/shp/stormtrack69.zip` |

Fetch public pages with:
```bash
curl -sL "https://www.tmd.go.th/warningpage"
```

---

## About TMD

กรมอุตุนิยมวิทยา (Thai Meteorological Department) is Thailand's national meteorological authority, providing weather observation, forecasting, warnings, and earthquake monitoring. Hotline: 1182.
- Website: https://www.tmd.go.th
- Open data: https://data.tmd.go.th
- NWP API docs: https://data.tmd.go.th/nwpapi/doc/
- Observational API docs: https://data.tmd.go.th/api/index1.php
