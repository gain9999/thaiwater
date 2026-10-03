#!/usr/bin/env python3
"""Google Flood Forecasting API over the Chao Phraya corridor (C.2 -> C.13 -> Ayutthaya).

Finds gauges near the RID stations, prints latest flood status, thresholds and
the 7-day discharge forecast, and saves everything to JSON for the report.
"""
import json, os, sys, urllib.parse, urllib.request, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def api_key():
    """Flood Forecasting API key: env FLOODHUB_API_KEY, else ~/.floodhub-api-key."""
    k = os.environ.get('FLOODHUB_API_KEY', '').strip()
    if k:
        return k
    p = os.path.expanduser('~/.floodhub-api-key')
    if os.path.exists(p):
        return open(p).read().strip()
    raise SystemExit('set FLOODHUB_API_KEY to a Google Flood Forecasting API key')


KEY = api_key()
BASE = 'https://floodforecasting.googleapis.com/v1'
OUT = os.path.join(ROOT, 'out', 'floodhub')
os.makedirs(OUT, exist_ok=True)

# RID reference stations (lat, lon) from the thaiwater feed
REF = {
    'C.2  Nakhon Sawan': (15.7047, 100.1083),
    'C.13 tail of Chao Phraya Dam': (15.16384, 100.18792),
    'C.3  Bang Phutsa (Sing Buri)': (14.8850, 100.4010),
    'C.7A Bang Kaeo (Ang Thong)': (14.5620, 100.4400),
    'CPY011 Ayutthaya': (14.36913, 100.52861),
}


def post(path, body):
    req = urllib.request.Request(
        f'{BASE}{path}?key={KEY}', data=json.dumps(body).encode(),
        headers={'Content-Type': 'application/json'}, method='POST')
    return json.loads(urllib.request.urlopen(req, timeout=90).read().decode())


def get(path, params):
    q = urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(f'{BASE}{path}?key={KEY}&{q}')
    return json.loads(urllib.request.urlopen(req, timeout=90).read().decode())


def haversine(a, b):
    import math
    R = 6371.0
    la1, lo1, la2, lo2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    return 2 * R * math.asin(math.sqrt(math.sin((la2 - la1) / 2) ** 2
                                       + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2))


# 1. all Thai gauges (paginate)
gauges, token = [], None
while True:
    body = {'regionCode': 'TH', 'pageSize': 2000}
    if token:
        body['pageToken'] = token
    d = post('/gauges:searchGaugesByArea', body)
    gauges.extend(d.get('gauges', []))
    token = d.get('nextPageToken')
    if not token:
        break
print(f'gauges in TH: {len(gauges)} (with model: {sum(1 for g in gauges if g.get("hasModel"))})')

# 2. nearest gauge per reference station (prefer qualityVerified + hasModel)
picks = {}
for name, (la, lo) in REF.items():
    cand = [g for g in gauges if g.get('hasModel')]
    cand.sort(key=lambda g: haversine((la, lo), (g['location']['latitude'], g['location']['longitude'])))
    top = cand[:3]
    picks[name] = top
    print(f'\n{name}: nearest model gauges')
    for g in top:
        d = haversine((la, lo), (g['location']['latitude'], g['location']['longitude']))
        print(f'   {g["gaugeId"]:>22}  {g["location"]["latitude"]:.3f},{g["location"]["longitude"]:.3f}'
              f'  {d:5.1f} km  src={g.get("source")} qv={g.get("qualityVerified")}'
              f'  site="{g.get("siteName","")}" river="{g.get("river","")}"')

ids = []
for v in picks.values():
    ids.extend([g['gaugeId'] for g in v])
ids = list(dict.fromkeys(ids))
print(f'\nquerying {len(ids)} gauge ids')

# 3. latest flood status
st = post('/floodStatus:searchLatestFloodStatusByArea',
          {'regionCode': 'TH', 'includeNonQualityVerified': True})
statuses = {s['gaugeId']: s for s in st.get('floodStatuses', [])}
print(f'TH flood statuses: {len(statuses)}')
sev = {}
for s in statuses.values():
    sev[s.get('severity')] = sev.get(s.get('severity'), 0) + 1
print('severity counts:', sev)

# 4. thresholds
models = {}
for i in range(0, len(ids), 100):
    chunk = ids[i:i + 100]
    d = get('/gaugeModels:batchGet', {'names': [f'gaugeModels/{g}' for g in chunk]})
    for m in d.get('gaugeModels', []):
        models[m['gaugeId']] = m

# 5. forecasts
fc = get('/gauges:queryGaugeForecasts', {'gaugeIds': ids})
forecasts = fc.get('forecasts', {})

print('\n================ per gauge ================')
report = {}
for name, top in picks.items():
    for g in top:
        gid = g['gaugeId']
        s = statuses.get(gid, {})
        m = models.get(gid, {})
        th = m.get('thresholds', {})
        f = forecasts.get(gid, {}).get('forecasts', [])
        latest = f[-1] if f else None
        row = dict(gaugeId=gid, near=name, lat=g['location']['latitude'], lon=g['location']['longitude'],
                   severity=s.get('severity'), trend=s.get('forecastTrend'),
                   qualityVerified=g.get('qualityVerified'), thresholds=th,
                   issued=latest.get('issuedTime') if latest else None)
        rng = (latest or {}).get('forecastRanges', [])
        if rng:
            vals = [(r.get('forecastStartTime'), r.get('value')) for r in rng]
            cur = vals[0][1]
            pk = max(vals, key=lambda t: (t[1] if t[1] is not None else -1))
            row['current'] = cur
            row['peak'] = pk[1]
            row['peak_time'] = pk[0]
            row['series'] = vals
        report[f'{name} | {gid}'] = row
        print(f'\n{name}\n  gauge {gid} ({g["location"]["latitude"]:.3f},{g["location"]["longitude"]:.3f})')
        print(f'  severity={s.get("severity")} trend={s.get("forecastTrend")} issued={row["issued"]}')
        print(f'  thresholds: {json.dumps(th)}')
        if rng:
            print(f'  current={row["current"]}  peak={row["peak"]} at {row["peak_time"]}  points={len(vals)}')
            for t, v in vals[:8]:
                print(f'     {t}  {v}')
        else:
            print('  no forecast returned')

json.dump({'gauges': gauges, 'statuses': statuses, 'models': models,
           'report': report}, open(f'{OUT}/c13_floodhub.json', 'w'))
print('\nsaved ' + OUT + '/c13_floodhub.json')
