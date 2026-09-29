---
name: water_situation_check
description: Run a full daily water-situation check the way Thai water analysts do it — rain 24h + 3-day accumulation, rain forecast, over-bank water levels, 3–7 day level outlook, dam storage in seasonal context, and tide for Bangkok. Cross-skill routine (thaiwater / ews / wmsc_rid / egat / rid_forecast / navy_tide).
---

Run the standard 6-step "is this flood situation getting worse, holding, or milder?" check.

The user asked: $ARGUMENTS

The routine below mirrors what Thai water researchers publish for the public (adapted from a 25 Sep 2026 post by อ.น้อย / thaiwater.net, which walked citizens through exactly these six checks). Do the steps in order and report findings step by step — do not jump to a conclusion after one dataset.

## How to respond

1. State the analysis window (today's date + latest data timestamp) up front.
2. Walk steps 1→6, presenting the numbers you actually fetched. If a source is unavailable, say so and name the substitute.
3. Close with the verdict the data supports: **หนักขึ้น / ทรง ๆ / เบาลง**, plus the watch list of provinces/stations, and state explicitly what is still unknown (field water, harvest status, local drainage works).
4. Never present a single data point (e.g. one heavy rain day) as a flood forecast; the method is always *past accumulation* + *forecast continuation* + *river/dam/tide context*.

---

## Step 1 — Rain in the last 24 h (where did it actually fall?)

```bash
# Station-level daily rainfall (latest day)
curl -sL "https://api-v3.thaiwater.net/api/v1/thaiwater30/public/rain_yesterday" -H "Accept: application/json"
# Rolling 24 h
curl -sL "https://api-v3.thaiwater.net/api/v1/thaiwater30/public/rain_24h" -H "Accept: application/json"
```

Sort descending by `rainfall_value` (mm) and group by province. Heavy totals here = candidate areas for fast runoff in the next 12–24 h.

Site equivalent for a human: https://www.thaiwater.net/weather/rainfall

## Step 2 — 3-day accumulation + 3-day forecast (flash flood & landslide window)

```bash
# 3-day accumulated rainfall per station (ฝนสะสม 3 วันย้อนหลัง)
curl -sL "https://api-v3.thaiwater.net/api/v1/thaiwater30/provinces/rain3d" -H "Accept: application/json"
# If the national aggregate is empty, use rain3d_graph for a station in the area
# being assessed. Replace STATION_ID with its station.id and use the last three
# complete calendar dates (not the current, potentially incomplete day).
curl -sL "https://api-v3.thaiwater.net/api/v1/thaiwater30/provinces/rain3d_graph?station_id=STATION_ID&start_date=YYYY-MM-DD&end_date=YYYY-MM-DD" -H "Accept: application/json"

# Flash-flood risk for the next 24 / 48 h (HII, tambon level with FFPI)
curl -sL "https://api.hii.or.th/v2/4UQaYnf0Bx4fXPYyCdDRbqHyXH9Ixvd2nVUjaN1cLBY=/warning/flashflood-24h" -H "User-Agent: Mozilla/5.0"
curl -sL "https://fews2.hii.or.th/model-output/data_portal/flashflood/flashflood_report.txt"

# DWR early-warning stations (the /ews skill) for the same window
```

Reasoning rule: **past 3 days alone is not enough** — if the past 3 days were wet *and* the next 3 days keep raining, the landslide/flash-flood odds climb sharply, especially in foothill provinces. If the wet spell has ended, the risk decays.

Site equivalent: https://www.thaiwater.net/risk-rainfall-3-day-forecast

## Step 3 — Who is already over-bank (ล้นตลิ่ง)?

The RID SVG river-viewer used by analysts (`hyd-app-db.rid.go.th`) does not respond from this VM — use the API instead:

```bash
curl -sL "https://api-v3.thaiwater.net/api/v1/thaiwater30/public/waterlevel_load" -H "Accept: application/json" \
  | python3 -c "
import sys,json
rows=json.load(sys.stdin)['waterlevel_data']['data']
over=[r for r in rows if (r.get('diff_wl_bank_text') or '').startswith('ล้นตลิ่ง')]
for r in sorted(over,key=lambda r:-float(r['diff_wl_bank'] or 0)):
    g=r.get('geocode') or {}
    print(round(float(r['diff_wl_bank']),2),'m |',g.get('province_name',{}).get('th'),'|',
          r['station']['tele_station_name']['th'],'| lvl',r.get('situation_level'))
print('total over-bank:',len(over))
"
```

`situation_level`: 1 normal → 2 watch → 3 warning → 4 critical → 5 over-bank. Use `diff_wl_bank_text` as the direct indicator: on 2026-09-29, 83 of 804 stations were marked over-bank, but six had no `situation_level`. A missing level does not mean the station is below bank. `diff_wl_bank` is a magnitude; read it with the text to determine whether the station is above or below bank.

Site equivalent: https://www.thaiwater.net/water/wl

## Step 4 — Outlook: where are levels heading in 3–7 days?

- RID station forecast charts (image, no API): `http://water.rid.go.th/itcwater/utok/{CODE}.html` → `F-{CODE}.jpg` (see the `rid_forecast` skill; check `Last-Modified` — W.1C / W.3A / M.182 are stale since Nov 2025).
- Reservoir-region forecasts / releases: `wmsc_rid` (Telerid, reservoir app) and `egat` (dam inflow/outflow).
- Chao Phraya specifically: read **C.2 Nakhon Sawan** (inflow) together with **C.13 Chao Phraya Dam** (release at Chai Nat) — a level at one station alone does not tell you the trend downstream.

If nothing is over-bank yet, this step is where the "will it get there?" answer comes from.

## Step 5 — Dam storage in seasonal context

```bash
# Large dams, hourly + daily (dam_size: 1=large, 2=medium, 3=small telemetry — INT, not a string)
curl -sL "https://api-v3.thaiwater.net/api/v1/thaiwater30/analyst/dam?dam_size=1" -H "Accept: application/json"
```

Do not react to the storage percentage alone. Ask:

1. Is the reservoir still in its normal **inflow season** (for most Thai dams the peak inflow window is Aug–Oct)? If storage is low but the season has not ended, low storage is not yet a drought signal.
2. Compare inflow with the same date in previous years and check current official operating notices. Do not infer or recommend releases from storage and inflow alone.
3. Any release decision is (and must be) taken together with downstream river level and the rain outlook — never quote a release as "flooding caused by the dam".

Site equivalent: https://www.thaiwater.net/water/dam/large

## Step 6 — Bangkok & the 3 Samut provinces: tide + pumps

```bash
# Gulf tide table (max/min + 4-hourly)
curl -sL "https://fews2.hii.or.th/model-output/data_portal/tide_table/summary.txt"
# Bangkok canals / rain stations / polder status
curl -sL "https://flood.bangkok.go.th/api/polder/all" -H "User-Agent: Mozilla/5.0"   # see the dds_bangkok skill for the rest
```

⚠️ Verified 2026-09-25/26: `flood.bangkok.go.th`, `dds.bangkok.go.th` and `weather.bangkok.go.th` all fail TLS from some networks (connect error, no response) — if the Bangkok step cannot be fetched, say so explicitly instead of reporting "no flooding in Bangkok", and fall back to the tide table + news reports for the city.

High tide coinciding with heavy in-city rain = drainage slows, standing water lasts longer even with moderate rainfall. Note that Bangkok is *not* affected by upper-Chao-Phraya releases; its flooding is in-city rain + drainage capacity. The Navy Hydrographic Department dashboard can only be used in a browser (`navy_tide` skill).

Site equivalent: https://www.thaiwater.net/ (city view) + https://flood.bangkok.go.th

---

## What this method cannot see (state it in the verdict)

- **Water in the fields (น้ำในทุ่ง)** — flooded or harvested paddy absorbs or passes on water; agency summaries carry this, the APIs above do not.
- **Local drainage/pump operations** and canal gate decisions made in the last hours.
- **Officially announced warning zones** (DDPM/จังหวัด) — check the `ddpm` skill for the current announcements.
- Thailand has no operational Decision Support System that fuses these automatically; this routine is a manual approximation, and the final call always belongs to the responsible agency plus local experience.

---

## Cross-references

- `thaiwater` — the API behind steps 1, 2, 3, 5
- `ews` — DWR flash-flood / landslide warning stations
- `wmsc_rid`, `rid_forecast` — RID telemetry, reservoir app, forecast charts
- `egat` — EGAT dam storage/inflow/outflow
- `navy_tide` — tide sources (scriptable + browser-only)
- `dds_bangkok`, `ddpm`, `gistda`, `onwr`, `tmd` — city drainage, official warnings, satellite flood extent, national portal, weather/NWP
