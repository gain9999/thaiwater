#!/usr/bin/env python3
"""Travel time along the lower Mae Klong (chart: เขื่อนแม่กลอง -> K.55A -> K.56 -> K.2B -> K.57).

Same idea as q_lag.py (cross-correlate hourly discharge increments), applied to the
K. station chain printed on the RID Mae Klong schematic. Writes data/mk_cache.json.

Usage: mk_lag.py [days] [max_lag_h]
"""
import datetime
import json
import os
import sys
import time
import urllib.request

API = 'https://api-v3.thaiwater.net/api/v1/thaiwater30/public/waterlevel_graph_oldcode'
CODES = ['K.55A', 'K.56', 'K.2B', 'K.57']
EXTRA = ['RAJ001', 'RAJ002']
PAIRS = [('K.55A', 'K.56'), ('K.56', 'K.2B'), ('K.2B', 'K.57'), ('K.55A', 'K.2B'), ('K.55A', 'K.57'),
         ('RAJ002', 'RAJ001'), ('RAJ001', 'K.2B')]
# chart's printed figures: (river km, hours)
CHART = {('K.55A', 'K.56'): (13, 2.5), ('K.56', 'K.2B'): (23, 4.25), ('K.2B', 'K.57'): (15, 2.75),
         ('K.55A', 'K.2B'): (36, 6.75), ('K.55A', 'K.57'): (51, 9.5)}
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'mk_cache.json')


def fetch(code, start, end, tries=3, pause=6):
    url = f'{API}?station_id={code}&agency_id=12&start_date={start}&end_date={end}'
    last = ''
    for i in range(tries):
        try:
            b = json.loads(urllib.request.urlopen(
                urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=90).read().decode())
            d = b.get('data')
            if isinstance(d, dict):
                return d.get('graph_data') or []
            last = str(d)[:60]
        except Exception as e:
            last = type(e).__name__
        time.sleep(pause * (i + 1))
    print(f'  {code} {start}..{end} failed: {last}', file=sys.stderr)
    return []


def series(code, days=20, slice_days=10):
    try:
        cache = json.load(open(OUT))
    except Exception:
        cache = {}
    end = datetime.date.today()
    start = end - datetime.timedelta(days=days)
    got, rowmap = {}, {}
    for r in cache.get(code, []):
        key = r.get('datetime')
        if not key:
            continue
        rowmap[key] = r
        if r.get('discharge') is not None:
            got[key] = r['discharge']
    cur = start
    while cur < end:
        nxt = min(cur + datetime.timedelta(days=slice_days), end)
        rows = fetch(code, cur, nxt)
        print(f'  {code} {cur}..{nxt}: {len(rows)} rows', flush=True)
        for r in rows:
            key = r.get('datetime')
            if key:
                rowmap[key] = r
                if r.get('discharge') is not None:
                    got[key] = r['discharge']
        cur = nxt
        time.sleep(3)
    cache[code] = [rowmap[k] for k in sorted(rowmap)]
    json.dump(cache, open(OUT, 'w'), ensure_ascii=False)
    return {datetime.datetime.strptime(k, '%Y-%m-%d %H:%M'): float(v) for k, v in got.items()}


def dq(s, smooth=3):
    ts = sorted(s)
    if len(ts) < 30:
        return {}
    vals = [s[t] for t in ts]
    out = {}
    for i in range(1, len(ts)):
        if (ts[i] - ts[i - 1]).total_seconds() > 5400:
            continue
        out[ts[i]] = vals[i] - vals[i - 1]
    keys = sorted(out)
    sm = {}
    for i, k in enumerate(keys):
        w = [out[keys[j]] for j in range(max(0, i - smooth // 2), min(len(keys), i + smooth // 2 + 1))]
        sm[k] = sum(w) / len(w)
    return sm


def xcorr(a, b, max_lag=48):
    grid = sorted(set(a) & set(b))
    if len(grid) < 100:
        grid = sorted(a)
    best = None
    curve = []
    for lag in range(0, max_lag + 1):
        xs, ys = [], []
        for t in grid:
            t2 = t + datetime.timedelta(hours=lag)
            if t in a and t2 in b:
                xs.append(a[t]); ys.append(b[t2])
        n = len(xs)
        if n < 60:
            continue
        mx, my = sum(xs) / n, sum(ys) / n
        num = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
        dx = sum((v - mx) ** 2 for v in xs) ** 0.5
        dy = sum((v - my) ** 2 for v in ys) ** 0.5
        if dx and dy:
            r = num / (dx * dy)
            curve.append((lag, r))
            if best is None or r > best[1]:
                best = (lag, r)
    return best, curve


if __name__ == '__main__':
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    maxlag = int(sys.argv[2]) if len(sys.argv) > 2 else 48
    S = {}
    for c in CODES + EXTRA:
        print(f'{c}: fetching', flush=True)
        s = series(c, days=days)
        span = f'{min(s):%Y-%m-%d %H:%M} .. {max(s):%Y-%m-%d %H:%M}' if s else '-'
        print(f'{c}: {len(s)} hourly Q points, {span}', flush=True)
        S[c] = s
    D = {c: dq(s) for c, s in S.items()}
    print('\n== cross-correlation of hourly dQ/dt ==', flush=True)
    for a, b in PAIRS:
        if not D.get(a) or not D.get(b):
            print(f'{a} -> {b}: no data', flush=True)
            continue
        best, curve = xcorr(D[a], D[b], max_lag=maxlag)
        top = sorted(curve, key=lambda x: -x[1])[:4]
        cf = CHART.get((a, b))
        line = (f'{a} -> {b}: best lag {best[0]} h (r={best[1]:.2f})' if best else f'{a} -> {b}: n/a')
        if cf:
            km, h = cf
            line += f' | chart {km} km / {h} h ({km / h:.1f} km/h)'
            if best:
                line += f' | measured {km / max(best[0], 1):.1f} km/h'
        line += ' | top-r lags: ' + ', '.join(f'{l}h r={r:.2f}' for l, r in top)
        print(line, flush=True)
    print('ALL DONE', flush=True)
