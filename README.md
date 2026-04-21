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
/ews show all critical stations right now
/ews water level trend for station STN0042
/tmd 7-day forecast for Chiang Mai
/dds_bangkok current water level on Bangkok canals
/wmsc_rid reservoir storage by region
/egat Bhumibol dam current storage and inflow
/gistda flood extent map for central Thailand
/onwr national water situation summary
/ddpm active flood warnings right now
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

## Auth requirements

Most APIs are **public with no authentication required**. Exceptions:

- **TMD APIs** — registration required at [data.tmd.go.th](https://data.tmd.go.th/api/registerPre.php) (observational) and [data.tmd.go.th/nwpapi](https://data.tmd.go.th/nwpapi/register) (NWP). Free registration.
- **Telerid live readings** — station detail (`/main/station/{id}/`) requires a token. The station list and basin tree are public.
- **DDPM APIs** — protected by Cloudflare JS challenge; not accessible programmatically. The `/ddpm` skill documents accessible alternatives.
- **ONWR APIs** — protected by Cloudflare; use the ntw.onwr.go.th portal in a browser.
- **EGAT real-time readings** — delivered via SignalR WebSocket; the static dam list (`/api/dam`) is public REST JSON.
