---
name: ddpm
description: Fetch disaster warnings and situation reports from DDPM (Department of Disaster Prevention and Mitigation — กรมป้องกันและบรรเทาสาธารณภัย)
---

Fetch and display DDPM disaster warning and situation data.
The user asked: $ARGUMENTS

## How to respond

1. Identify which data type the user wants (warnings, situation reports, flood events).
2. Use Bash to call accessible endpoints; note Cloudflare-protected systems.
3. Present results in a readable summary with severity levels and locations.

---

## System overview

DDPM (ปภ.) is Thailand's national disaster agency responsible for issuing warnings, coordinating response, and publishing situation reports for floods, storms, and other disasters.

| System | URL | Auth | Access |
|---|---|---|---|
| Main website | `https://www.disaster.go.th/` | No | Cloudflare JS challenge — browser only |
| Warning API | `https://api.disaster.go.th/` | No | Cloudflare JS challenge — browser only |
| Flood monitoring | `https://flood.disaster.go.th/` | No | Cloudflare JS challenge — browser only |
| Open data | `https://data.go.th/organization/ddpm` | No | CSV/Excel downloads |

**Note:** All DDPM API endpoints are protected by Cloudflare's JavaScript challenge and cannot be accessed programmatically. Use a browser or the alternatives below.

---

## Accessible alternatives

Since DDPM's API is Cloudflare-protected, use these public sources for DDPM-equivalent data:

### Flash flood and storm warnings

```bash
# DDPM issues warnings that HII aggregates — use HII flash flood API instead:
curl -sL "https://api.hii.or.th/v2/4UQaYnf0Bx4fXPYyCdDRbqHyXH9Ixvd2nVUjaN1cLBY=/warning/flashflood-24h" \
  -H "User-Agent: Mozilla/5.0"
```

### TMD severe weather warnings

```bash
# TMD weather warnings page (HTML — parse for latest warnings)
curl -sL "https://www.tmd.go.th/warningpage" -H "User-Agent: Mozilla/5.0"

# TMD heavy rain warnings
curl -sL "https://www.tmd.go.th/warning-rain/warning-rain" -H "User-Agent: Mozilla/5.0"

# TMD storm / tropical cyclone warnings
curl -sL "https://www.tmd.go.th/warning-strom/warning-strom" -H "User-Agent: Mozilla/5.0"
```

### Flooded roads

```bash
# thaiwater.net flood road reports
curl -sL "https://api-v3.thaiwater.net/api/v1/thaiwater30/public/flood_road" \
  -H "Accept: application/json"
```

### Flood situation (national)

```bash
# RID daily flood situation report (PDF)
curl -sL "https://water.rid.go.th/flood/flood/daily.pdf" -o ddpm_daily_flood.pdf

# RID weekly flood situation report
curl -sL "https://water.rid.go.th/flood/flood/weekreportnew.pdf" -o weekly_flood.pdf
```

---

## DDPM public resources (browser access)

| Resource | URL |
|---|---|
| Main portal | https://www.disaster.go.th |
| Disaster warnings (Thai) | https://www.disaster.go.th/th/ข่าวภัยพิบัติ |
| Flood situation map | https://flood.disaster.go.th |
| PM Flood Center | https://www.floodcenter.go.th |
| Emergency hotline | 1784 (24 hours) |

---

## DDPM warning levels

| Level | Color | Meaning |
|---|---|---|
| ระวัง (Watch) | Yellow | Possible hazard — monitor closely |
| เตือน (Warning) | Orange | Hazard likely — prepare to act |
| วิกฤต (Critical) | Red | Immediate danger — take protective action |

---

## Open data — data.go.th

DDPM publishes historical datasets on Thailand's national open data portal:

```
https://data.go.th/organization/ddpm
```

Includes flood event records, disaster statistics, and annual situation reports. Data is published as CSV/Excel downloads.

---

## About DDPM

กรมป้องกันและบรรเทาสาธารณภัย (DDPM) operates under the Ministry of Interior and is responsible for issuing disaster warnings, coordinating evacuation, and managing the national disaster response network across all 77 provinces. It operates 76 provincial disaster prevention offices and the national Emergency Operations Center (EOC).

- Website: https://www.disaster.go.th
- Flood portal: https://flood.disaster.go.th
- Hotline: 1784
