---
name: onwr
description: Fetch national water resource data from ONWR (Office of the National Water Resources — สำนักงานทรัพยากรน้ำแห่งชาติ)
---

Fetch and display ONWR national water resource data.
The user asked: $ARGUMENTS

## How to respond

1. Identify which data type the user wants.
2. Use Bash to call accessible endpoints; note Cloudflare-protected ones.
3. Present results in a clean table with relevant context.

---

## System overview

ONWR (สทนช.) coordinates Thailand's national water resource policy and operates a national water monitoring portal aggregating data from multiple agencies:

| System | URL | Auth | Description |
|---|---|---|---|
| National Water Portal | `https://www.ntw.onwr.go.th/` | No | Aggregate national water situation map |
| ONWR Website | `https://www.onwr.go.th/` | No | Policy, regulations, reports |
| Water API | `https://api.ntw.onwr.go.th/` | Partial/Cloudflare | API backend for ntw portal |

**Note:** The `api.ntw.onwr.go.th` backend is protected by Cloudflare and cannot be fetched programmatically. Use the portal in a browser.

---

## 1. National Water Portal — ntw.onwr.go.th

Open in browser:
```
https://www.ntw.onwr.go.th/
```

The portal aggregates and displays data from:
- กรมทรัพยากรน้ำ (DWR) — EWS water level and rainfall stations
- กรมชลประทาน (RID) — reservoir storage
- สสน. (HII/thaiwater.net) — nationwide water situation
- กรมอุตุนิยมวิทยา (TMD) — weather observations and forecasts

For programmatic access to this underlying data, use the source agency APIs directly:
- Water levels and rainfall → `/ews` skill (DWR)
- Reservoir storage → `/wmsc_rid` skill (RID)
- Dam data → `/thaiwater` skill (HII/thaiwater.net)
- Weather → `/tmd` skill (TMD)

---

## 2. ONWR public website — onwr.go.th

No auth required. Useful for policy context, regulations, and reports.

```bash
# ONWR homepage (Thai)
curl -sL "https://www.onwr.go.th/" -H "User-Agent: Mozilla/5.0"
```

Key sections:
- **Water resource regulations:** `https://www.onwr.go.th/category/ระเบียบกฎหมาย/`
- **National Water Plan:** `https://www.onwr.go.th/category/แผนแม่บทน้ำ/`
- **Situation reports:** `https://www.onwr.go.th/category/รายงานสถานการณ์น้ำ/`
- **Publications / data:** `https://www.onwr.go.th/category/ข้อมูลสารสนเทศ/`

---

## 3. Chao Phraya basin water allocation

ONWR coordinates inter-agency water allocation decisions for the Chao Phraya basin. Published decisions and announcements appear on the ONWR website and via the Royal Irrigation Department (RID):

```bash
# RID upper Chao Phraya water management plan
curl -sL "https://water.rid.go.th/flood/plan_new/planup.html" \
  -H "User-Agent: Mozilla/5.0"

# RID lower Chao Phraya water management plan
curl -sL "https://water.rid.go.th/flood/plan_new/planlow.html" \
  -H "User-Agent: Mozilla/5.0"
```

---

## 4. ONWR Open Data

ONWR publishes datasets on Thailand's national open data portal:

```
https://data.go.th/organization/onwr
```

Includes water quality surveys, basin-level water balance data, and groundwater reports. Data is published as CSV/Excel downloads, not as a live API.

---

## About ONWR

สำนักงานทรัพยากรน้ำแห่งชาติ (ONWR) was established in 2018 under the National Water Resources Act to serve as the single national authority for water resource management policy. It coordinates between 35+ government agencies involved in water management, sets water allocation priorities, and issues drought/flood advisories at national level.

- Website: https://www.onwr.go.th
- National water portal: https://www.ntw.onwr.go.th
- Hotline: 1460
