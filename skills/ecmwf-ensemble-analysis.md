---
name: ecmwf-ensemble-analysis
description: >-
  Retrieves ECMWF ensemble forecasts (50 members), processes GRIB2 precipitation and atmospheric data, computes discrete 24-hour daily accumulations, multi-threshold exceedance probabilities (>20mm, >50mm, >100mm), percentile quantiles (Q50, Q90, ensemble maximum), and exploratory spatial rainfall diagnostics. These are not ECMWF EFI/SOT, which require model climatology. Use when asked to download ECMWF ensemble data, plot extreme weather probability maps, generate 14-day forecast dashboards, or perform ensemble meteorological risk analysis. Don't use for raw satellite imagery or non-ECMWF GFS data.
---

# ECMWF Ensemble Data Processing & Risk Analysis

This skill provides end-to-end workflows for retrieving, processing, analyzing, and visualizing 50-member ensemble weather forecasts from ECMWF Open Data (`ecmwf-opendata`) and ECMWF Web API (`ecmwf-api-client`).

---

## Default Geographical Region & Boundaries: Thailand

Unless specified otherwise, all scripts and maps use **Thailand** as the default geographical domain.

### 1. Default Bounding Box (Thailand)
* **Latitude Range**: `5.0°N` to `21.0°N` *(Note: ECMWF datasets index latitude descendingly `slice(21.0, 5.0)`)*
* **Longitude Range**: `97.0°E` to `106.0°E` (`slice(97.0, 106.0)`)
* **Cartopy Spatial Extent**: `ax.set_extent([97.0, 106.0, 5.0, 21.0], crs=ccrs.PlateCarree())`

```python
# Crop dataset to default Thailand extent
thailand_ds = ds.sel(latitude=slice(21.0, 5.0), longitude=slice(97.0, 106.0))
```

### 2. Default Administrative & Province Boundaries
To render national borders and Thailand province lines:

```python
import cartopy.feature as cfeature

# Load 10m scale Natural Earth Province / State lines
provinces = cfeature.NaturalEarthFeature(
    category='cultural',
    name='admin_1_states_provinces_lines',
    scale='10m',
    facecolor='none'
)

# Apply boundary layers to Cartopy map axis
ax.add_feature(cfeature.LAND, facecolor='#f8f9fa', zorder=1)
ax.add_feature(cfeature.OCEAN, facecolor='#e3f2fd', zorder=1)
ax.add_feature(cfeature.COASTLINE, linewidth=1.0, edgecolor='#212121', zorder=4)
ax.add_feature(cfeature.BORDERS, linewidth=1.2, linestyle='-', edgecolor='#212121', zorder=5)
ax.add_feature(provinces, linewidth=0.5, linestyle=':', edgecolor='#666666', zorder=6)
```

---

## Quick Start

### 1. Python Environment Requirements
Ensure the required libraries are installed in your Python environment:
```bash
pip install ecmwf-opendata ecmwf-api-client xarray cfgrib eccodes eccodeslib matplotlib cartopy pandas numpy
```

---

## ECMWF Account & API Credentials Setup

### 1. Registration & Signing Up
To access ECMWF services and API clients:
1. Go to the ECMWF portal: [https://identity.ecmwf.int/](https://identity.ecmwf.int/) or [https://apps.ecmwf.int/registration/](https://apps.ecmwf.int/registration/)
2. Create a free ECMWF user account.

### 2. Obtaining Your API Key
1. Log in to your ECMWF account.
2. Navigate to your ECMWF API Key page: [https://api.ecmwf.int/v1/key/](https://api.ecmwf.int/v1/key/)
3. Copy your **API Key**, **Email Address**, and **API URL**.

### 3. Configuring `~/.ecmwfapirc`
Save your credentials to a file named `.ecmwfapirc` in your home directory (`~/.ecmwfapirc`):

```json
{
    "url"   : "https://api.ecmwf.int/v1",
    "key"   : "<YOUR_ECMWF_API_KEY>",
    "email" : "<YOUR_REGISTERED_EMAIL>"
}
```

```bash
# Restrict access and verify the configuration file is readable without printing its secrets
chmod 600 ~/.ecmwfapirc
test -r ~/.ecmwfapirc && echo "ECMWF credentials configured"
```

* **Note**: `ecmwf.opendata.Client()` retrieves public open data feeds (`data.ecmwf.int`). Configuring `~/.ecmwfapirc` is required when using `ecmwf-api-client` (`from ecmwfapi import ECMWFDataServer`) to query Web API or MARS archived datasets.

---

## Data Retrieval & Discrete Daily Differencing

### 1. Free Open Data vs. MARS Subscription
* **Free Open Data (`ecmwf.opendata`)**: Accesses public ECMWF forecasts (`data.ecmwf.int`). Provides 50 perturbed ensemble members (`stream="enfo"`, `type="pf"`) for lead times up to **360 hours (15 days)**.
* **MARS Subscription (`ecmwf-api-client`)**: Pre-computed Extreme Forecast Index (`type="ef"`) and Shift of Tail (`type="es"`) require a MARS subscription account.
* **Solution**: You can derive ensemble exceedance probabilities and percentiles directly from the 50 free perturbed members. True ECMWF EFI/SOT require model-climate references and cannot be calculated from a single forecast ensemble alone.

### 2. Downloading Multi-Day Ensemble Data
ECMWF total precipitation (`param="tp"`) is accumulated from forecast time $T=0$. To analyze a multi-day window (e.g. 14 days), download the full set of 24h daily steps:

```python
from ecmwf.opendata import Client

client = Client(source="ecmwf")
steps_14 = [24, 48, 72, 96, 120, 144, 168, 192, 216, 240, 264, 288, 312, 336]

client.retrieve(
    stream="enfo",
    type="pf",
    param="tp",
    step=steps_14,
    target="/tmp/multistep_enfo_tp.grib2"
)
```

### 3. Discrete 24-Hour Daily Differencing Logic
To evaluate true 24-hour daily rainfall without cumulative masking:
$$\Delta P_k = \max\Big( P(t_k) - P(t_{k-1}), \; 0 \Big) \quad \text{for Day } k$$

```python
import xarray as xr
import numpy as np

ds = xr.open_dataset("/tmp/multistep_enfo_tp.grib2", engine="cfgrib")
# Crop to default Thailand extent
thailand_ds = ds.sel(latitude=slice(21.0, 5.0), longitude=slice(97.0, 106.0))
tp_mm = thailand_ds["tp"] * 1000.0  # Convert meters to mm

daily_tp = {}
daily_tp[1] = tp_mm.sel(step=np.timedelta64(24, 'h'))

for day in range(2, 15):
    s_curr = steps_14[day - 1]
    s_prev = steps_14[day - 2]
    tp_curr = tp_mm.sel(step=np.timedelta64(s_curr, 'h'))
    tp_prev = tp_mm.sel(step=np.timedelta64(s_prev, 'h'))
    daily_tp[day] = (tp_curr - tp_prev).clip(min=0.0)
```

---

## Probabilistic Calculations & Metrics

### 1. Empirical Exceedance Probability (Relative Frequency)
For a specific threshold (e.g., >20mm, >50mm, >100mm), calculate the proportion of the 50 ensemble members exceeding it:

$$\text{Prob}_{>\text{thresh}}(x, y) = \left( \frac{1}{50} \sum_{i=1}^{50} \mathbb{I}(\Delta P_i(x, y) > \text{thresh}) \right) \times 100\%$$

```python
# Probability of >50mm rain in 24h
prob_50mm = (daily_tp[day] > 50.0).mean(dim="number") * 100.0

# Probability of >100mm rain in 24h (Extreme Deluge / Flood Risk)
prob_100mm = (daily_tp[day] > 100.0).mean(dim="number") * 100.0
```

### 2. Physical Quantiles & Worst-Case Scenario
```python
q50_median = daily_tp[day].quantile(0.50, dim="number")  # Most likely baseline (mm)
q90_extreme = daily_tp[day].quantile(0.90, dim="number") # Severe 90th percentile (mm)
q100_max = daily_tp[day].max(dim="number")               # Largest sampled member (mm), not an upper bound
```

### 3. Optional spatial diagnostics (not EFI or SOT)
These exploratory fields do not use model climatology and must not be described as probabilities, climatological anomalies, or official EFI/SOT values. To report ECMWF EFI/SOT, use ECMWF's products or implement the documented M-climate calculation.

```python
q50 = daily_tp[day].quantile(0.50, dim="number")
q90 = daily_tp[day].quantile(0.90, dim="number")
q98 = daily_tp[day].quantile(0.98, dim="number")

# Spatially normalized Q90, useful only to rank grid cells in this map.
# It is not a climatological anomaly or an exceedance probability.
q90_spatial_index = (q90 / (float(q90.max()) + 1e-5)).clip(0, 1)

# Ensemble tail spread in millimeters; this is not ECMWF Shift of Tails (SOT).
tail_spread_mm = q98 - q50
```

---

## Detailed Metric Definitions & Operational Use Cases

### 1. Empirical Exceedance Probability (Relative Frequency)
* **Definition**: The percentage of 50 ensemble members predicting precipitation above a specified physical threshold ($>20\text{mm}$, $>50\text{mm}$, $>100\text{mm}$) within a 24-hour window.
* **Mathematical Formula**:
  $$\text{Prob}_{>\text{thresh}}(x, y) = \left( \frac{1}{50} \sum_{i=1}^{50} \mathbb{I}(\Delta P_i(x, y) > \text{thresh}) \right) \times 100\%$$
* **Operational Use Cases**:
  * **Flood & Urban Drainage Preparedness**: Evaluating $>50\text{mm}$ and $>100\text{mm}$ exceedance probabilities for municipal stormwater drainage capacity and early flood advisories.
  * **Agriculture & Crop Management**: Assessing $>20\text{mm}$ probabilities for field machinery access, harvesting planning, and crop protection.
  * **Aviation & Transport Logistics**: Identifying severe rainfall disruption risks across airport hubs and highway networks.

### 2. Physical Quantiles ($Q_{50}, Q_{90}, Q_{100}$)
* **Definitions**:
  * **Ensemble Median ($Q_{50}$)**: The 50th percentile daily rainfall; represents the central expectation / baseline forecast.
  * **90th Percentile ($Q_{90}$)**: High-end severe rain scenario (only 10% of ensemble members forecast higher rainfall).
* **Ensemble maximum ($Q_{100}$)**: The largest value among the 50 perturbed members; it is not a bound on possible rainfall.
* **Operational Use Cases**:
  * **Planning context**: Use Q90 to compare scenarios and identify areas for follow-up with hydrologic and official forecasts. Do not use ensemble rain quantiles alone to determine dam releases or emergency actions.
  * **Disaster response**: Use Q90 spatial footprints as one input for situational awareness, alongside official warnings and local observations.

### 3. Spatially normalized Q90 index (not EFI)
* **Definition**: A map-relative score ($0.0$ to $1.0$) comparing Q90 with the maximum Q90 in the selected map. It has no climatology and is not an anomaly or probability.
* **Mathematical Formula**:
  $$\text{spatial Q90 index} = \text{clip}\left(\frac{Q_{90}}{\max(Q_{90})}, 0, 1\right)$$
* **Operational Use Cases**:
  * **Use**: Visual ranking of grid cells within this forecast map only. Do not use it for climatological or early-warning claims.

### 4. Ensemble tail-spread ratio (not SOT)
* **Definition**: This exploratory tail-spread ratio has no ECMWF SOT interpretation or calibrated alert thresholds and does not establish HILP risk.
* **Mathematical Formula**:
  $$\text{tail-spread ratio} = \frac{Q_{98} - Q_{50}}{Q_{50} + 2.0}$$
* **Operational Use Cases**:
  * **Use**: Compare ensemble spread within this forecast only. Do not infer HILP risk or use official SOT contour values from this ratio.

### 5. Neighborhood Ensemble Probability (NEP)
* **Definition**: A spatial rolling average ($3\times3$ grid box pooling) that mitigates spatial positioning errors inherent in convective storm forecasts.
* **Mathematical Formula**:
  $$\text{NEP}(x, y) = \frac{1}{9} \sum_{\Delta x \in \{-1,0,1\}} \sum_{\Delta y \in \{-1,0,1\}} \text{Prob}_{>\text{thresh}}(x + \Delta x, y + \Delta y)$$
* **Operational Use Cases**:
  * **River Basin & Watershed Hydrology**: Smoothing spatial jitter across complex terrain and mountain watersheds.


---

## Visualization & Plotting Recipes

### 1. Rainfall percentile and tail-spread map (Thailand Region)
```python
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

fig = plt.figure(figsize=(10, 11))
ax = fig.add_axes([0.10, 0.08, 0.68, 0.82], projection=ccrs.PlateCarree())
ax.set_extent([97.0, 106.0, 5.0, 21.0], crs=ccrs.PlateCarree())

# Shaded spatially normalized Q90; not EFI and not climatology-based.
q90_cntr = ax.contourf(lons, lats, q90_spatial_index.values, levels=np.linspace(0, 1, 21), cmap="YlOrRd")

# Tail-spread contours in millimeters; not SOT.
tail_cntr = ax.contour(lons, lats, tail_spread_mm.values, levels=5, colors='black', linewidths=1.3)
ax.clabel(tail_cntr, inline=True, fmt='%.0f mm', fontsize=9)

# Geography & Province Boundaries
provinces = cfeature.NaturalEarthFeature(
    category='cultural', name='admin_1_states_provinces_lines', scale='10m', facecolor='none'
)
ax.add_feature(cfeature.LAND, facecolor='#fdfdfd', zorder=1)
ax.add_feature(cfeature.OCEAN, facecolor='#edf4f9', zorder=1)
ax.add_feature(cfeature.COASTLINE, linewidth=1.0, edgecolor='#212121', zorder=4)
ax.add_feature(cfeature.BORDERS, linewidth=1.2, linestyle='-', edgecolor='#212121', zorder=5)
ax.add_feature(provinces, linewidth=0.5, linestyle=':', edgecolor='#666666', zorder=6)
```

### 2. High-Impact Low-Probability (HILP) Deluge Map (>100mm)
To catch rare extreme flood events:
```python
# Plot background exceedance probability shading for >100mm
contour = ax.contourf(lons, lats, prob_100mm.values, levels=np.linspace(0, 100, 21), cmap="YlOrRd")

# Highlight 10% and 20% HILP isoline contours explicitly in blue/purple
hilp_cntr = ax.contour(lons, lats, prob_100mm.values, levels=[10, 20], colors=['blue', 'purple'], linewidths=1.3)
ax.clabel(hilp_cntr, inline=True, fmt='%d%%', fontsize=9)
```

---

## Expanding to Other Meteorological Variables & Analysis

### 1. Severe Wind & Wind Gust Thresholds
* **10m Wind Gusts (`param="10fg"`)**:
  * Moderate Gust Risk: Exceedance probability for **>15 m/s** (~54 km/h)
  * Severe Storm Gust Risk: Exceedance probability for **>25 m/s** (~90 km/h)
* **10m Sustained Wind (`param="10ff"`)**:
  * Exceedance probability for **>20 m/s** (Gale force)

```python
client.retrieve(
    stream="enfo", type="pf", param="10fg", step=[24, 48, 72], target="/tmp/wind_gusts.grib2"
)
```

### 2. Temperature Extremes (`param="2t"`)
* **Extreme Heatwave Risk**: Exceedance probability for 2m Temperature **> 35°C** or **> 40°C**.
* **Frost / Freeze Risk**: Exceedance probability for 2m Temperature **< 0°C**.

### 3. Maritime & Ocean Wave Ensemble (`stream="waef"`, `param="swh"`)
* **Significant Wave Height (`swh`)**: Exceedance probability for **> 2.0 m** or **> 4.0 m** high seas.

### 4. Spatial Neighborhood Ensemble Probability (NEP)
To account for spatial convective uncertainty, apply a $3 \times 3$ grid-cell rolling spatial average:
```python
# 3x3 Neighborhood Probability Smoothing
prob_smoothed = prob_50mm.rolling(latitude=3, longitude=3, center=True).mean()
```

---

## Verification & Methodological References

1. **[ECMWF Forecast User Guide: Probability and Quantiles](https://confluence.ecmwf.int/display/FUG/Probability+and+Quantiles)**: Validates direct ensemble relative frequency $P = \frac{1}{N} \sum \mathbb{I}(\Delta P_i > \text{threshold})$ across 50 members as ECMWF's standard exceedance estimator ([ECMWF Confluence FUG](https://confluence.ecmwf.int/display/FUG/Forecast+User+Guide)).
2. **Lalaurette, F. (2003)**: *"Early detection of abnormal weather conditions using a probabilistic extreme forecast index"*, *Quarterly Journal of the Royal Meteorological Society*, 129(594), 3041-3057. ([ECMWF eLibrary](https://www.ecmwf.int/en/elibrary/9623-early-detection-abnormal-weather-conditions-using-probabilistic-forecast-index), [DOI: 10.1256/qj.02.152](https://doi.org/10.1256/qj.02.152)).
3. **Zsótér, E. (2006)**: *"Recent developments in extreme weather forecasting using the ECMWF Extreme Forecast Index"*, *Meteorological Applications*, 13(3), 247-254. ([ECMWF eLibrary](https://www.ecmwf.int/en/elibrary/10540-recent-developments-extreme-weather-forecasting-using-ecmwf-extreme-forecast-index), [DOI: 10.1002/met.29](https://doi.org/10.1002/met.29)).
4. **Roberts, N. M., & Lean, H. W. (2008)**: *"Scale-Selective Verification of Quantitative Precipitation Forecasts Using Spatial High-Resolution Forecasts"*, *Monthly Weather Review*, 136(1), 78–97. ([AMS Journals](https://journals.ametsoc.org/view/journals/mwre/136/1/2007mwr2123.1.xml), [DOI: 10.1175/2007MWR2123.1](https://doi.org/10.1175/2007MWR2123.1)).
