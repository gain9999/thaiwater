---
name: dds_bangkok
description: Fetch Bangkok drainage, flood, rainfall, and water level data from dds.bangkok.go.th — Department of Drainage and Sewerage, Bangkok Metropolitan Administration (สำนักการระบายน้ำ กรุงเทพมหานคร)
---

Fetch and display Bangkok drainage and flood data from DDS BMA systems.
The user asked: $ARGUMENTS

## How to respond

1. Identify which system and data type the user wants.
2. Note which endpoints require login (see Auth notes below).
3. Use Bash to call accessible endpoints; present results in a clean table.
4. For auth-required APIs, explain the login flow and what data will be available after authentication.

---

## System overview

DDS Bangkok operates several separate systems:

| System | URL | Auth | Description |
|---|---|---|---|
| Main website | `https://dds.bangkok.go.th/index2.php` | No | News, reports, documents |
| Drainage Info System | `https://flood.bangkok.go.th` | **No** (public API) | Live rain/water/flood monitoring |
| Telemetry | `https://weather.bangkok.go.th` | Unknown | Real-time sensor data |
| Flood Risk Map | ArcGIS Dashboard | No | Bangkok flood risk points |
| Data Center | `https://datacenter.dds.bangkok.go.th` | Unknown | DDS data center |
| E-Service | `https://dxs.dds.bangkok.go.th/public` | Partial | Drainage service requests |

---

## 1. Drainage Information System — flood.bangkok.go.th

**Base API URL:** `https://flood.bangkok.go.th/api/`

**Auth:** Not required for the endpoints listed below. All are public.

### How to call

```bash
curl -sL "https://flood.bangkok.go.th/api/ENDPOINT" -H "User-Agent: Mozilla/5.0"
```

---

### Reference / Lookup endpoints

#### Districts

```bash
curl -sL "https://flood.bangkok.go.th/api/district/all" -H "User-Agent: Mozilla/5.0"
```

Returns all Bangkok districts. Fields: `id`, `name` (Thai), `name_en`, `zone_id`, `area` (km²), `latitude`, `longitude`, `utm_x`, `utm_y`

#### Sub-districts (แขวง)

```bash
curl -sL "https://flood.bangkok.go.th/api/subdistrict/all" -H "User-Agent: Mozilla/5.0"
```

Fields: `id`, `name` (Thai), `name_en`, `district_id`, `area`, `latitude`, `longtitude`, `utm_x`, `utm_y`

#### Polders (drainage management zones)

```bash
curl -sL "https://flood.bangkok.go.th/api/polder/all" -H "User-Agent: Mozilla/5.0"
```

Fields: `ID` (e.g. `FC01`), `display` (Thai), `display_en`, `area`, `latitude`, `longitude`, `utm_x`, `utm_y`

#### Canal/river list

```bash
curl -sL "https://flood.bangkok.go.th/api/water/riverlist" -H "User-Agent: Mozilla/5.0"
```

Fields: `river_id`, `river_name` (Thai), `river_name_en`

#### Alert thresholds (color scale reference)

```bash
# Rainfall thresholds
curl -sL "https://flood.bangkok.go.th/api/rain/threshold" -H "User-Agent: Mozilla/5.0"
# → [{"value":"ไม่มีฝน","value_en":"None","color":"#FFFFFF"}, {"value":"ฝนเล็กน้อย","value_en":"Low","color":"#0BC100"}, {"value":"ฝนหนัก","value_en":"Heavy","color":"#FFAA00"}, {"value":"ฝนหนักมาก","value_en":"Pouring","color":"#FF0000"}]

# Flood depth thresholds (cm)
curl -sL "https://flood.bangkok.go.th/api/flood/threshold" -H "User-Agent: Mozilla/5.0"
# → [{"value":"0","color":"#FFFFFF"}, {"value":"<5","color":"#0BC100"}, {"value":"5-10","color":"#FFAA00"}, {"value":">10","color":"#FF0000"}]

# Water level thresholds
curl -sL "https://flood.bangkok.go.th/api/water/threshold" -H "User-Agent: Mozilla/5.0"
# → [{"value":"ปกติ","value_en":"Normal","color":"#0BC100"}, {"value":"เตือนภัย","value_en":"Warning","color":"#FFAA00"}, {"value":"วิกฤต","value_en":"Critical","color":"#FF0000"}]
```

---

### Live status endpoints

#### Current active events

```bash
# Active flood events (empty array when none)
curl -sL "https://flood.bangkok.go.th/api/flood/currentevent" -H "User-Agent: Mozilla/5.0"

# Active rain events (empty array when none)
curl -sL "https://flood.bangkok.go.th/api/rain/currentevent" -H "User-Agent: Mozilla/5.0"
```

#### Water level stations — latest readings

```bash
# All main water level stations with latest reading and status
curl -sL "https://flood.bangkok.go.th/api/mainwater/lastdata/0" -H "User-Agent: Mozilla/5.0"
```

Response fields per station:

| Field | Description |
|---|---|
| `st_code` | Station code (e.g. `WL.BCN.02`) |
| `site_time` | Timestamp (ISO 8601 UTC) |
| `wl_in` | Water level (m MSL, in-canal) |
| `wl_m` | Water level (m MSL) |
| `st_name` | Station name (Thai) |
| `st_name_en` | Station name (English) |
| `latitude` / `longitude` | Coordinates |
| `utm_x` / `utm_y` | UTM coordinates |
| `desc_display` / `desc_display_en` | Measurement description |
| `unit_display` / `unit_display_en` | Unit (e.g. `m.msl.`) |
| `status` | `normal` / `warning` / `critical` |
| `color` | Hex color matching threshold (`#0BC100` / `#FFAA00` / `#FF0000`) |

#### Rain station status (with params)

```bash
# Rain station statuses at a specific datetime, with 5-minute period
# Returns empty array if no rainfall at that time
curl -sL "https://flood.bangkok.go.th/api/rain/stationstatus_dt?period=5&datetime=2026-04-20T21:53:00Z" \
  -H "User-Agent: Mozilla/5.0"
```

Parameters: `period` (minutes, e.g. `5`), `datetime` (ISO 8601 UTC)

---

### Historical & forecast endpoints

#### Water level history

```bash
# Time-series water level readings for a station
curl -sL "https://flood.bangkok.go.th/api/water/history?period=5&st_code=WL.BCN.02&stdate=2026-04-20T15:53:00Z&enddate=2026-04-20T21:53:00Z" \
  -H "User-Agent: Mozilla/5.0"
```

Parameters: `period` (minutes), `st_code` (station code), `stdate` / `enddate` (ISO 8601 UTC)

Returns array of `{st_code, site_time, wl_in}` records.

#### Water level forecast

```bash
# Forecast readings for a station (next few hours)
curl -sL "https://flood.bangkok.go.th/api/water/forecastdata/WL.BCN.02" \
  -H "User-Agent: Mozilla/5.0"
```

Returns array of `{st_code, site_time, wl_in}` records with future timestamps.

---

### Other documented endpoints (not yet live-tested)

| Endpoint | Description |
|---|---|
| `GET rain/forecastdata/{station_code}` | Rain forecast for a station |
| `GET rain/history` | Historical rain records (likely needs params like water/history) |
| `GET rain/info/{id}` | Rain station detail by ID |
| `GET rain/infoByDistrict/{district_id}` | Rain stations in a district |
| `GET water/stationstatus_dt` | All water level stations (likely needs period/datetime params) |
| `GET water/info/{id}` | Water station detail by ID |
| `GET water/infoByDistrict/{district_id}` | Water stations in a district |
| `GET water/WlOnCanal` | Water level readings on canals |
| `GET flood/stationstatus_dt` | All flood monitoring stations |
| `GET flood/forecastdata/{station_code}` | Flood forecast for a station |
| `GET flood/history` | Historical flood records |
| `GET flood/info/{id}` | Flood event/station detail by ID |
| `GET flood/infoByDistrict/{district_id}` | Flood events by district |
| `GET flow/history` | Historical flow records |
| `GET flow/info/{id}` | Flow station detail by ID |
| `GET flow/infoByDistrict/{district_id}` | Flow data by district |
| `GET notifications` | System notifications / alerts |
| `GET counter/getcounter/web` | Page view counter (`[{"count": N}]`) |

---

## 2. Main website — public content

No auth required. Access via browser or curl.

### Daily situation reports (ข้อมูลประจำวัน)

```bash
# List latest daily reports
curl -sL "https://dds.bangkok.go.th/content/prnews/index.php" | \
  grep -oE 'href="detail\.php\?id=[^"]*"'

# Fetch a specific report (replace ID)
curl -sL "https://dds.bangkok.go.th/content/prnews/detail.php?id=11141&type=2"
```

### Official announcements (ประกาศสำนักการระบายน้ำ)
```bash
curl -sL "https://dds.bangkok.go.th/content/news/index.php"
```

### Project data
```bash
curl -sL "https://dds.bangkok.go.th/project_data.php"
```

### Downloadable documents
- Canal drainage plan (PDF): `https://dds.bangkok.go.th/public_content/files/001/0006030_1.pdf` (sea level data)
- Download forms: `https://dds.bangkok.go.th/download/download01.html`

---

## 3. Flood risk map (public ArcGIS Dashboard)

No auth required — open in browser:
```
https://bmasedgis.bangkok.go.th/portal/apps/dashboards/a3d8a9fa438f4e219d56a3be16fcce5e
```
Shows: Bangkok flood-prone area points, risk levels by district, real-time overlays.

---

## 4. Water management map

```
https://u.bangkok.go.th/drainagemapnew
```
Interactive map of Bangkok's drainage network (canals, pipes, pump stations, gates).

---

## 5. Online invert level approval system

For pipe invert level requests:
```
https://disd.bangkok.go.th/invertlevelrequest/
```

---

## Bangkok district codes (for `infoByDistrict` endpoints)

Bangkok has 50 districts (เขต). Common ones:

| Code | District (EN) | District (TH) |
|---|---|---|
| 1001 | Phra Nakhon | พระนคร |
| 1002 | Dusit | ดุสิต |
| 1003 | Nong Chok | หนองจอก |
| 1004 | Bang Rak | บางรัก |
| 1005 | Bang Khen | บางเขน |
| 1006 | Bang Kapi | บางกะปิ |
| 1007 | Pathum Wan | ปทุมวัน |
| 1008 | Pom Prap | ป้อมปราบ |
| 1009 | Phra Khanong | พระโขนง |
| 1010 | Min Buri | มีนบุรี |
| 1011 | Lat Krabang | ลาดกระบัง |
| 1012 | Yan Nawa | ยานนาวา |
| 1013 | Samphanthawong | สัมพันธวงศ์ |
| 1014 | Phaya Thai | พญาไท |
| 1015 | Thon Buri | ธนบุรี |
| 1016 | Bangkok Yai | บางกอกใหญ่ |
| 1017 | Huai Khwang | ห้วยขวาง |
| 1018 | Khlong San | คลองสาน |
| 1019 | Taling Chan | ตลิ่งชัน |
| 1020 | Bangkok Noi | บางกอกน้อย |
| 1021 | Bang Khun Thian | บางขุนเทียน |
| 1022 | Phasi Charoen | ภาษีเจริญ |
| 1023 | Nong Khaem | หนองแขม |
| 1024 | Rat Burana | ราษฎร์บูรณะ |
| 1025 | Khlong Toei | คลองเตย |
| 1026 | Suan Luang | สวนหลวง |
| 1027 | Chom Thong | จอมทอง |
| 1028 | Don Mueang | ดอนเมือง |
| 1029 | Ratchathewi | ราชเทวี |
| 1030 | Lat Phrao | ลาดพร้าว |
| 1031 | Wang Thonglang | วังทองหลาง |
| 1032 | Khlong San | คลองสาน |
| 1033 | Khan Na Yao | คันนายาว |
| 1034 | Saphan Sung | สะพานสูง |
| 1035 | Wang Thonglang | วังทองหลาง |
| 1036 | Khlong Sam Wa | คลองสามวา |
| 1037 | Bang Na | บางนา |
| 1038 | Thawi Watthana | ทวีวัฒนา |
| 1039 | Thung Khru | ทุ่งครุ |
| 1040 | Bang Bon | บางบอน |

---

## About DDS Bangkok

สำนักการระบายน้ำ กรุงเทพมหานคร (Department of Drainage and Sewerage, BMA) manages Bangkok's entire drainage infrastructure: 2,604 km of canals (khlongs), storm drains, 469 pump stations, and flood gates across all 50 districts.

- Website: https://dds.bangkok.go.th
- Drainage Info System: https://flood.bangkok.go.th
- Flood risk map: https://bmasedgis.bangkok.go.th/portal/apps/dashboards/a3d8a9fa438f4e219d56a3be16fcce5e
