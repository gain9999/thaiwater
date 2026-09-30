#!/usr/bin/env python3
"""Travel time from DISCHARGE (gate-step routing).

Idea: a change in release/diversion shows up as a sharp step in Q. Unlike water level,
which every gauge sees rise at once when it rains, a step has a distinctive shape that
propagates downstream with a time offset -- so cross-correlating dQ/dt between two
stations on the same reach gives the translation time without rainfall ambiguity.

Source: waterlevel_graph_oldcode?station_id=<CODE>&agency_id=12 (RID discharge, hourly),
pulled in 10-day slices because the API 500s on wide windows.
"""
import datetime
import json
import os
import sys
import time
import urllib.request

API = 'https://api-v3.thaiwater.net/api/v1/thaiwater30/public/waterlevel_graph_oldcode'
CODES = ['C.2', 'C.13', 'C.3', 'C.7A', 'C.35', 'C.36', 'C.2A']
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'discharge_cache.json')


def fetch(code, start, end, tries=3, pause=8):
    url = f'{API}?station_id={code}&agency_id=12&start_date={start}&end_date={end}'
    last = ''
    for i in range(tries):
        try:
            b = json.loads(urllib.request.urlopen(
                urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=90).read().decode())
            d = b.get('data')
            if isinstance(d, dict):
                return d.get('graph_data') or []
            last = str(d)[:50]
        except Exception as e:
            last = type(e).__name__
        time.sleep(pause * (i + 1))
    print(f'  {code} {start}..{end} failed: {last}', file=sys.stderr)
    return []


def series(code, days=60, slice_days=10):
    try:
        cache = json.load(open(OUT))
    except Exception:
        cache = {}
    end = datetime.date.today()
    start = end - datetime.timedelta(days=days)
    got = {r['datetime']: r.get('discharge') for r in cache.get(code, []) if r.get('discharge') is not None}
    rowmap = {r['datetime']: r for r in cache.get(code, [])}
    cur = start
    while cur < end:
        nxt = min(cur + datetime.timedelta(days=slice_days), end)
        for r in fetch(code, cur, nxt):
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
    """Hourly increments, lightly smoothed."""
    ts = sorted(s)
    if len(ts) < 30:
        return {}
    vals = [s[t] for t in ts]
    out = {}
    for i in range(1, len(ts)):
        # require a 1-h step (skip gaps)
        if (ts[i] - ts[i - 1]).total_seconds() > 5400:
            continue
        out[ts[i]] = vals[i] - vals[i - 1]
    if smooth > 1:
        keys = sorted(out)
        sm = {}
        for i, k in enumerate(keys):
            w = [out[keys[j]] for j in range(max(0, i - smooth // 2), min(len(keys), i + smooth // 2 + 1))]
            sm[k] = sum(w) / len(w)
        return sm
    return out


def xcorr(a, b, max_lag=48):
    """Lag of b behind a from the correlation of their increment series."""
    grid = sorted(set(a) & set(b))
    if len(grid) < 100:
        grid = sorted(a)
    best = None
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
            if best is None or r > best[1]:
                best = (lag, r)
    return best


if __name__ == '__main__':
    S = {}
    for c in CODES:
        s = series(c)
        S[c] = s
        print(f'{c:6} hourly discharge points: {len(s)}', file=sys.stderr)
    D = {c: dq(s) for c, s in S.items()}
    pairs = [('C.2', 'C.13'), ('C.13', 'C.3'), ('C.3', 'C.7A'), ('C.7A', 'C.35'),
             ('C.7A', 'C.36'), ('C.35', 'C.36'), ('C.2', 'C.3')]
    for up, dn in pairs:
        if not S.get(up) or not S.get(dn):
            continue
        q = xcorr(dq(S[up]), dq(S[dn]), 48)
        lvl = xcorr(dq(S[up]), dq(S[dn]), 48)
        print(f'{up:6}->{dn:6}  dQ lag {q[0] if q else "-"} h  r {round(q[1],3) if q else "-"}   '
              f'(samples {len(S[up])}/{len(S[dn])})')
