---
name: rid_forecast
description: Fetch RID water-level / runoff forecasts (คาดการณ์น้ำท่า) and hydrology reference data from water.rid.go.th — ฝ่ายสารสนเทศและพยากรณ์น้ำ ส่วนอุทกวิทยา กรมชลประทาน
---

Fetch RID runoff/water-level forecasts and hydrology reference material.

The user asked: $ARGUMENTS

## How to respond

1. Identify whether the user wants a **forecast chart** (คาดการณ์น้ำท่า, image) or **reference criteria** (warning thresholds, rainfall-runoff tables).
2. Use Bash to `curl` the page/image; RID HTML pages use legacy Thai encodings (the index currently reports `ISO-8859-11`; other pages may report `windows-874` or `x-mac-thai`). Check the response `Content-Type` and pass its charset to `iconv` before reading Thai text.
3. Forecast charts are **JPEG images with no numeric API** — download and read the image (vision) or report the `Last-Modified` date as the freshness signal. Never quote numbers off a chart unless you actually looked at it.
4. For numeric station values (thresholds, current level, over-bank status) use the API skills instead: `thaiwater` (`/public/waterlevel_load`) or `wmsc_rid` (Telerid).

---

## 1. Runoff / water-level forecast pages — water.rid.go.th/itcwater/utok

Published by ฝ่ายสารสนเทศและพยากรณ์น้ำ ส่วนอุทกวิทยา (RID hydrology division). Layout:

| URL | Content |
|---|---|
| `http://water.rid.go.th/itcwater/utok/index.html` | Index: station list per basin + reference links + station location map (`map2.jpg`) |
| `http://water.rid.go.th/itcwater/utok/{CODE}.html` | One station page (small HTML page); use the index filename code (for example `P1`, not the display label `P.1`) |
| `http://water.rid.go.th/itcwater/utok/F-{CODE}.jpg` | The forecast chart itself — use the same punctuation-free filename code (for example `F-P1.jpg` for station P.1) |

```bash
# Index (station list + criteria links)
curl -sL "http://water.rid.go.th/itcwater/utok/index.html" | iconv -f ISO-8859-11 -t UTF-8 | sed -n '40,100p'

# A station's forecast chart (RID filenames omit punctuation from display codes)
curl -sL "http://water.rid.go.th/itcwater/utok/F-C2.jpg" -o F-C2.jpg
curl -sI "http://water.rid.go.th/itcwater/utok/F-C2.jpg" | grep -i last-modified   # freshness
# P.1 is named P1 in the URL: .../F-P1.jpg
```

### Station catalog (from the index page, verified 2026-09-25)

| Basin | Stations |
|---|---|
| ปิง (Ping) | P.1, P.17 |
| วัง (Wang) | W.1C, W.3A |
| ยม (Yom) | Y.1C |
| น่าน (Nan) | N.67, N.1, N.8B |
| เจ้าพระยา (Chao Phraya) | C.2 |
| โขงตะวันออกเฉียงเหนือ | Kh.58A |
| ชี (Chi) | E.18, E.20A |
| มูล (Mun) | M.182, M.7 |
| บางปะกง (Bang Pakong) | Kgt.3 |

### C.2 carries printed numeric forecasts (verified 2026-09-30)

The C.2 chart is not picture-only: it prints the numbers on the curves, so it can be read without a numeric API.

- Header: `กราฟคาดการณ์ปริมาณน้ำล่วงหน้า 1 - 3 วัน ด้วยแบบจำลอง ANNs แม่น้ำเจ้าพระยา สถานี C.2 อ.เมือง จ.นครสวรรค์` + a data timestamp (`ข้อมูล ณ วันที่ … เวลา 06.00 น.`).
- Series: blue = observed discharge (ลบ.ม./วิ), red = forecast discharge **and** water level in `ม.(รทก.)` printed as `2,713.00 (24.26 ม.)`, green dot = current discharge, red dashed = `ความจุลำน้ำ` (channel capacity).
- Fixed station annotations: `ระดับตลิ่ง 25.70 ม.(รทก.) / ความจุลำน้ำ 3,735 ลบ.ม./วินาที เริ่มท่วมพื้นที่ลุ่มต่ำเขตเทศบาลนครสวรรค์`.
- Reading it: the assistant has no native vision — download the JPEG and go through the image-vision (DeepSeek) skill. **Always crop/zoom the label area first**: a whole-chart read on 2026-09-30 returned 25.51/26.26/26.63 m MSL, while two independent zoomed reads of the printed labels gave the correct 24.26/24.64/24.63 m MSL (cross-checked against telemetry: C.2 12:00 = 23.77 m MSL / 2,443 m³/s).
- Cross-check any read against the thaiwater API reading for the same station before quoting it.

### Chart availability (verified 2026-09-25 — check `Last-Modified` before trusting a chart)

| Status | Stations |
|---|---|
| Updated daily (~00:0x–00:29 UTC = ~07:00–07:30 Thai) | P.1, P.17, Y.1C, N.67, N.1, N.8B, C.2, E.18, E.20A, M.7 |
| Stale — last updated Nov 2025 | W.1C (24 Nov 2025), W.3A (23 Nov 2025), M.182 (23 Nov 2025) |
| Page exists, chart 404 | Kh.58A, Kgt.3 |

Rule of thumb: if `Last-Modified` is not within ~36 h, say the forecast is stale rather than presenting it as current.

---

## 2. Reference criteria & statistics — water.rid.go.th/hyd

Reachable, no auth, mostly HTML/PDF (windows-874):

| URL | Content |
|---|---|
| `http://water.rid.go.th/hyd/PORTAL/submenu/4-06-1.html` | ช่วงเวลาในการเฝ้าระวังน้ำท่วม — flood watch periods |
| `http://water.rid.go.th/hyd/download/warning2/index.html` | เกณฑ์การเฝ้าระวังน้ำท่วม — flood warning thresholds |
| `http://water.rid.go.th/hyd/PORTAL/submenu/3-01.html` | เกณฑ์ปริมาณฝน 1 วัน ที่ทำให้เกิดน้ำท่วม — 1-day rainfall flood thresholds |
| `http://water.rid.go.th/hyd/download/rainfall-runoff-25basin.pdf` | ปริมาณฝน-น้ำท่าใน 22 ลุ่มน้ำหลัก — rainfall vs runoff by basin |
| `http://water.rid.go.th/hyd/PORTAL/submenu/6-022.html` | สถิติอุทกวิทยาประจำปี (Yearbook) |
| `http://water.rid.go.th/hyd/PORTAL/submenu/4-09.html` | ปริมาณน้ำท่ารายปีเฉลี่ยต่อพื้นที่รับน้ำฝน |
| `http://water.rid.go.th/hyd/index.html` | ฝ่ายสารสนเทศและพยากรณ์น้ำ main page |

Use these to answer "is this rainfall total actually dangerous for this basin?" instead of guessing thresholds.

---

## 3. Numeric water-level data (use instead of the image charts)

When the user needs numbers rather than a picture, these verified endpoints cover the same rivers:

```bash
# thaiwater API — all ~800 telemetry water-level stations, incl. warning/critical levels,
# situation_level and diff_wl_bank_text (ล้นตลิ่ง = over-bank)
curl -sL "https://api-v3.thaiwater.net/api/v1/thaiwater30/public/waterlevel_load" \
  -H "Accept: application/json"

# RID Telerid — 921 stations: station list / basin tree (public); live readings need a token
curl -sL "https://telerid.rid.go.th/restapi/main/station_list/" -H "User-Agent: Mozilla/5.0"
```

Cross-reference RID station codes (`C.2`, `P.17`, `N.67`, `Kgt.3` …) with `station.tele_station_oldcode` in the thaiwater payload, or with `code` in the Telerid payload. The thaiwater API carries `warning_level_m` / `critical_level_m` per station, which the image charts do not expose.

---

## 4. Hosts NOT reachable from this VM (browser-only)

Attempted 2026-09-25 — both hosts resolve but TCP connect times out on ports 80 and 443; do not retry them programmatically:

| Host / URL | Content | Result |
|---|---|---|
| `hydro-2.rid.go.th/index1.html` | ศูนย์อุทกวิทยาที่ 2 — live river water-level / runoff viewer | connect timeout |
| `hyd-app-db.rid.go.th/SVG/flow_water.html?svg=hydro5_637977164104194493` | River cross-section / flow SVG viewer per station (e.g. Chao Phraya `hydro5`) | connect timeout |
| `hyd-app.rid.go.th` | related app host | blocked by SSRF guard (internal/private classification) |

Practical consequence: the "ล้นตลิ่งแล้วหรือยัง" check has to be done through the APIs in section 3 (or `wmsc_rid` Telerid + `water.rid.go.th/flood/` reports), and the per-station river cross-section charts can only be viewed by a human in a browser.

River context for the Chao Phraya (the pairing used in RID analyses): **C.2 Nakhon Sawan** (upper inflow) together with **C.13 เขื่อนเจ้าพระยา / Chao Phraya Dam** (regulated release at Chai Nat); for the Tha Chin, stations around Nakhon Pathom / Suphan Buri. Releases are always a judgement on downstream river level + rain outlook together — never read dam release numbers alone.

---

## Cross-references

- `thaiwater` — rain accumulation, water level (`situation_level`), dam storage APIs
- `wmsc_rid` — Telerid stations, RID reservoir app, flood situation PDFs
- `egat` — EGAT hydro dam storage / inflow / outflow
- `water_situation_check` — the 6-step daily routine that strings all of these together
