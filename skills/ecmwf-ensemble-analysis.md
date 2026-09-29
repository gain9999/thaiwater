---
name: ecmwf-ensemble-analysis
description: >-
  Retrieves ECMWF ensemble forecasts (50 members), processes GRIB2 precipitation and atmospheric data, computes discrete 24-hour daily accumulations, exceedance probabilities and percentiles, and can estimate an explicitly labeled EFI-like index against a free historical climatology. Use when asked to download ECMWF ensemble data, map rainfall risk, or approximate EFI/SOT without ECMWF M-climate access. Don't describe the proxy as official ECMWF EFI/SOT. Don't use for raw satellite imagery or non-ECMWF GFS data.
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

### 1. Free Open Data vs. Model Climatology
* **Free Open Data (`ecmwf.opendata`)**: Accesses public ECMWF forecasts (`data.ecmwf.int`). Provides 50 perturbed ensemble members (`stream="enfo"`, `type="pf"`) for lead times up to **360 hours (15 days)**.
* **Climatology limitation**: Open forecast members alone cannot produce EFI or SOT: both compare a forecast distribution with a reference climate distribution. ECMWF's official EFI uses its model climate (M-climate), built from reforecasts. That reference is distinct from the current free real-time forecast subset; check ECMWF's current data-access terms before assuming M-climate fields or reforecasts are freely downloadable.
* **Free-data approach**: Use a free historical gridded dataset such as ERA5 as a documented reference climatology, then compare today's ECMWF ensemble to it. This yields an **ERA5-referenced EFI-like index**, not ECMWF EFI: the forecast model and reference dataset differ, and ERA5 does not reproduce ECMWF's lead-time-dependent M-climate. Keep this distinction visible in field names, map titles, legends, and any published interpretation.

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

### 3. EFI-like index from a free reference climatology
This is the main free-data approximation when ECMWF M-climate is unavailable. Obtain historical 24-hour precipitation samples from a free gridded climate dataset (for example, ERA5), use the same accumulation definition as the forecast, and construct a calendar-day climatology at each grid cell. A practical starting window is the target day-of-year +/- 15 days across all available years. Regrid the reference consistently, and document the dataset, period, calendar window, accumulation, and interpolation method. ERA5 is an observation/reanalysis reference, not ECMWF's model climate; forecast bias and resolution differences can affect the result.

At each grid cell, let `climate_samples` be those historical daily totals and `forecast_members` the 50 ECMWF daily totals. Evaluate the forecast empirical CDF at climate quantiles and integrate the weighted CDF difference:

$$EFI_{like} = \frac{2}{\pi} \int_0^1 \frac{p - F_f(Q_c(p))}{\sqrt{p(1-p)}}\,dp$$

Positive values indicate a forecast shifted toward wetter conditions relative to the selected reference. Do not apply official ECMWF EFI thresholds or interpret this as an official warning category. It is a rough proxy, especially where the climate product, model bias, grid resolution, or near-zero-rain frequency differ substantially.

```python
import numpy as np

def efi_like_rain(forecast_members_mm, climate_samples_mm):
    """Scalar-grid-cell EFI-like score; requires matched daily totals in mm."""
    forecast = np.asarray(forecast_members_mm, dtype=float)
    climate = np.asarray(climate_samples_mm, dtype=float)
    forecast = forecast[np.isfinite(forecast)]
    climate = climate[np.isfinite(climate)]
    if forecast.size == 0 or climate.size < 20:
        return np.nan

    # Avoid the singular endpoints in the EFI weighting function.
    p = np.linspace(0.005, 0.995, 199)
    climate_quantiles = np.quantile(climate, p)
    forecast_cdf = (forecast[:, None] <= climate_quantiles[None, :]).mean(axis=0)
    integrand = (p - forecast_cdf) / np.sqrt(p * (1.0 - p))
    return float((2.0 / np.pi) * np.trapz(integrand, p))
```

For an array workflow, apply this calculation independently to each latitude/longitude cell and forecast valid day; do not pool climate samples across locations. Use the same daily accumulation period for the ECMWF forecast and reference. Label outputs `efi_like_era5`, not `efi`.

### 4. SOT-like upper-tail shift from a free reference
If a comparable reference climatology is available, the documented upper-tail SOT relationship can be approximated with forecast Q90 and climate Q90/Q99:

$$SOT_{like}(90) = \frac{Q_{f}(90) - Q_{c}(99)}{Q_{c}(99) - Q_{c}(90)}$$

Here `Qf` comes from today's ECMWF members, while `Qc` comes from the chosen free climate reference. Call this `sot_like_era5` (or name the selected reference); it is not ECMWF SOT and official thresholds do not transfer. Guard against a zero or near-zero climate Q99-Q90 denominator and return missing rather than an unstable value. The raw `(Q98 - Q50)` ensemble spread may still be reported in mm as a separate forecast-spread diagnostic, but it is not SOT.

### 5. Optional spatial diagnostics (not EFI or SOT)
Map-relative fields do not use climatology and must not be described as probabilities or climatological anomalies. They can supplement, but cannot replace, the reference-based EFI-like calculation above.

```python
q50 = daily_tp[day].quantile(0.50, dim="number")
q90 = daily_tp[day].quantile(0.90, dim="number")
q98 = daily_tp[day].quantile(0.98, dim="number")

# Spatially normalized Q90, useful only to rank grid cells in this map.
# It is not a climatological anomaly or an exceedance probability.
q90_spatial_index = (q90 / (float(q90.max()) + 1e-5)).clip(0, 1)

# Ensemble spread in millimeters; this is not ECMWF Shift of Tails (SOT).
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

### 3. ERA5-referenced EFI-like score (not official EFI)
* **Definition**: A weighted comparison between the ECMWF forecast ensemble CDF and a free historical precipitation reference CDF, using the EFI form of the integral. It preserves EFI's core distribution-comparison idea, but uses a different climate reference from ECMWF M-climate.
* **Interpretation**: Positive values indicate a wetter-than-reference forecast. Do not use official EFI thresholds or label it simply `EFI`.
* **Requirements**: Matched daily precipitation totals, per-grid-cell calendar-day climate samples, and documented reference dataset/time period. A single ECMWF ensemble run is not its own climatology.

### 4. SOT-like Q90 shift (not official SOT)
* **Definition**: `(forecast Q90 - climate Q99) / (climate Q99 - climate Q90)` using the chosen free climate reference.
* **Interpretation**: It approximates the upper-tail comparison form, but ERA5-based values are not ECMWF SOT and its alert thresholds must not be borrowed. Mask cells with a near-zero denominator.

### 5. Spatially normalized Q90 index (not EFI)
* **Definition**: A map-relative score ($0.0$ to $1.0$) comparing Q90 with the maximum Q90 in the selected map. It has no climatology and is not an anomaly or probability.
* **Mathematical Formula**:
  $$\text{spatial Q90 index} = \text{clip}\left(\frac{Q_{90}}{\max(Q_{90})}, 0, 1\right)$$
* **Operational Use Cases**:
  * **Use**: Visual ranking of grid cells within this forecast map only. Do not use it for climatological or early-warning claims.

### 6. Neighborhood Ensemble Probability (NEP)
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
