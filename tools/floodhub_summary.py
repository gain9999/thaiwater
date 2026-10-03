#!/usr/bin/env python3
"""Summarise the Flood Hub JSON: corridor gauges, severities, nearest to C.2/C.13."""
import json, math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'out', 'floodhub', 'c13_floodhub.json')
if not os.path.exists(SRC):
    raise SystemExit(
        f"Flood Hub JSON not found: {SRC}\n"
        "Run tools/floodhub_c13.py first (needs FLOODHUB_API_KEY), or pass the JSON path.")
D = json.load(open(SRC))
gauges = D['gauges']; statuses = D['statuses']; models = D['models']; report = D['report']

print('TH gauges:', len(gauges), ' statuses:', len(statuses))
cnt = {}
for s in statuses.values():
    cnt[s.get('severity')] = cnt.get(s.get('severity'), 0) + 1
print('TH severity:', cnt)

def hav(a, b):
    R = 6371.0
    la1, lo1, la2, lo2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    return 2 * R * math.asin(math.sqrt(math.sin((la2 - la1) / 2) ** 2
                                       + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2))

print('\n=== corridor gauges (13.4-16.0N, 99.0-101.6E) with a status, nearest-first to C.13 ===')
C13 = (15.16384, 100.18792)
rows = []
for g in gauges:
    la, lo = g['location']['latitude'], g['location']['longitude']
    if 13.4 <= la <= 16.0 and 99.0 <= lo <= 101.6:
        s = statuses.get(g['gaugeId'])
        if not s:
            continue
        rows.append((hav(C13, (la, lo)), g, s))
rows.sort(key=lambda r: r[0])
for d, g, s in rows:
    m = models.get(g['gaugeId'], {}).get('thresholds', {})
    print(f'{d:5.1f} km  {g["gaugeId"]:>22}  {g["location"]["latitude"]:.3f},{g["location"]["longitude"]:.3f}'
          f'  {s.get("severity",""):<13} trend={s.get("forecastTrend")}  warn={m.get("warningLevel")}'
          f' danger={m.get("dangerLevel")} extreme={m.get("extremeDangerLevel")}')

print('\n=== nearest gauges to C.2 / C.13 (from report) ===')
for k, v in report.items():
    if k.startswith('C.2') or k.startswith('C.13'):
        print(f'\n{k}: {v["lat"]:.3f},{v["lon"]:.3f} sev={v["severity"]} trend={v["trend"]} qv={v["qualityVerified"]}')
        print('  thresholds', json.dumps(v['thresholds']))
        s = v.get('series') or []
        for t, val in s:
            print(f'   {t}  {val}')
