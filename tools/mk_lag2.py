#!/usr/bin/env python3
"""Level-based lag check for the lower Mae Klong chart chain (K.55A -> K.2B -> K.57).

Only K.55A publishes discharge on this API; K.2B/K.57 publish water level only, so this
uses hourly level increments. Level correlation is known to be weak when both gauges see
the same rain, so the result is reported together with r and with a rise-event estimate.

Usage: mk_lag2.py
"""
import datetime
import json
import os
import sys

CACHE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'mk_cache.json')
PAIRS = [('K.55A', 'K.2B', 36, 6.75), ('K.2B', 'K.57', 15, 2.75), ('K.55A', 'K.57', 51, 9.5)]
cache = json.load(open(CACHE))


def series(code, field='value'):
    out = {}
    for r in cache.get(code, []):
        v = r.get(field)
        if v is None:
            continue
        try:
            out[datetime.datetime.strptime(r['datetime'], '%Y-%m-%d %H:%M')] = float(v)
        except Exception:
            pass
    return out


def diffs(s):
    ts = sorted(s)
    d = {}
    for i in range(1, len(ts)):
        if (ts[i] - ts[i - 1]).total_seconds() > 5400:
            continue
        d[ts[i]] = s[ts[i]] - s[ts[i - 1]]
    return d


def xcorr(a, b, max_lag=30):
    grid = sorted(set(a) & set(b))
    res = []
    for lag in range(0, max_lag + 1):
        xs, ys = [], []
        for t in grid:
            t2 = t + datetime.timedelta(hours=lag)
            if t in a and t2 in b:
                xs.append(a[t]); ys.append(b[t2])
        n = len(xs)
        if n < 100:
            continue
        mx, my = sum(xs) / n, sum(ys) / n
        num = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
        dx = sum((v - mx) ** 2 for v in xs) ** 0.5
        dy = sum((v - my) ** 2 for v in ys) ** 0.5
        if dx and dy:
            res.append((lag, num / (dx * dy)))
    return sorted(res, key=lambda x: -x[1])


def rise_event(sa, sb):
    """Timing of the strongest 12 h rise in each series (same basin event)."""
    def peak(s):
        ts = sorted(s)
        best = None
        for i in range(len(ts)):
            t0 = ts[i]
            t1 = t0 + datetime.timedelta(hours=12)
            # nearest sample at t1
            cand = [t for t in ts if abs((t - t1).total_seconds()) < 1800]
            if not cand:
                continue
            rise = s[cand[0]] - s[t0]
            if best is None or rise > best[1]:
                best = (t0, rise)
        return best
    return peak(sa), peak(sb)


if __name__ == '__main__':
    S = {c: series(c) for c in ['K.55A', 'K.2B', 'K.57']}
    for c, s in S.items():
        print(f'{c}: {len(s)} level points {min(s):%d %b %H:%M} .. {max(s):%d %b %H:%M}', flush=True)
    D = {c: diffs(s) for c, s in S.items()}
    for a, b, km, h in PAIRS:
        res = xcorr(D[a], D[b])
        top = ', '.join(f'{l}h r={r:.2f}' for l, r in res[:5])
        (ta, ra), (tb, rb) = rise_event(S[a], S[b])
        print(f'\n{a} -> {b}  ({km} km, chart {h} h = {km/h:.1f} km/h)')
        print(f'  dLevel xcorr top lags: {top}')
        print(f'  strongest 12h rise: {a} at {ta:%d %b %H:%M} (+{ra:.2f} m), {b} at {tb:%d %b %H:%M} (+{rb:.2f} m)'
              f' -> offset {(tb-ta).total_seconds()/3600:.1f} h')
