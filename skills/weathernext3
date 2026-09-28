---
name: weathernext3
description: >-
  Retrieves, processes, and visualizes WeatherNext 3 global atmospheric forecasts from GCS Zarr stores. Supports both 15-day (360h) synoptic runs and 48-hour interim hourly runs. Handles 0.1-degree spatial cropping (default: Thailand), discrete 1-hour step precipitation accumulations, percentiles (mean, p50, p90), spatial ensemble spread, and regional multi-member plume generation. Use when downloading WeatherNext 3 data, analyzing WeatherNext forecast runs, plotting precipitation plume charts, or creating spatial risk maps.
---

# WeatherNext 3 Data Processing & Forecast Analysis Skill

This skill provides end-to-end workflows for retrieving, reading, analyzing, and plotting WeatherNext 3 forecast runs from Google Cloud Storage Zarr stores.

---

## 1. Storage Architecture & Bucket Layout

WeatherNext 3 produces high-resolution AI numerical weather predictions globally on a 0.1° grid:

### 1. Bucket Paths
* **Statistics Store (Requester Pays OFF)**:
  `gs://weathernext3_statistics_spatial/weathernext_3_0_0_statistics/zarr/`
  * Contains ensemble summary statistics: `mean`, `p10`, `p50`, `p90`, `spread`.
  * Access requires standard Google Cloud authentication / Application Default Credentials (`gcloud auth application-default login`).
* **Full Ensemble Store (Requester Pays ON)**:
  `gs://weathernext3_spatial/`
  * Contains full 64-member trajectories and 3D pressure levels (`geopotential`, `temperature`, `u_component_of_wind`, etc.).
  * Requires a GCP project billing configuration (`user_project`).

### 2. Forecast Run Cycles & Horizons
* **Synoptic Runs (4× Daily)**: `00`, `06`, `12`, `18` UTC.
  * **Horizon**: **15 Days (360 hours)**.
  * **Path Structure**: `YYYY_to_present/YYYYMMDD_HHhr_01_preds/predictions.zarr`
  * **Dissemination Delay**: ~7 hours 45 minutes after initialization (e.g. `06 UTC` publishes at ~`13:45 UTC`, `12 UTC` at ~`19:45 UTC`).
* **Interim Hourly Runs (20× Daily)**: `01-05`, `07-11`, `13-17`, `19-23` UTC.
  * **Horizon**: **48 Hours** for surface variables.
  * Used for ultra-fresh near-term monitoring. For forecasts exceeding 48h (e.g. 5-day / 120h), fall back to the latest synoptic run.

---

## 2. Grid Coordinates & Variable Conventions

### Spatial Resolution
* **Latitude**: `lat_0p1` ranging from `-90.0°` to `+90.0°` (Ascending!).
* **Longitude**: `lon_0p1` ranging from `0.0°` to `360.0°`.
* **Lead Time**: `lead_time` dimension in hours (`0` to `360`).

### Thailand Regional Default Bounds
* **Latitude**: `slice(5.0, 21.0)`
* **Longitude**: `slice(97.0, 106.0)`

### Key Precipitation Variables
* `total_precipitation_1hr_mean`: Ensemble mean hourly accumulation.
* `total_precipitation_1hr_p50`: Median (50th percentile) hourly accumulation.
* `total_precipitation_1hr_p90`: High-impact 90th percentile hourly accumulation.
* **Unit Conversion**: Raw values in the Zarr store are in **meters (`m`)** per 1-hour step. **Multiply by 1000** to convert to **millimeters (`mm`)**.

---

## 3. Environment & Python Setup

Reading WeatherNext 3 Zarr v3 stores requires `obstore`, `zarr` (v3+), `xarray`, and `dask`:

```bash
pip install "zarr>=3.0.0" obstore xarray dask matplotlib cartopy pandas numpy
```

---

## 4. Standard Python Reading Recipe

```python
import dask
import matplotlib.pyplot as plt
import numpy as np
import obstore as obs
import pandas as pd
import xarray as xr


def open_weathernext_zarr(init_date_str="20260924", init_hour="06"):
  """Opens WeatherNext 3 Zarr store directly from GCS using obstore."""
  prefix = f"weathernext_3_0_0_statistics/zarr/2026_to_present/{init_date_str}_{init_hour}hr_01_preds/predictions.zarr"

  # Configure GCS Store with Application Default Credentials
  store = obs.store.GCSStore(
      bucket="weathernext3_statistics_spatial",
      prefix=prefix,
  )

  # xarray.open_zarr requires dask to handle chunk indexing
  ds = xr.open_zarr(store, consolidated=True)
  return ds


def extract_thailand_precip(ds):
  """Subsets Thailand domain and extracts hourly precipitation statistics."""
  # Slice Thailand bounds (lat: 5.0 to 21.0, lon: 97.0 to 106.0)
  ds_th = ds.sel(
      lat_0p1=slice(5.0, 21.0),
      lon_0p1=slice(97.0, 106.0),
  )

  # Extract variables and convert meters to millimeters (x 1000)
  p_mean = ds_th["total_precipitation_1hr_mean"] * 1000.0
  p_p50 = ds_th["total_precipitation_1hr_p50"] * 1000.0
  p_p90 = ds_th["total_precipitation_1hr_p90"] * 1000.0

  return p_mean, p_p50, p_p90
```

---

## 5. Computing Calendar-Day Discrete Accumulations (ICT Timezone)

Because WeatherNext 3 variables are discrete **1-hour step accumulations**, calculating daily totals requires:
1. Constructing target timestamps: `init_utc + pd.to_timedelta(lead_time, unit='h')`.
2. Converting timestamps to Bangkok Local Time (`ICT`, `UTC+7`).
3. Grouping or masking slices by the local calendar day (e.g. `2026-09-25 00:00 ICT` to `2026-09-25 23:59 ICT`).
4. Summing the 1-hour step values across the 24 hours of each target day.

```python
def compute_ict_daily_totals(p_1hr_da, init_dt_utc, num_days=5):
  """Sums 1-hour precipitation into discrete 24-hour calendar days in ICT (UTC+7)."""
  leads = p_1hr_da["lead_time"].values
  utc_times = [init_dt_utc + pd.Timedelta(hours=int(h)) for h in leads]
  ict_times = [t.tz_localize("UTC").tz_convert("Asia/Bangkok") for t in utc_times]

  daily_accumulations = {}
  unique_dates = sorted(list(set([t.date() for t in ict_times])))[:num_days]

  for d in unique_dates:
    # Find indices belonging to this ICT calendar date
    indices = [i for i, t in enumerate(ict_times) if t.date() == d]
    if indices:
      day_slice = p_1hr_da.isel(lead_time=indices)
      daily_accumulations[str(d)] = day_slice.sum(dim="lead_time")

  return daily_accumulations
```

---

## 6. Visualization & Plotting Patterns

* **Cartopy Spatial Extent**:
  ```python
  import cartopy.crs as ccrs
  import cartopy.feature as cfeature

  fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})
  ax.set_extent([97.0, 106.0, 5.0, 21.0], crs=ccrs.PlateCarree())
  ax.add_feature(cfeature.COASTLINE, linewidth=0.8)
  ax.add_feature(cfeature.BORDERS, linewidth=1.0)
```
* **Ensemble Plume Charts (3×3 Province Subplots)**:
  * Extract provincial coordinates using `.sel(lat_0p1=lat, lon_0p1=lon, method='nearest')`.
  * Plot `p50` (median) as a solid curve.
  * Plot `p10` to `p90` as a semi-transparent shaded envelope (`fill_between`).
  * Display all times on the x-axis in **Bangkok Datetime (ICT)**.

---

## 7. Best Practices & Rules
* **Explicit Time Range**: Always declare the target forecast dates and initialization cycle in ICT at the beginning of any report.
* **Synoptic vs. Interim Selection**: Always use Synoptic runs (00/06/12/18 UTC) for medium-range forecasts (up to 15 days), and reserve Interim runs for immediate 48-hour event tracking.
