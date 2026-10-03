#!/usr/bin/env python3
"""List Chao Phraya basin gauges (13-20.5N, 97.5-102.2E) flagged SEVERE/EXTREME with peaks."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'out', 'floodhub', 'c13_floodhub.json')
if not os.path.exists(SRC):
    raise SystemExit(
        f"Flood Hub JSON not found: {SRC}\n"
        "Run tools/floodhub_c13.py first (needs FLOODHUB_API_KEY), or pass the JSON path.")
D = json.load(open(SRC))
gauges = D['gauges']; statuses = D['statuses']; models = D['models']

rows = []
for g in gauges:
    la, lo = g['location']['latitude'], g['location']['longitude']
    if not (13.0 <= la <= 20.5 and 97.5 <= lo <= 102.2):
        continue
    s = statuses.get(g['gaugeId'])
    if not s or s.get('severity') not in ('SEVERE', 'EXTREME'):
        continue
    m = models.get(g['gaugeId'], {}).get('thresholds', {})
    rows.append((s['severity'], la, lo, g['gaugeId'], s.get('forecastTrend'), m))
rows.sort(key=lambda r: (r[0] != 'EXTREME', -r[1]))
print(f'Chao Phraya box SEVERE/EXTREME gauges: {len(rows)}')
for sev, la, lo, gid, tr, m in rows:
    print(f'  {sev:<8} {la:6.3f},{lo:7.3f}  {gid:>22} trend={tr} warn={m.get("warningLevel")} '
          f'danger={m.get("dangerLevel")} extreme={m.get("extremeDangerLevel")}')
