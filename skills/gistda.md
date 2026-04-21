---
name: gistda
description: Fetch satellite flood mapping and disaster data from GISTDA (Geo-Informatics and Space Technology Development Agency — สำนักงานพัฒนาเทคโนโลยีอวกาศและภูมิสารสนเทศ)
---

Fetch and display GISTDA satellite flood and disaster mapping data.
The user asked: $ARGUMENTS

## How to respond

1. Identify which data type the user wants (flood extent, WMS layers, disaster maps).
2. Use Bash to call WMS/API endpoints and present results or image URLs.
3. For WMS layers, construct GetMap requests with appropriate parameters.

---

## System overview

GISTDA provides satellite-derived flood mapping using SAR (Synthetic Aperture Radar) imagery:

| System | URL | Auth | Description |
|---|---|---|---|
| Flood WMS | `api-gateway.gistda.or.th/api/2.0/resources/maps/flood/7days/wms` | API key (public) | Flood extent WMS layers from SAR analysis |
| Disaster Dashboard | `https://disaster.gistda.or.th/flood/` | No | Interactive flood mapping SPA |
| Flood Portal | `https://flood.gistda.or.th/` | No | Flood situation maps and reports |

---

## 1. Flood Extent WMS — api-gateway.gistda.or.th

**API key (embedded in public dashboard):** `m4bUUjGDPc3rdxyb8JHcL8SDhgLHPgRjq2NBeibPIucJkpxuoHahMVwXwRjKTOq6`

### GetCapabilities (discover available layers)

```bash
curl -sL "https://api-gateway.gistda.or.th/api/2.0/resources/maps/flood/7days/wms?api_key=m4bUUjGDPc3rdxyb8JHcL8SDhgLHPgRjq2NBeibPIucJkpxuoHahMVwXwRjKTOq6&SERVICE=WMS&REQUEST=GetCapabilities" \
  -H "User-Agent: Mozilla/5.0"
```

Returns WMS XML listing all available flood layers with names, bounding boxes, and time extents.

### GetMap — request a flood extent image

```bash
# Flood extent map — Thailand bounding box, 7-day SAR analysis
curl -sL "https://api-gateway.gistda.or.th/api/2.0/resources/maps/flood/7days/wms?api_key=m4bUUjGDPc3rdxyb8JHcL8SDhgLHPgRjq2NBeibPIucJkpxuoHahMVwXwRjKTOq6&SERVICE=WMS&REQUEST=GetMap&VERSION=1.1.1&LAYERS=flood&STYLES=&FORMAT=image/png&TRANSPARENT=true&SRS=EPSG:4326&BBOX=97.5,5.5,105.7,20.5&WIDTH=800&HEIGHT=600" \
  -o flood_extent.png
```

**WMS parameters:**

| Parameter | Value | Description |
|---|---|---|
| `SERVICE` | `WMS` | Service type |
| `REQUEST` | `GetCapabilities` or `GetMap` | Request type |
| `VERSION` | `1.1.1` | WMS version |
| `LAYERS` | See GetCapabilities | Layer name(s) |
| `FORMAT` | `image/png` | Output format |
| `TRANSPARENT` | `true` | Transparent background |
| `SRS` | `EPSG:4326` | Coordinate system |
| `BBOX` | `minLon,minLat,maxLon,maxLat` | Bounding box |
| `WIDTH` / `HEIGHT` | pixels | Image dimensions |

### Common bounding boxes

| Area | BBOX |
|---|---|
| Thailand (full) | `97.5,5.5,105.7,20.5` |
| Central Thailand | `99.0,13.0,102.0,16.0` |
| Chao Phraya basin | `99.5,13.5,101.5,15.5` |
| Bangkok area | `100.3,13.5,101.0,14.0` |
| North Thailand | `97.5,17.0,102.5,20.5` |
| Northeast Thailand | `101.5,14.0,105.7,18.5` |
| South Thailand | `99.0,5.5,105.0,12.0` |

---

## 2. Disaster Dashboard — disaster.gistda.or.th

Browser-only (Next.js SPA). No public REST API — all data loaded dynamically.

```
https://disaster.gistda.or.th/flood/
```

Features:
- Current flood extent overlaid on basemap
- Province-level flood area statistics (km²)
- SAR image acquisition dates
- Historical flood comparison

---

## 3. Flood Portal — flood.gistda.or.th

```
https://flood.gistda.or.th/
```

Provides:
- Downloadable flood extent shapefiles
- SAR analysis reports (PDF)
- Historical flood events archive
- Near-real-time flood monitoring (updated within 1–3 days of SAR pass)

---

## 4. Other GISTDA data products

| Product | URL | Description |
|---|---|---|
| THEOS-2 imagery | `https://earthobservation.gistda.or.th/` | Thai satellite imagery portal |
| Map catalog | `https://catalog.gistda.or.th/` | Geospatial data catalog |
| Open data | `https://data.gistda.or.th/` | Open geospatial datasets |
| Atmosphere | `https://atmosphere.gistda.or.th/` | Air quality / PM2.5 monitoring |

---

## About GISTDA

สำนักงานพัฒนาเทคโนโลยีอวกาศและภูมิสารสนเทศ (GISTDA) operates Thailand's earth observation satellite program (THEOS-1, THEOS-2) and provides satellite-based monitoring of floods, droughts, forest fires, and other disasters. Flood mapping uses SAR imagery which can penetrate clouds — particularly useful during monsoon season.

- Flood portal: https://flood.gistda.or.th
- Disaster dashboard: https://disaster.gistda.or.th
- Earth observation: https://earthobservation.gistda.or.th
