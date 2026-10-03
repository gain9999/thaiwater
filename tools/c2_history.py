#!/usr/bin/env python3
"""Print C.2 (oldcode) 06:00 discharge/level for the last N days from thaiwater graph."""
import json, urllib.request, datetime, sys

UA = {'User-Agent': 'Mozilla/5.0'}
def get(url):
    return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90).read().decode())

end = datetime.date.today()
start = end - datetime.timedelta(days=9)
url = (f'https://api-v3.thaiwater.net/api/v1/thaiwater30/public/waterlevel_graph_oldcode'
       f'?station_id=C.2&agency_id=9&start_date={start}&end_date={end}')
b = get(url)
rows = (b.get('data') or {}).get('graph_data') or []
print('rows', len(rows))
byh = {}
for r in rows:
    dt = r.get('datetime')
    if not dt: continue
    byh[dt] = r
keys = sorted(byh)
print('range', keys[0], '->', keys[-1])
print(f"{'datetime':<18}{'level_msl':>10}{'discharge':>12}")
for k in keys:
    if ':06:00' in k or k.endswith('06:00'):
        r = byh[k]
        print(f"{k:<18}{str(r.get('waterlevel_msl')):>10}{str(r.get('discharge')):>12}")
# last 12 hourly
print('--- last 12 ---')
for k in keys[-12:]:
    r = byh[k]
    print(f"{k:<18}{str(r.get('waterlevel_msl')):>10}{str(r.get('discharge')):>12}")
