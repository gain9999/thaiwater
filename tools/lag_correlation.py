#!/usr/bin/env python3
"""Travel-time lag between upstream/downstream stations, done properly:
resample each series to a common hourly grid (time-based), then find the shift
in hours that maximises the correlation of hourly level increments."""
import json, urllib.request, datetime, math, os
from collections import defaultdict

WL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'waterlevel_load.json')
if not os.path.exists(WL):
    raise SystemExit(
        f"snapshot not found: {WL}\n"
        "Run tools/fetch_nodes.py once (it writes data/waterlevel_load.json from the "
        "key-free public API).")
d = json.load(open(WL))
ids = {}
for s in d['waterlevel_data']['data']:
    st = s.get('station') or {}
    c = str(st.get('tele_station_oldcode') or '')
    if c:
        ids[c] = st.get('id')

PAIRS = [('C.2', 'CPY002'), ('CPY002', 'C.13'), ('CPY005', 'CPY006'),
         ('CPY006', 'C.3'), ('C.3', 'CPY007'), ('CPY007', 'C.7A'), ('CPY008', 'CPY012')]
DAYS = 45


def hourly(code):
    sid = ids.get(code)
    if not sid:
        return {}
    end = datetime.date.today(); start = end - datetime.timedelta(days=DAYS)
    url = ('https://api-v3.thaiwater.net/api/v1/thaiwater30/public/waterlevel_graph'
           f'?station_type=tele_waterlevel&station_id={sid}&start_date={start}&end_date={end}')
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    body = json.loads(urllib.request.urlopen(req, timeout=60).read().decode())
    acc = defaultdict(list)
    for row in body.get('data', {}).get('graph_data', []) or []:
        if row.get('value') in (None, ''):
            continue
        try:
            dt = datetime.datetime.strptime(row['datetime'][:16], '%Y-%m-%d %H:%M')
            acc[dt.replace(minute=0)].append(float(row['value']))
        except Exception:
            pass
    return {k: sum(v)/len(v) for k, v in acc.items()}


def corr(x, y):
    m = min(len(x), len(y))
    if m < 30:
        return None
    x, y = x[:m], y[:m]
    mx, my = sum(x)/m, sum(y)/m
    num = sum((x[i]-mx)*(y[i]-my) for i in range(m))
    dx = math.sqrt(sum((v-mx)**2 for v in x)); dy = math.sqrt(sum((v-my)**2 for v in y))
    return num/(dx*dy) if dx and dy else None


cache = {}
for up, dn in PAIRS:
    for c in (up, dn):
        if c not in cache:
            cache[c] = hourly(c)
    A, B = cache[up], cache[dn]
    grid = sorted(set(A) & set(B))
    print(f'\n{up} -> {dn}: common hours={len(grid)}')
    if len(grid) < 100:
        continue
    a = [A[t] for t in grid]; b = [B[t] for t in grid]
    best = []
    for lag in range(0, 61):
        x = [a[i+1]-a[i] for i in range(len(a)-1)][:len(a)-1-lag]
        y = [b[i+lag+1]-b[i+lag] for i in range(len(b)-1-lag)]
        r = corr(x, y)
        if r is not None:
            best.append((r, lag))
    best.sort(reverse=True)
    for r, lag in best[:3]:
        print(f'   lag {lag:3} h  r={r:+.3f}')
