# Thai Water & Weather Skills

A collection of [Claude Code](https://claude.ai/code) skill files for fetching live water, flood, and weather data from Thai government agencies.

Each skill is a `.md` file that acts as a slash command — invoke it by name and Claude will fetch and display the relevant data for you.

## Skills

| Skill | Source | Data |
|---|---|---|
| `/thaiwater` | thaiwater.net + HII | Dams, rainfall, water levels, flood roads, storms, ocean, radar, flash flood warnings, tide tables, storm surge, GSMaP |
| `/ews` | ews.dwr.go.th | Flash flood & landslide early warning stations (800+ nationwide) |
| `/tmd` | tmd.go.th | Weather observations, forecasts, NWP model output, earthquakes |
| `/dds_bangkok` | flood.bangkok.go.th | Bangkok drainage: canals, rain stations, water level, flood events |
| `/wmsc_rid` | wmsc.rid.go.th | RID reservoirs, telemetry stations, dam storage, flood reports |
| `/egat` | water.egat.co.th | EGAT hydro dams: storage, inflow, outflow, CCTV |
| `/gistda` | api-gateway.gistda.or.th | Satellite flood extent WMS layers, SAR flood mapping |
| `/onwr` | ntw.onwr.go.th | National water resource portal and policy data |
| `/ddpm` | disaster.go.th | Disaster warnings, flood situation reports, emergency alerts |
| `/rid_forecast` | water.rid.go.th | RID runoff / water-level forecasts (คาดการณ์น้ำท่า) as per-station charts, plus hydrology warning criteria and rainfall-runoff reference data |
| `/navy_tide` | กรมอุทกศาสตร์ + HII | Tide predictions for Thai coasts, including the Gulf and Bangkok (scriptable tide table + browser-only Navy dashboard) |
| `/water_situation_check` | (cross-skill) | The 6-step daily "is it getting worse?" routine that chains the skills above, the way Thai water analysts do it |
| `/ecmwf-ensemble-analysis` | ECMWF Open Data | Ensemble rainfall probabilities, percentiles, and Thailand maps (spatial diagnostics are not climatological EFI/SOT) |
| `/google-flood-hub` | Google Flood Forecasting API | River gauge alerts, discharge forecasts, return-period thresholds, and inundation polygons |
| `/weathernext3` | Google Cloud Storage | WeatherNext 3 global ensemble forecasts, rainfall probabilities, and regional plume/maps |

## Installation

### For this project only

Copy the skills you want into your project's `.claude/commands/` folder:

```bash
mkdir -p .claude/commands
cp skills/thaiwater.md .claude/commands/
cp skills/ews.md .claude/commands/
# etc.
```

### For all your projects (user-level)

```bash
mkdir -p ~/.claude/commands
cp skills/*.md ~/.claude/commands/
```

After copying, the skills are available as slash commands in Claude Code (e.g. `/thaiwater`, `/ews`).

## Usage

Invoke a skill with a natural-language request as the argument:

```
/thaiwater dam storage in the north
/thaiwater rainfall in Bangkok last 24 hours
/thaiwater flash flood risk areas right now
/thaiwater tide table for Gulf of Thailand today
/thaiwater storm surge stations Gulf coast
/thaiwater where is the water already over the river bank?
/ews show all critical stations right now
/ews water level trend for station STN0042
/tmd 7-day forecast for Chiang Mai
/dds_bangkok current water level on Bangkok canals
/wmsc_rid reservoir storage by region
/egat Bhumibol dam current storage and inflow
/gistda flood extent map for central Thailand
/onwr national water situation summary
/ddpm active flood warnings right now
/rid_forecast the Chao Phraya forecast chart at C.2
/navy_tide tide heights for Bangkok tomorrow
/water_situation_check should I worry about flooding this week?
/ecmwf-ensemble-analysis map ensemble rainfall risk for Thailand
/google-flood-hub check current river flood alerts in Thailand
/weathernext3 plot the next 5 days of ensemble rainfall for Thailand
```

## Data Sources

| Agency | System | Coverage |
|---|---|---|
| กรมทรัพยากรน้ำ (DWR) | EWS | Flash flood & landslide early warning, ~800 stations, 15-min updates |
| สสน. / thaiwater.net + HII | National Hydroinformatics | Dams, rainfall, water levels, flood roads, storms, ocean, satellite imagery, flash flood risk, tide tables, storm surge, GSMaP/PERSIANN |
| กรมอุตุนิยมวิทยา (TMD) | Data API + NWP | Surface observations, 3-km and 9-km NWP forecasts, earthquake data |
| สำนักการระบายน้ำ กทม. (DDS BMA) | flood.bangkok.go.th | Bangkok canal water levels, rain stations, flood events, polders |
| กรมชลประทาน (RID) | WMSC / Telerid | 921 telemetry stations, reservoir storage (medium + large dams) |
| การไฟฟ้าฝ่ายผลิต (EGAT) | water.egat.co.th | 69 large hydro dams: storage, inflow, outflow, CCTV |
| GISTDA | api-gateway.gistda.or.th | SAR satellite flood mapping, WMS flood extent layers |
| สทนช. (ONWR) | ntw.onwr.go.th | National water resource coordination and policy portal |
| กรมป้องกันฯ (DDPM) | disaster.go.th | Disaster warnings, flood situation reports (Cloudflare-protected — see skill for alternatives) |
| Google | Flood Forecasting API / WeatherNext 3 | Global river flood forecasts and AI weather ensemble data |
| กรมชลประทาน (RID) | water.rid.go.th/itcwater | Runoff / water-level forecasts (คาดการณ์น้ำท่า) as per-station charts; hydrology warning criteria, rainfall-runoff tables, yearbooks |
| กรมอุทกศาสตร์ กองทัพเรือ / HII | Apps Script dashboard / tide table | Tide predictions for Thai coastal sites (Navy dashboard is browser-only; HII provides machine-readable values) |

## Auth requirements

Most APIs are **public with no authentication required**. Exceptions:

- **TMD APIs** — registration required at [data.tmd.go.th](https://data.tmd.go.th/api/registerPre.php) (observational) and [data.tmd.go.th/nwpapi](https://data.tmd.go.th/nwpapi/register) (NWP). Free registration.
- **Telerid live readings** — station detail (`/main/station/{id}/`) requires a token. The station list and basin tree are public.
- **DDPM APIs** — protected by Cloudflare JS challenge; not accessible programmatically. The `/ddpm` skill documents accessible alternatives.
- **ONWR APIs** — protected by Cloudflare; use the ntw.onwr.go.th portal in a browser.
- **EGAT real-time readings** — delivered via SignalR WebSocket; the static dam list (`/api/dam`) is public REST JSON.
- **Google Flood Forecasting API** — requires a Google Cloud API key with the API enabled.
- **WeatherNext 3 full ensemble** — requires Google Cloud authentication and billing; the statistics store uses standard Google Cloud credentials.

## Network reachability caveats

Some hosts used by Thai analysts are not reachable from every network (verified 2026-09-25 from a cloud VM — TCP connect timeouts on both 80 and 443):

| Host | Content | Workaround |
|---|---|---|
| `hydro-2.rid.go.th` | RID Hydrology Center 2 live water-level / runoff viewer | use `thaiwater` `/public/waterlevel_load` or `wmsc_rid` Telerid |
| `hyd-app-db.rid.go.th` | River cross-section / flow SVG viewer per station | use `thaiwater` `/public/waterlevel_load` (`diff_wl_bank_text` = over-bank) + `rid_forecast` charts |

The skills mark these as browser-only rather than retrying them programmatically.
