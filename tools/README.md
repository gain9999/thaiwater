# tools/ — how to run the helpers

Everything here is plain Python 3, key-free by default, and resolves its paths from the
repository root, so a fresh clone works:

```bash
git clone https://github.com/gain9999/thaiwater.git && cd thaiwater
python3 -m pip install -r requirements.txt   # Pillow, numpy, matplotlib, playwright
```

Conventions:

- Inputs default to `data/` (chart sources in `data/raw/`), outputs go to `out/` — both
  relative to the repo root, overridable with the flags shown below.
- `out/` is scratch (crops, logs, plots) and is gitignored.
- Two environment variables are needed only by the optional parts:
  - `FLOODHUB_API_KEY` — Google Flood Forecasting API key (the `floodhub_*` tools; falls back to `~/.floodhub-api-key`). An ADC/service-account token is not interchangeable; API keys also never work on Cloud Storage.
  - `VISION_SCRIPT` — your own image-to-text helper, called as `python VISION_SCRIPT IMAGE "question"` (the `c2_crops*.py` / `c2_tiles.py` chart readers).

| file | what it does | inputs → outputs |
|---|---|---|
| `fetch_nodes.py` | Build the merged river-node inventory (waterlevel_load + watergate basins + the two chart pages) | public API → `data/station_nodes.csv`, `data/station_nodes.json`, `data/node_summary.json`, raw caches in `data/` |
| `station_chain.py` | Reconstruct the station topology: chain order per river + co-located cross-agency pairs | `data/waterlevel_load.json` (or argv[1]) → stdout |
| `event_lag.py` | Measured water travel time between adjacent main-stem stations (rise-rate timing) | `data/series_raw.json` / API → `data/event_lag_<date>.csv|json` |
| `q_lag.py` | Travel time from **discharge** (gate-step routing) — the method that works with RID releases | API/cache → stdout |
| `lag_correlation.py` | Travel-time lag between an upstream/downstream pair by correlation | API/cache → stdout |
| `travel_time.py` | Extract the brief chart's printed travel-time labels, and check node coverage | SVG → stdout |
| `svgnet.py` | Cross-check the thaiwater-derived chain against the official chart SVG | `data/raw/*` → stdout (+ builds `data/raw/svg_paths.json`) |
| `analyze_svg.py` | Snap SVG station attach-points onto the drawn river, print the chart's own order | `data/raw/{cp.svg,svg_leaders.json}` → stdout |
| `compare_snapshot.py` | Diff two `waterlevel_load` snapshots (level m MSL + discharge deltas) | two JSON snapshots → stdout |
| `chain_trend.py` | Main-stem Chao Phraya level/discharge trend for the last N hours (+ PNG) | public API → `data/chain_trend.json`, `out/chain_trend.png` |
| `forecast_plot.py` | C.2 observed-vs-forecast plot (the forecast half drawn as a marked zone) | `data/chain_trend.json` → `out/c2_observed_vs_forecast.png` |
| `c2_history.py` | C.2 06:00 level/discharge for the last N days | public API → stdout |
| `c2_labels.py` / `c2_layout.py` | Locate the printed value labels on the F-C2 chart by pixel density / gridline mapping | `out/F-C2.jpg` → stdout |
| `c2_crops.py` / `c2_crops2.py` / `c2_tiles.py` | Crop or tile F-C2 and ask a vision model to transcribe the labels | `out/F-C2.jpg` + `VISION_SCRIPT` → `out/*.png` + transcription |
| `crop_zoom.py` | Crop + upscale a region of any image | image → PNG |
| `clip_svg.py` / `clip_png.py` | Screenshot a region of the SVG / raster chart with headless Chromium | `data/raw/cp.svg` → PNG |
| `mk_stations.py` | Which Mae Klong stations actually publish discharge / level | public API → stdout |
| `mk_lag.py` … `mk_lag4.py` | Mae Klong travel-time checks along the RID Ratchaburi chart chain (dam → K.55A → K.56 → K.2B → K.57) | `data/mk_cache.json` → stdout |
| `floodhub_c13.py` | Google Flood Hub over the Chao Phraya corridor (C.2 → C.13 → Ayutthaya): status, thresholds, 7-day discharge | Flood Hub API → `out/floodhub/*.json` |
| `floodhub_summary.py` | Summarise that JSON: corridor gauges, severities, nearest reaches to C.2/C.13 | `out/floodhub/c13_floodhub.json` → stdout |
| `floodhub_basin.py` | Basin gauges flagged SEVERE/EXTREME with peak values | same JSON → stdout |
| `floodhub_probe.py` | Flood Hub reachability / API-key check | Flood Hub API → stdout |

Data files that are **derived and large** are not committed — the first run of a tool builds
what it needs: `svg_paths.json` comes from `data/raw/cp.svg` automatically, `waterlevel_load.json`
from `tools/fetch_nodes.py`, and `out/floodhub/*.json` from `tools/floodhub_c13.py`.

The corresponding reference documentation lives in `../skills/` (one markdown file per source:
`thaiwater.md`, `rid_forecast.md`, `google-flood-hub.md`, `station_network.md`, `weathernext3.md`, …).
