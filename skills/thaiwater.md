---
name: thaiwater
description: Fetch live water, weather, and flood data from thaiwater.net (National Hydroinformatics Data Center)
---

Fetch and display data from the thaiwater.net public API. The API base is `https://api-v3.thaiwater.net/api/v1/thaiwater30/`.

The user asked: $ARGUMENTS

## How to respond

1. Parse the user's request to identify which data type they want (see categories below).
2. Use the Bash tool to `curl` the appropriate endpoint(s).
3. Parse the JSON and present data in a clean, readable table or summary — translate Thai field names where possible, show units, and highlight alert levels if present.
4. If the user did not specify a data type, list the available categories and ask them to pick one.

## Available data categories and endpoints

### Dam / Reservoir
- **All dams (latest):** `GET /analyst/dam`
- **By date and size:** `GET /analyst/dam?dam_date=YYYY-MM-DD&dam_size=large` (dam_size: `large` or `small`)
- **Yearly storage graph:** `GET /analyst/dam_yearly_graph?data_type=dam_storage&dam_id=ID&year=YYYY`
- **Small dam telemetry graph:** `GET /analyst/dam_small_tele_graph?data_type=volume&tele_station_id=ID&start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`

Key fields: `dam_name`, `dam_storage` (MCM), `dam_storage_percent` (%), `dam_inflow` (m³/s), `dam_released` (m³/s), `dam_level` (m MSL), `dam_spilled`, `dam_uses_water`

### Rainfall
- **Last 24 hours (all stations):** `GET /public/rain_24h`
- **By province:** `GET /public/rain_24h?province_code=10` (e.g. 10=Bangkok)
- **By river basin:** `GET /public/rain_24h?basin_code=12`
- **Today cumulative:** `GET /public/rain_today`
- **Yesterday:** `GET /public/rain_yesterday`
- **Monthly:** `GET /public/rain_monthly`
- **Yearly:** `GET /public/rain_yearly`
- **7-day forecast:** `GET /public/rain7day_forecast`
- **3/5/7/15-day province summary:** `GET /provinces/rain3d` | `rain5d` | `rain7d` | `rain15d`
- **Graph for a station:** `GET /provinces/rain7d_graph?station_id=ID&start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`

Key fields: `rain_24h` (mm), `rain_1h` (mm), `rainfall_datetime`, `station.tele_station_name`, `geocode.province_name`

### Water Level
- **All stations (latest):** `GET /public/waterlevel_load`
- **By basin:** `GET /public/waterlevel_load?basin_code=12`
- **Chao Phraya region:** `GET /public/waterlevel?province_code=10,11,12,13,73,74`
- **Historical graph:** `GET /public/waterlevel_graph?station_type=tele_waterlevel&station_id=ID&start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`
- **Yearly graph:** `GET /public/waterlevel_graph_year?station_type=tele_waterlevel&station_id=ID&year=YYYY`
- **Canal water level:** `GET /public/canal_waterlevel`
- **Canal graph:** `GET /public/waterlevel_graph?station_type=canal&station_id=ID&start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`

Key fields: `waterlevel_m`, `waterlevel_msl` (m), `discharge` (m³/s), `storage_percent` (%), `situation_level` (1=normal … 4=critical), `station.tele_station_name`, `station.warning_level_m`, `station.critical_level_msl`

### Water Gate (Floodgate)
- **All gates (latest):** `GET /public/watergate_load`
- **By basin:** `GET /public/watergate_load?basin_code=12`
- **Graph:** `GET /public/watergate_graph?station_id=ID&start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`

Key fields: `watergate_in` (m), `watergate_out` (m), `pump_on`, `floodgate_open`, `floodgate_height`

### River Flow / Discharge
- **All stations:** `GET /public/flow`
- **Graph:** `GET /public/flow_graph?station_id=ID&date_start=YYYY-MM-DD&date_end=YYYY-MM-DD`

### Flood Roads
- **Flooded road reports:** `GET /public/flood_road`
- **Graph:** `GET /public/flood_road_graph?station_id=ID&date_start=YYYY-MM-DD&date_end=YYYY-MM-DD`

### Weather Stations
- **Temperature:** `GET /public/thaiwater/temperature`
- **Humidity:** `GET /public/thaiwater/humid`
- **Pressure:** `GET /public/thaiwater/pressure`
- **Weather (combined):** `GET /public/thaiwater/weather`
- **Weather graph for station:** `GET /public/weather_graph?station_id=ID`
- **Temperature graph:** `GET /public/temperature_graph?station_id=ID&start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`

### Water Quality
- **Load stations:** `GET /analyst/waterquality_load`
- **By datetime:** `GET /analyst/waterquality_compare_datetime_graph?waterquality_station_id=ID&param=PARAM&date=YYYY-MM-DD`
- **By parameter:** `GET /analyst/waterquality_compare_param_graph?waterquality_station_id=ID&param=PARAM&start_datetime=YYYY-MM-DD`
- **Compare stations:** `GET /analyst/waterquality_compare_station_graph?waterquality_station_id=ID&param=PARAM&start_datetime=YYYY-MM-DD`
- **Compare with water level:** `GET /analyst/waterquality_compare_waterlevel_graph?waterquality_station_id=ID&param=PARAM&start_datetime=YYYY-MM-DD`

### Salinity (Chao Phraya)
- Site page: `/salinity` and `/report-salinity`

### Storm / Typhoon
- **Current storm data:** `GET /public/storm_data`
- **Historical storms:** `GET /analyst/storm_history_v2?name=NAME&month=MM&year=YYYY&storm_type=TYPE`
- **Yearly typhoon tracks:** `GET /analyst/typhoon_track_yearly`

Storm category scale: Depression (<34 kt), Tropical Storm (34–63 kt), Typhoon Cat 1–5 (64+ kt)

### Ocean / Wave / Sea
- **Wave forecast (station):** `GET /public/wave_forecast?station_id=ID`
- **Wave forecast image:** `GET /public/wave_forecast_img`
- **SWAN stations:** `GET /public/swan_station`
- **Sea surface temp image:** `GET /public/weather_img/sst_ocean_weather`

### CCTV
- **All CCTV cameras:** `GET /analyst/cctv` — returns list of flood/river CCTV stations with lat/lon and stream info

### Radar / Satellite Images
- **Current radar:** `GET /analyst/radar_img`
- **Radar history:** `GET /analyst/radar_history_img?date=YYYY-MM-DD&radar_type=TYPE&interval=15`
- **Cloud image:** `GET /public/weather_img/cloud`
- **Weather map (TMD):** `GET /public/weather_img/weather_map_tmd`
- **Upper wind (latest):** `GET /analyst/upper_wind_img`
- **Upper wind history:** `GET /analyst/upper_wind_history_img?height=LEVEL&month=YYYY-MM` — pressure level (e.g. `850`, `500`, `200` hPa)
- **Vertical wind history:** `GET /analyst/vertical_wind_history_img?month=YYYY-MM`
- **Wind 10m forecast (latest):** `GET /analyst/wind10m_forecast_img`
- **Wind 10m forecast history:** `GET /analyst/wind10m_forecast_history_img?year=YYYY`
- **Wind 10m forecast animation:** `GET /analyst/wind10m_forecast_animation_img`
- **Rain forecast animation:** `GET /analyst/rain_forecast_animation_img`
- **Rain forecast history:** `GET /analyst/rain_forecast_history_img?month=YYYY-MM`
- **Accumulated rainfall images:** `GET /analyst/rainaccumulat_img?year=YYYY`
- **Chao Phraya 48h rain history:** `GET /analyst/rain_chaopraya48_history_img`

### Ocean / Satellite Extended Images
- **Wave forecast image:** `GET /public/wave_forecast_img`
- **Wave forecast animation:** `GET /public/wave_forecast_animation_img` (also `?media_type=mp4`)
- **Wave forecast history:** `GET /analyst/wave_forecast_history_img?year=YYYY`
- **Sea surface height (HII):** `GET /public/weather_img/ssh_hii`
- **SST 2-week (HAII):** `GET /public/weather_img/sst_2w_haii`
- **SST ocean weather:** `GET /public/weather_img/sst_ocean_weather`
- **Wave height ocean weather:** `GET /public/weather_img/wave_height_ocean_weather`
- **Indian Ocean analysis (UCL):** `GET /public/weather_img/india_ocean_ucl`
- **Pacific Ocean analysis (UCL):** `GET /public/weather_img/pacific_ocean_ucl`
- **MODIS NDVI (USDA):** `GET /public/weather_img/modis_ndvi_usda`
- **MODIS precipitation (USDA):** `GET /public/weather_img/modis_precipitation_usda`
- **MODIS soil moisture (USDA):** `GET /public/weather_img/modis_soil_moisture_usda`
- **Contour image:** `GET /public/weather_img/contour_image`
- **Image generate (latest dam/flood images):** `GET /public/weather_img/image_generate`
- **Animation by agency:** `GET /public/weather_img/animation?agency_id=ID&media_type_id=ID`

### Weather History Images
- **By date:** `GET /public/weather_history_img/date?agency_id=ID&media_type_id=ID&date=YYYY-MM-DD`
- **By date range:** `GET /public/weather_history_img/date_range?agency_id=ID&media_type_id=ID&start=YYYY-MM-DD&end=YYYY-MM-DD`
- **By month:** `GET /public/weather_history_img/month?agency_id=ID&media_type_id=ID&month=YYYY-MM`
- **By year:** `GET /public/weather_history_img/year?year=YYYY`

### Station Lookup
- **All stations by province:** `GET /frontend/shared/station_all?province_code=10`
- **Canal stations:** `GET /frontend/shared/tele_canal_station?province_code=10`
- **Watergate stations:** `GET /frontend/shared/watergate_station?province_code=10`
- **PM2.5 stations:** `GET /frontend/shared/pm25_station?province_code=10`

### Iframe / Embed Data
- **Rain 24h province list (for iframe selector):** `GET /iframe/rain24`
- **Water level province list (for iframe selector):** `GET /iframe/waterlevel`

### Main Dashboard / Summary
- **National summary:** `GET /public/thaiwater_main`
- **Thailand overview:** `GET /public/thailand`
- **Main rain by province:** `GET /public/thailand_main_rain?province_code=10`
- **Dam uses water (major dams):** `GET /provinces/dam_uses_water?dam_id=1,11,12,36`

## Common province codes
10=Bangkok, 11=Samut Prakan, 12=Nonthaburi, 13=Pathum Thani, 50=Chiang Mai, 53=Uttaradit, 60=Nakhon Sawan, 73=Nakhon Pathom, 74=Samut Sakhon, 86=Chumphon

## Common basin codes
1=Ping, 2=Wang, 3=Yom, 4=Nan, 5=Mun, 6=Chi, 7=Mekong, 8=Ruak, 9=Nan (lower), 10=Chao Phraya, 11=Sakae Krang, 12=Pasak, 13=Tha Chin, 14=Mae Klong, 19=Peninsula Upper East, 20=Peninsula Upper West

---

## HII APIs (Hydro and Agro Informatics Institute — สสน.)

HII operates several data systems, all accessible without user registration. Tokens below are embedded in the thaiwater.net JS bundle.

### HII Flash Flood Risk API

```bash
# Areas at risk of flash flood in the next 24 hours
curl -sL "https://api.hii.or.th/v2/4UQaYnf0Bx4fXPYyCdDRbqHyXH9Ixvd2nVUjaN1cLBY=/warning/flashflood-24h" \
  -H "User-Agent: Mozilla/5.0"

# Areas at risk in the next 48 hours
curl -sL "https://api.hii.or.th/v2/4UQaYnf0Bx4fXPYyCdDRbqHyXH9Ixvd2nVUjaN1cLBY=/warning/flashflood-48h" \
  -H "User-Agent: Mozilla/5.0"
```

Response fields:

| Field | Description |
|---|---|
| `date` / `time` | Report timestamp |
| `type` | Warning type description (Thai) |
| `area[]` | Stations in active risk zones |
| `area_nearby[]` | Nearby monitoring stations (48h only) |
| `noData` | Thai message when no areas are at risk |
| `riskMap` | URL of the current risk map PNG image |
| `bannerWarning` | Boolean — whether to show a warning banner |

Each `area` entry fields: `id`, `geocode`, `tambon`, `amphoe`, `province`, `region_id`, `region_name`, `oldcode`, `name` (station code), `agency`, `latitude`, `longitude`, `sum_rainfall_24h` or `sum_rainfall_48h` (mm), `latest_rainfall_datetime`

---

### HII fews2 Data Portal (flat-file CSV, no auth)

Base URL: `https://fews2.hii.or.th/model-output/data_portal/`

```bash
# Flash flood risk report — all tambons nationwide with FFPI index
curl -sL "https://fews2.hii.or.th/model-output/data_portal/flashflood/flashflood_report.txt"
# CSV fields: tambon_id, province, district, subdistrict, FFPI, rain_1d_forecast, monitoring_station, basin

# Active tropical storms / depressions
curl -sL "https://fews2.hii.or.th/model-output/data_portal/flashflood/storm.txt"
# CSV fields: name, file (image filename), lat, long

# Drought index report — all tambons with DRI score
curl -sL "https://fews2.hii.or.th/model-output/data_portal/drought/drought_dri_report.txt"
# CSV fields: tambon_id, province, district, subdistrict, d_score, d_meaning (Thai), event_date

# Water level station metadata with alarm/warning/critical thresholds
curl -sL "https://fews2.hii.or.th/model-output/data_portal/metadata/hii_waterlevel.csv"

# RID discharge station metadata with thresholds
curl -sL "https://fews2.hii.or.th/model-output/data_portal/metadata/rid_discharge.csv"

# Salinity monitoring stations (Chao Phraya S02–S09)
curl -sL "https://fews2.hii.or.th/model-output/data_portal/metadata/mwa_salinity.csv"

# Latest 24-hour accumulated rainfall radar image (PNG)
curl -sL "https://fews2.hii.or.th/model-output/data_portal/radar/latest/png/rain24hrs.png" -o rain24hrs.png
```

#### Tide table — Gulf of Thailand stations

```bash
# Daily tide predictions — 9 Gulf of Thailand stations (4-hourly + max/min)
curl -sL "https://fews2.hii.or.th/model-output/data_portal/tide_table/summary.txt"
```

CSV fields: `code`, `station.name.TH`, `station.name.EN`, `lat`, `long`, `date`, `max_value` (m), `max_time`, `min_value` (m), `min_time`, `time_0000`, `time_0400`, `time_0800`, `time_1200`, `time_1600`, `time_2000`

Stations covered: Navy HQ (Sattahip), Bangkok Harbour, Fort Chulachomklao, Bangkok Bar, Tha Chin River mouth, Hua Hin, Rayong, Ao Sattahip, Ko Sichang

---

### HII tiservice API

Two tokens — use the correct one per endpoint:
- `TOKEN_SURGE` = `cEniGCuZcTBSa3xj4A8PY187BhpExTfE` (storm surge / wave)
- `TOKEN_ISO` = `MBtOTp6IUXbjaCxhQoFQNrFgZUCzNgbo` (isohyet, PWV, GSMaP)

```bash
# Storm surge monitoring stations — 26 Gulf coast stations with warning status
curl -sL "https://api.hii.or.th/tiservice/v1/ws/cEniGCuZcTBSa3xj4A8PY187BhpExTfE/model/stromsurge/station_info" \
  -H "User-Agent: Mozilla/5.0"

# Wave/storm surge animation (latest MP4 and GIF URLs)
curl -sL "https://api.hii.or.th/tiservice/v1/ws/cEniGCuZcTBSa3xj4A8PY187BhpExTfE/stromsurge/wave/antimation/high_wave/lastest" \
  -H "User-Agent: Mozilla/5.0"
# Response: {Mp4:{date,time,file}, Gif:{date,time,file}}

# Isohyet (rainfall contour) images by province — rain_1d, rain_3d, rain_7d
# PROV_CODE = 2-digit province code (e.g. 10 = Bangkok, 50 = Chiang Mai)
curl -sL "https://api.hii.or.th/tiservice/v1/ws/MBtOTp6IUXbjaCxhQoFQNrFgZUCzNgbo/isohyet/daily/latest/province/10" \
  -H "User-Agent: Mozilla/5.0"
# Response: {image:{rain_1d, rain_3d, rain_7d} (PNG URLs), geotiff, ascii}

# Precipitable Water Vapor (PWV) latest image
curl -sL "https://api.hii.or.th/tiservice/v1/ws/MBtOTp6IUXbjaCxhQoFQNrFgZUCzNgbo/pwv/latest" \
  -H "User-Agent: Mozilla/5.0"

# GSMaP / PERSIANN satellite rainfall products (latest)
curl -sL "https://api.hii.or.th/v2/MBtOTp6IUXbjaCxhQoFQNrFgZUCzNgbo/model/gsmap/latest2" \
  -H "User-Agent: Mozilla/5.0"
# Response: {GSMaP_10km:[], GSMaP_25km:[], PERSIANN_4km:[]} — arrays of image URLs
```

Storm surge station fields: `id`, `name` (Thai/EN), `lat`, `lon`, `monitoring_level` (m), `warning_level` (m), `status`, `color`

---

### HII Urban / BMA Radar API

```bash
TOKEN_URBAN="oeLrEjIwGpHaT7pQ1p3kB2iZa6kRcYEXy0GGb75nLpPQxHqOU6"
curl -sL "http://hydro-hims.hii.or.th/service/api/urban/data?token=${TOKEN_URBAN}" \
  -H "User-Agent: Mozilla/5.0"
```

Response structure:
- `system` — system name
- `data[]` — array of `{time, url (PNG), status}`
- `metadata` — `{radar_name, unit, colorbar (URL), xmin, xmax, ymin, ymax}`
- `colorbar` — color-to-rainfall legend

---

## How to call the API
```bash
curl -sL "https://api-v3.thaiwater.net/api/v1/thaiwater30/ENDPOINT" -H "Accept: application/json" | python3 -m json.tool
```

No authentication required for all `/public/` and `/analyst/` endpoints listed above.

## Situation levels (water level alerts)
- Level 1: Normal (green)
- Level 2: Watch (yellow)  
- Level 3: Warning (orange)
- Level 4: Critical / Flood risk (red)
