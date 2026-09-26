---
name: navy_tide
description: Get tide height predictions for the Gulf of Thailand / Bangkok — Royal Thai Navy Hydrographic Department (กรมอุทกศาสตร์ กองทัพเรือ) dashboard plus scriptable tide sources
---

Tide predictions matter for Bangkok and the three Samut provinces (สมุทรปราการ / สมุทรสาคร / สมุทรสงคราม): they are pump-dependent, so a high tide slows drainage and standing flood water stays longer.

The user asked: $ARGUMENTS

## How to respond

1. Prefer the **scriptable** source below (HII flat file) when the user wants numbers — it can be fetched and parsed.
2. If the user specifically asks for the **Hydrographic Department** (กรมอุทกศาสตร์) prediction, give them the dashboard URL and explain that it must be opened in a browser — it cannot be fetched programmatically (see section 2).
3. Always state the station and the local time of max/min tide; the difference between high and low tide is what drives the drainage window.

---

## 1. Scriptable tide table — HII fews2 (same data family shown on thaiwater.net)

```bash
# Daily tide predictions — 9 Gulf of Thailand stations, 4-hourly + daily max/min
curl -sL "https://fews2.hii.or.th/model-output/data_portal/tide_table/summary.txt"
```

CSV fields: `code`, `station.name.TH`, `station.name.EN`, `lat`, `long`, `date`, `max_value` (m), `max_time`, `min_value` (m), `min_time`, `time_0000`, `time_0400`, `time_0800`, `time_1200`, `time_1600`, `time_2000`

Stations: N01 Navy HQ (Sattahip) · N02 Bangkok Harbour (ท่าเรือกรุงเทพ) · N03 Fort Chulachomklao (ป้อมพระจุล) · and 6 more along the Gulf coast.

Verified 2026-09-25: file present with that day's rows (one row per station per day).

Related HII tide/sea products:

```bash
# 26 Gulf storm-surge monitoring stations with warning levels (tide + surge)
curl -sL "https://api.hii.or.th/tiservice/v1/ws/cEniGCuZcTBSa3xj4A8PY187BhpExTfE/model/stromsurge/station_info" \
  -H "User-Agent: Mozilla/5.0"

# Storm-surge / high-wave animation (latest MP4 + GIF)
curl -sL "https://api.hii.or.th/tiservice/v1/ws/cEniGCuZcTBSa3xj4A8PY187BhpExTfE/stromsurge/wave/antimation/high_wave/lastest" \
  -H "User-Agent: Mozilla/5.0"
```

---

## 2. Royal Thai Navy Hydrographic Department tide dashboard (บราเซอร์เท่านั้น)

URL (the one shared in Thai water-monitoring posts — opens the กรมอุทกศาสตร์ "Dashboard กระแสน้ำ"):

```
https://script.google.com/macros/s/AKfycbzt1dHpMeJ2fsM8oOEp4LEqm6dRKPXLZW0TfEV6KxR9FLu3UeJpojCkehLpxcP42GAWaw/exec
```

Why it cannot be fetched: it is a Google Apps Script **HTML-service** app. `curl -L` returns only the ~50 KB sandbox shell — the chart/tide data is requested inside the sandbox via `google.script.run.getDashboardData()`, which needs a real browser session. Verified 2026-09-25 (HTTP 200, but no tide values in the response body).

So: hand the URL to the user for the interactive view, and use section 1 for anything the agent must compute.

---

## 3. Reading the result (drainage logic)

- Tide heights are relative to the station datum (chart datum / MSL) — treat them as relative, not as absolute sea level; the **range** (max − min) is what matters for drainage.
- Bangkok + Samut: rain coinciding with the high-tide window drains slowly → standing water lasts longer even when rainfall totals are moderate.
- Combine with the Chao Phraya discharge (`thaiwater` `/public/waterlevel_load`, `wmsc_rid`) and the rain forecast before concluding whether the city will be flooded.
- Sea-level rise in the Gulf also feeds back on canal drainage in Samut Prakan / Samut Sakhon — check `public/weather_img/ssh_hii` in the `thaiwater` skill for the sea-surface-height product.

---

## Cross-references

- `thaiwater` — rain, water level, ocean/wave products (incl. `ssh_hii`)
- `dds_bangkok` — Bangkok canals, rain stations, pump/polder status
- `water_situation_check` — the 6-step routine (tide is its last step)
