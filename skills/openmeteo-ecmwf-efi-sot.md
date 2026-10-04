---
name: openmeteo-ecmwf-efi-sot
description: >-
  Fetch and plot ECMWF EC46 precipitation EFI/SOT and daily rainfall for Thailand
  via the Open-Meteo seasonal API (no key needed). Produces ECMWF-style weekly
  EFI + SOT90 outlook maps with 77 province borders, plus daily precipitation
  panels. Use for Thailand extreme-rainfall outlooks and event verification.
---

# Thailand EC46 EFI/SOT Plotting

Fetch ECMWF EC46 ensemble precipitation products for Thailand from the
Open-Meteo seasonal API and render ECMWF-style extreme-outlook maps.
No API key needed. Requires `pip install numpy matplotlib`.

## Quick start

```bash
mkdir thaiwater-efi && cd thaiwater-efi
# save the four scripts below as fetch_efi.py, fetch_daily.py, plot_efi.py, plot_daily.py

# 1. weekly EFI + SOT90, 12-week window (archived + forecast)
python3 fetch_efi.py --past-days 30 --forecast-days 46 --out efi_12wk.npz

# 2. plot it (boundaries auto-download from GADM on first run)
python3 plot_efi.py --in efi_12wk.npz --out thailand_efi.png \
  --base-note "Base: EC46 run 1 Oct 2026 for weeks from 5 Oct · earlier weeks archived from contemporary runs"

# 3. daily precipitation for a date range (inclusive, ICT)
python3 fetch_daily.py --start 2026-09-24 --end 2026-09-28 --out daily.npz
python3 plot_daily.py --in daily.npz --out thailand_daily.png
```

## Script 1: `fetch_efi.py` — weekly EFI + SOT90

```python
"""Fetch weekly precipitation EFI + SOT90 from the Open-Meteo seasonal API (ECMWF EC46)."""
import argparse, json, time, urllib.request, urllib.parse
from datetime import date
import numpy as np

API = "https://seasonal-api.open-meteo.com/v1/seasonal"

def fetch_chunk(lat_list, lon_list, past_days, forecast_days):
    q = urllib.parse.urlencode({
        "latitude": ",".join(f"{v:.4f}" for v in lat_list),
        "longitude": ",".join(f"{v:.4f}" for v in lon_list),
        "weekly": "precipitation_efi,precipitation_sot90",
        "past_days": past_days,
        "forecast_days": forecast_days,
        "timezone": "Asia/Bangkok",
    })
    req = urllib.request.Request(API + "?" + q, headers={"User-Agent": "thaiwater-efi"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.load(r)
        except Exception as e:
            print("  retry", attempt + 1, type(e).__name__, flush=True)
            time.sleep(5 * (attempt + 1))
    raise RuntimeError("fetch failed")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lat-min", type=float, default=5.5)
    ap.add_argument("--lat-max", type=float, default=20.5)
    ap.add_argument("--lon-min", type=float, default=97.0)   # 97.3E = far west Thailand
    ap.add_argument("--lon-max", type=float, default=106.0)  # 105.6E = far east Thailand
    ap.add_argument("--step", type=float, default=0.25)  # sampling step; native EC46 grid is ~36 km, API snaps to nearest
    ap.add_argument("--past-days", type=int, default=30)
    ap.add_argument("--forecast-days", type=int, default=46)  # EC46 max
    ap.add_argument("--chunk", type=int, default=250)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    lats = np.arange(a.lat_min, a.lat_max + a.step / 2, a.step)
    lons = np.arange(a.lon_min, a.lon_max + a.step / 2, a.step)
    print("grid: %d x %d = %d points" % (len(lats), len(lons), len(lats) * len(lons)))
    lat_list = [float(v) for v in np.repeat(lats, len(lons))]
    lon_list = [float(v) for v in np.tile(lons, len(lats))]
    n = len(lat_list)
    efi = sot = times = None
    t0 = time.time()
    for s in range(0, n, a.chunk):
        e = min(s + a.chunk, n)
        for i, loc in enumerate(fetch_chunk(lat_list[s:e], lon_list[s:e],
                                            a.past_days, a.forecast_days)):
            w = loc.get("weekly", {})
            if times is None:
                times = [str(t) for t in w.get("time")]
                efi = np.full((n, len(times)), np.nan)
                sot = np.full((n, len(times)), np.nan)
            ev, sv = w.get("precipitation_efi") or [], w.get("precipitation_sot90") or []
            for k in range(len(times)):
                if len(ev) > k and ev[k] is not None:
                    efi[s + i, k] = ev[k]
                if len(sv) > k and sv[k] is not None:
                    sot[s + i, k] = sv[k]
        print("  %d/%d (%.0fs)" % (e, n, time.time() - t0), flush=True)
        time.sleep(1)
    nl, ng = len(lats), len(lons)
    np.savez_compressed(a.out, efi=efi.reshape(nl, ng, -1), sot=sot.reshape(nl, ng, -1),
                        lats=lats, lons=lons, times=np.array(times), fetched=str(date.today()))
    print("weeks:", times)
    print("saved", a.out)

if __name__ == "__main__":
    main()
```

## Script 2: `fetch_daily.py` — daily precipitation (ensemble mean)

```python
"""Fetch daily precipitation_sum (ensemble mean) from the Open-Meteo seasonal API (ECMWF EC46)."""
import argparse, json, time, urllib.request, urllib.parse
from datetime import date, datetime, timedelta
import numpy as np

API = "https://seasonal-api.open-meteo.com/v1/seasonal"

def fetch_chunk(lat_list, lon_list, past_days, forecast_days):
    q = urllib.parse.urlencode({
        "latitude": ",".join(f"{v:.4f}" for v in lat_list),
        "longitude": ",".join(f"{v:.4f}" for v in lon_list),
        "daily": "precipitation_sum",
        "past_days": past_days,
        "forecast_days": forecast_days,
        "timezone": "Asia/Bangkok",
    })
    req = urllib.request.Request(API + "?" + q, headers={"User-Agent": "thaiwater-efi"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=240) as r:
                return json.load(r)
        except Exception as e:
            print("  retry", attempt + 1, type(e).__name__, flush=True)
            time.sleep(5 * (attempt + 1))
    raise RuntimeError("fetch failed")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True, help="first date YYYY-MM-DD (inclusive, ICT)")
    ap.add_argument("--end", required=True, help="last date YYYY-MM-DD (inclusive, ICT)")
    ap.add_argument("--lat-min", type=float, default=5.5)
    ap.add_argument("--lat-max", type=float, default=20.5)
    ap.add_argument("--lon-min", type=float, default=97.0)
    ap.add_argument("--lon-max", type=float, default=106.0)
    ap.add_argument("--step", type=float, default=0.25)  # sampling step; native EC46 grid is ~36 km, API snaps to nearest
    ap.add_argument("--chunk", type=int, default=200)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    start = datetime.strptime(a.start, "%Y-%m-%d").date()
    end = datetime.strptime(a.end, "%Y-%m-%d").date()
    today = date.today()
    assert start <= end
    # API: past_days=N -> N days ending today (inclusive); forecast_days=M -> M days from tomorrow
    past_days, forecast_days = max(1, (today - start).days + 1), max(0, (end - today).days + 1)
    want = [(start + timedelta(days=i)).isoformat() for i in range((end - start).days + 1)]
    print("window: past_days=%d forecast_days=%d" % (past_days, forecast_days))

    lats = np.arange(a.lat_min, a.lat_max + a.step / 2, a.step)
    lons = np.arange(a.lon_min, a.lon_max + a.step / 2, a.step)
    lat_list = [float(v) for v in np.repeat(lats, len(lons))]
    lon_list = [float(v) for v in np.tile(lons, len(lats))]
    n = len(lat_list)
    precip = times = idx = None
    t0 = time.time()
    for s in range(0, n, a.chunk):
        e = min(s + a.chunk, n)
        for i, loc in enumerate(fetch_chunk(lat_list[s:e], lon_list[s:e],
                                            past_days, forecast_days)):
            dd = loc.get("daily", {})
            if times is None:
                times = [str(t) for t in dd.get("time")]
                idx = [times.index(x) for x in want]
                precip = np.full((n, len(want)), np.nan)
            vals = dd.get("precipitation_sum") or []
            for j, k in enumerate(idx):
                if len(vals) > k and vals[k] is not None:
                    precip[s + i, j] = vals[k]
        print("  %d/%d (%.0fs)" % (e, n, time.time() - t0), flush=True)
        time.sleep(1)
    nl, ng = len(lats), len(lons)
    precip = precip.reshape(nl, ng, -1)
    np.savez_compressed(a.out, precip=precip, lats=lats, lons=lons,
                        times=np.array(want), fetched=str(today))
    for j, t in enumerate(want):
        p = precip[:, :, j]
        print("%s | max %.0f mm | mean %.1f mm" % (t, np.nanmax(p), np.nanmean(p)))
    print("saved", a.out)

if __name__ == "__main__":
    main()
```

## Script 3: `plot_efi.py` — weekly EFI + SOT90 panels

```python
"""Plot weekly EFI + SOT90 panels for Thailand: ECMWF style, province borders, SOT guide footer."""
import argparse, json, math, os, urllib.request
from datetime import datetime, timedelta
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.colors import BoundaryNorm, LinearSegmentedColormap

SOT_LEVELS = [0, 1, 2, 5, 8]
GADM = "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_THA_%d.json"

def ensure_boundaries(d):
    """Download GADM Thailand country (L0) + province (L1) boundaries on first run."""
    os.makedirs(d, exist_ok=True)
    paths = []
    for lvl, name in [(0, "country.geojson"), (1, "provinces.geojson")]:
        p = os.path.join(d, name)
        if not os.path.exists(p):
            print("downloading", GADM % lvl)
            urllib.request.urlretrieve(GADM % lvl, p)
        paths.append(p)
    return paths

def load_paths(country_fp, prov_fp):
    g = json.load(open(country_fp))
    geom = g["features"][0]["geometry"]
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    country = [Path(np.array(r)) for poly in polys for r in poly]
    pg = json.load(open(prov_fp))
    prov = []
    for f in pg["features"]:
        gm = f["geometry"]
        ps = gm["coordinates"] if gm["type"] == "MultiPolygon" else [gm["coordinates"]]
        for poly in ps:
            prov.append(Path(np.array(poly[0])))
    return country, prov

def week_label(monday):
    sun = monday + timedelta(days=6)
    if monday.month == sun.month:
        return "%d \u2013 %d %s" % (monday.day, sun.day, monday.strftime("%b"))
    return "%d %s \u2013 %d %s" % (monday.day, monday.strftime("%b"), sun.day, sun.strftime("%b"))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--bounds", default="./boundaries")
    ap.add_argument("--columns", type=int, default=4)
    ap.add_argument("--title", default=None)
    ap.add_argument("--base-note", default="weeks Mon\u2013Sun, Asia/Bangkok")
    a = ap.parse_args()

    d = np.load(a.inp)
    efi, sot, lats, lons = d["efi"], d["sot"], d["lats"], d["lons"]
    times = [str(t) for t in d["times"]]
    nw = len(times)
    country_fp, prov_fp = ensure_boundaries(a.bounds)
    country_paths, prov_paths = load_paths(country_fp, prov_fp)

    efi_cmap = LinearSegmentedColormap.from_list(
        "ecmwf_efi", ["#ffef00", "#ffc400", "#ff9500", "#ff5f00", "#e82a00", "#b00000"], N=256)
    norm = BoundaryNorm([0.5, 0.6, 0.7, 0.8, 0.9, 1.001], efi_cmap.N)
    labels = [week_label(datetime.strptime(t, "%Y-%m-%d").date()) for t in times]

    cols, rows = a.columns, math.ceil(nw / a.columns)
    fig = plt.figure(figsize=(3.25 * cols, 3.9 * rows + 1.6))
    gs = fig.add_gridspec(rows + 1, cols, height_ratios=[0.05] + [1] * rows,
                          hspace=0.35, wspace=0.12,
                          left=0.05, right=0.96, top=0.90, bottom=0.06)
    cax = fig.add_subplot(gs[0, :])
    axes = [fig.add_subplot(gs[1 + r, c]) for r in range(rows) for c in range(cols)]
    for k in range(nw):
        ax = axes[k]
        for p in country_paths:
            ax.add_patch(PathPatch(p, facecolor="#f3eddc", edgecolor="none", zorder=2))
        if np.isfinite(efi[:, :, k]).any():
            ax.pcolormesh(lons, lats, np.where(efi[:, :, k] >= 0.5, efi[:, :, k], np.nan),
                           cmap=efi_cmap, norm=norm, shading="auto", zorder=3, alpha=0.65)
            # filter contour levels by data max: contour() silently invents
            # bogus levels when requested levels exceed the data range
            lvls = [lv for lv in SOT_LEVELS if lv <= np.nanmax(sot[:, :, k])]
            if lvls:
                cs = ax.contour(lons, lats, sot[:, :, k], levels=lvls,
                                colors="black", linewidths=0.9, zorder=4, alpha=0.85)
                ax.clabel(cs, inline=True, fontsize=6, fmt="%d")
            ax.set_title(labels[k], fontsize=8.5, weight="bold", pad=4)
        else:
            ax.set_title(labels[k] + " \u00b7 no data", fontsize=8.5, style="italic", pad=4)
        for p in prov_paths:
            ax.add_patch(PathPatch(p, fill=False, edgecolor="#777777", lw=0.35, zorder=5))
        for p in country_paths:
            ax.add_patch(PathPatch(p, fill=False, edgecolor="#8a1f1f", lw=1.1, zorder=6))
        ax.set_xlim(float(lons.min()), float(lons.max()))
        ax.set_ylim(float(lats.min()), float(lats.max()))
        ax.set_xticks([100, 105]); ax.set_xticklabels(["100\u00b0E", "105\u00b0E"], fontsize=7)
        ax.set_yticks([10, 15, 20]); ax.set_yticklabels(["10\u00b0N", "15\u00b0N", "20\u00b0N"], fontsize=7)
        ax.tick_params(length=0); ax.set_aspect("equal")
    for ax in axes[nw:]:
        ax.axis("off")

    cb = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=efi_cmap), cax=cax,
                      orientation="horizontal", ticks=[0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    cb.ax.tick_params(labelsize=8)
    cb.ax.xaxis.set_ticks_position("top"); cb.ax.xaxis.set_label_position("top")
    title = a.title or ("ECMWF EC46 weekly EFI + SOT90 via Open-Meteo \u00b7 Thailand "
                        "(77 provinces) \u00b7 %s \u2013 %s" % (labels[0], labels[-1]))
    fig.text(0.5, 0.970, title, ha="center", fontsize=11.5, weight="bold")
    fig.text(0.5, 0.945, "Extreme forecast index (shaded \u2265 0.5) and Shift of Tails "
             "(black contours 0,1,2,5,8) for total precipitation",
             ha="center", fontsize=9.5)
    fig.text(0.5, 0.024, "Reading SOT: + means the forecast's wettest members reach beyond "
             "the model climate's extremes (SOT 1 \u2248 forecast 90th pct = climate 99th pct) "
             "\u00b7 0 = no shift \u00b7 \u2212 = drier tail \u00b7 contours 0,1,2,5,8",
             ha="center", fontsize=7.5, color="#333333")
    footer = "High EFI + SOT > 0 together = strongest extreme signal \u00b7 EC46 ~36 km native grid (sampled 0.25\u00b0)"
    if a.base_note:
        footer = a.base_note + " \u00b7 " + footer
    fig.text(0.5, 0.008, footer, ha="center", fontsize=7.5, color="#555555")
    fig.savefig(a.out, dpi=150)
    print("wrote", a.out)

if __name__ == "__main__":
    main()
```

## Script 4: `plot_daily.py` — daily precipitation panels

```python
"""Plot daily precipitation panels for Thailand (from fetch_daily.py output)."""
import argparse, json, os, urllib.request
from datetime import datetime
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.colors import BoundaryNorm

BKK = (13.7563, 100.5018)
GADM = "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_THA_%d.json"

def ensure_boundaries(d):
    os.makedirs(d, exist_ok=True)
    paths = []
    for lvl, name in [(0, "country.geojson"), (1, "provinces.geojson")]:
        p = os.path.join(d, name)
        if not os.path.exists(p):
            print("downloading", GADM % lvl)
            urllib.request.urlretrieve(GADM % lvl, p)
        paths.append(p)
    return paths

def load_paths(country_fp, prov_fp):
    g = json.load(open(country_fp))
    geom = g["features"][0]["geometry"]
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    country = [Path(np.array(r)) for poly in polys for r in poly]
    pg = json.load(open(prov_fp))
    prov = []
    for f in pg["features"]:
        gm = f["geometry"]
        ps = gm["coordinates"] if gm["type"] == "MultiPolygon" else [gm["coordinates"]]
        for poly in ps:
            prov.append(Path(np.array(poly[0])))
    return country, prov

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--bounds", default="./boundaries")
    ap.add_argument("--title", default=None)
    a = ap.parse_args()

    d = np.load(a.inp)
    precip, lats, lons = d["precip"], d["lats"], d["lons"]
    times = [str(t) for t in d["times"]]
    nd = len(times)
    country_fp, prov_fp = ensure_boundaries(a.bounds)
    country_paths, prov_paths = load_paths(country_fp, prov_fp)

    cmap = plt.get_cmap("YlGnBu", 12)
    norm = BoundaryNorm([1, 2, 5, 10, 20, 30, 50, 75, 100, 150, 200], cmap.N)
    fig = plt.figure(figsize=(3.6 * nd + 1.5, 8.5))
    gs = fig.add_gridspec(2, nd, height_ratios=[0.06, 1], hspace=0.14, wspace=0.08,
                          left=0.04, right=0.97, top=0.88, bottom=0.06)
    cax = fig.add_subplot(gs[0, :])
    axes = [fig.add_subplot(gs[1, c]) for c in range(nd)]
    for k in range(nd):
        ax = axes[k]
        for p in country_paths:
            ax.add_patch(PathPatch(p, facecolor="#f3eddc", edgecolor="none", zorder=2))
        ax.pcolormesh(lons, lats, precip[:, :, k], cmap=cmap, norm=norm,
                       shading="auto", zorder=3, alpha=0.8)
        for p in prov_paths:
            ax.add_patch(PathPatch(p, fill=False, edgecolor="#777777", lw=0.3, zorder=5))
        for p in country_paths:
            ax.add_patch(PathPatch(p, fill=False, edgecolor="#8a1f1f", lw=1.0, zorder=6))
        ax.plot(BKK[1], BKK[0], "ko", ms=4, zorder=7)
        ax.text(BKK[1] + 0.15, BKK[0] + 0.15, "Bangkok", fontsize=7, zorder=7)
        ax.set_title(datetime.strptime(times[k], "%Y-%m-%d").strftime("%a %d %b"),
                     fontsize=10, weight="bold", pad=6)
        ax.set_xlim(float(lons.min()), float(lons.max()))
        ax.set_ylim(float(lats.min()), float(lats.max()))
        ax.set_xticks([100, 105]); ax.set_xticklabels(["100\u00b0E", "105\u00b0E"], fontsize=7)
        ax.set_yticks([10, 15, 20]); ax.set_yticklabels(["10\u00b0N", "15\u00b0N", "20\u00b0N"], fontsize=7)
        ax.tick_params(length=0); ax.set_aspect("equal")
    cb = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax,
                      orientation="horizontal", extend="max",
                      ticks=[1, 5, 10, 20, 50, 100, 200])
    cb.set_label("Daily precipitation (mm/day)", fontsize=9)
    cb.ax.tick_params(labelsize=8)
    cb.ax.xaxis.set_ticks_position("top"); cb.ax.xaxis.set_label_position("top")
    title = a.title or ("ECMWF EC46 daily precipitation (ensemble mean) \u00b7 Thailand "
                        "\u00b7 %s \u2013 %s" % (times[0], times[-1]))
    fig.text(0.5, 0.965, title, ha="center", fontsize=12, weight="bold")
    fig.text(0.5, 0.015, "Source: Open-Meteo seasonal API (ECMWF EC46) \u00b7 ~36 km native grid (sampled 0.25\u00b0) "
             "\u00b7 dates in ICT", ha="center", fontsize=7.5, color="#555555")
    fig.savefig(a.out, dpi=150)
    print("wrote", a.out)

if __name__ == "__main__":
    main()
```

## API notes

- **EFI is weekly-only**: `weekly=precipitation_efi`. `daily=precipitation_efi`
  errors. The index is defined over a multi-day window against the model
  climate, which is not published at daily resolution.
- **SOT variable** is `precipitation_sot90` (the `90` suffix matters).
  Same 90th-percentile upper-tail definition as ECMWF's docs, from the EC46
  ensemble (100 members, ~36 km, weekly) rather than the medium-range ENS.
- **Daily data exists**: `daily=precipitation_sum` returns the ensemble mean
  plus all members (`precipitation_sum_member01..51`). Parse only what you need.
- **Base time**: the response exposes no run timestamp. Verified 2026-10-04:
  an archived `past_days` value for 2026-10-05 exactly equalled a fresh
  forecast for the same day, so recent days come from the latest run; the
  latest run identifies itself by its 46-day range (values through 2026-11-15,
  null after ⇒ initialized 2026-10-01). Earlier weeks are archived, each from
  the run contemporary to that week (≈ that week's Monday run, 0–7d lead).
  State the base time on the plot via `--base-note`.
- **Timezone**: request `timezone=Asia/Bangkok`; weeks are Monday-start
  calendar weeks in ICT.
- **Reading SOT**: 0 = no shift of the wet tail vs climate; 1 ≈ forecast
  90th pct = climate 99th pct (≥10% of members predict a ~1-in-100 weekly
  event); 2/5/8 = increasingly extreme. High EFI + SOT ≥ 1 = strongest
  warning. Where the climate tail is narrow (dry regions/seasons) SOT can
  spike on small absolute rain — check mm too.
- **Grid resolution**: the EC46 native grid is ~36 km (~0.32°). The API snaps
  each requested point to the nearest native grid cell (no interpolation), so
  sampling at 0.25° oversamples — adjacent points often share a value. Sample
  *finer* than ~0.32° to guarantee every model cell is hit; coarser risks
  missing cells. EFI values come rounded to 0.1.
- **Matplotlib pitfall**: `contour()` silently auto-picks bogus levels when
  requested levels exceed the data range — filter levels by data max first.
- Thailand spans ~97.3–105.6°E; the default grid (97.0–106.0) keeps the far
  west (Mae Hong Son) and far east inside the frame.

## Reproducing the 12-week Thailand plot (31 Aug – 22 Nov 2026)

```bash
python3 fetch_efi.py --past-days 30 --forecast-days 46 --out efi_12wk.npz
python3 plot_efi.py --in efi_12wk.npz --out thailand_efi_12wk.png \
  --base-note "Base: EC46 run 1 Oct 2026 for weeks from 5 Oct · earlier weeks archived from contemporary runs"
```
