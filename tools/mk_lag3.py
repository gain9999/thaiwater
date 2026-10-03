#!/usr/bin/env python3
"""Mae Klong travel-time check, take 2 — peak timing + detided increment correlation.

The lower Mae Klong is tidal (K.2B / K.57 sit in the estuarine reach), so raw level
correlation is dominated by a 23-24 h cycle. Two robust-off approaches are used here:

  A) peak timing   — time of the biggest 24 h rise and of the maximum level per station;
                     a flood peak of several metres dwarfs the tidal range, so the offset
                     between stations is a travel time.
  B) detided xcorr — subtract a 25 h centred moving average from each level series (kills
                     the diurnal + semi-diurnal tide) and cross-correlate the remaining
                     hourly increments.

Usage: mk_lag3.py
"""
import datetime
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = json.load(open(os.path.join(BASE, 'data', 'mk_cache.json')))
CODES = ['K.55A', 'RAJ002', 'RAJ001', 'K.2B', 'K.57']
CHART = {  # (upstream, downstream): (km, hours) as printed on the RID chart
    ('K.55A', 'K.2B'): (36, 6.75),
    ('K.2B', 'K.57'): (15, 2.75),
    ('K.55A', 'K.57'): (51, 9.5),
}


def series(code):
    out = {}
    for r in CACHE.get(code, []):
        v = r.get('value')
        if v is None:
            continue
        try:
            out[datetime.datetime.strptime(r['datetime'], '%Y-%m-%d %H:%M')] = float(v)
        except Exception:
            pass
    return out


def smooth(s, hours=25):
    ts = sorted(s)
    out = {}
    for i, t in enumerate(ts):
        w = [s[u] for u in ts if abs((u - t).total_seconds()) <= hours / 2 * 3600]
        out[t] = sum(w) / len(w)
    return out


def incr(s):
    ts = sorted(s)
    return {ts[i]: s[ts[i]] - s[ts[i - 1]] for i in range(1, len(ts))
            if (ts[i] - ts[i - 1]).total_seconds() <= 5400}


def xcorr(a, b, max_lag=30, minn=100):
    grid = sorted(set(a) & set(b))
    res = []
    for lag in range(0, max_lag + 1):
        xs, ys = [], []
        for t in grid:
            t2 = t + datetime.timedelta(hours=lag)
            if t in a and t2 in b:
                xs.append(a[t]); ys.append(b[t2])
        n = len(xs)
        if n < minn:
            continue
        mx, my = sum(xs) / n, sum(ys) / n
        num = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
        dx = sum((v - mx) ** 2 for v in xs) ** 0.5
        dy = sum((v - my) ** 2 for v in ys) ** 0.5
        if dx and dy:
            res.append((lag, num / (dx * dy)))
    return sorted(res, key=lambda x: -x[1])


def main():
    S = {c: series(c) for c in CODES}
    for c, s in S.items():
        print(f'{c}: {len(s)} points', flush=True)
    print('\nA) peak timing')
    for c, s in S.items():
        ts = sorted(s)
        tmax = max(ts, key=lambda t: s[t])
        # biggest 24 h rise, sampled hourly
        best = (None, -99)
        for t in ts:
            t2 = t + datetime.timedelta(hours=24)
            if t2 in s:
                r = s[t2] - s[t]
                if r > best[1]:
                    best = (t, r)
        print(f'  {c}: max level {s[tmax]:.2f} m at {tmax:%d %b %H:%M} | biggest 24h rise {best[1]:+.2f} m ending {best[0] + datetime.timedelta(hours=24):%d %b %H:%M}')

    D = {c: incr(smooth(s)) for c, s in S.items()}
    print('\nB) detided (25 h mean removed) increment cross-correlation')
    for a, b in [('K.55A', 'RAJ002'), ('K.55A', 'RAJ001'), ('K.55A', 'K.2B'), ('RAJ001', 'K.2B'),
                 ('K.2B', 'K.57'), ('K.55A', 'K.57'), ('RAJ002', 'RAJ001')]:
        res = xcorr(D[a], D[b])
        if not res:
            print(f'  {a} -> {b}: no overlap')
            continue
        line = f'  {a} -> {b}: ' + ', '.join(f'{l}h r={r:.2f}' for l, r in res[:4])
        cf = CHART.get((a, b))
        if cf:
            km, h = cf
            line += f'   [chart {km} km / {h} h]'
        print(line)


if __name__ == '__main__':
    main()
