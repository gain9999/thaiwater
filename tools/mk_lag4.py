#!/usr/bin/env python3
"""Top-leg check of the Mae Klong chart: เขื่อนแม่กลอง -> K.55A.

K.11A (บ้านวังขนาย, at the dam tailrace) and K.55A both publish hourly discharge, so the
release-step method used on the Chao Phraya applies directly here.

Chart (RID ราชบุรี chart): dam -> K.55A = 45 km, 8 h.
Straight line K.11A -> K.55A = 29.3 km, so the chart's river distance implies a meander
factor ~1.4 (dam sits ~3 km upstream of K.11A).

Usage: mk_lag4.py
"""
import datetime
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = json.load(open(os.path.join(BASE, 'data', 'mk_cache.json')))


def series(code, field='discharge'):
    out = {}
    for r in CACHE.get(code, []):
        v = r.get(field)
        if v is None:
            continue
        try:
            out[datetime.datetime.strptime(r['datetime'], '%Y-%m-%d %H:%M')] = float(v)
        except Exception:
            pass
    return out


def incr(s):
    ts = sorted(s)
    return {ts[i]: s[ts[i]] - s[ts[i - 1]] for i in range(1, len(ts))
            if (ts[i] - ts[i - 1]).total_seconds() <= 5400}


def xcorr(a, b, max_lag=48, minn=100):
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


if __name__ == '__main__':
    for c in ['K.11A', 'K.55A', 'K.2B']:
        q = series(c, 'discharge')
        print(f'{c}: {len(q)} hourly Q points')
    A, B = series('K.11A'), series('K.55A')
    if A and B:
        res = xcorr(incr(A), incr(B))
        print('\nK.11A -> K.55A  (discharge increments)')
        print('  top lags: ' + ', '.join(f'{l}h r={r:.2f}' for l, r in res[:6]))
        # around zero and the middle range
        for lo, hi, tag in [(0, 24, '0-24 h'), (24, 49, '24-48 h')]:
            sub = [x for x in res if lo <= x[0] <= hi]
            if sub:
                best = sub[0]
                print(f'  best inside {tag}: {best[0]}h r={best[1]:.2f}')
        # step events: biggest hourly jumps upstream and the matching downstream reaction
        iA, iB = incr(A), incr(B)
        top = sorted(iA.items(), key=lambda kv: -abs(kv[1]))[:5]
        print('\n  five largest hourly |dQ| at K.11A:')
        for t, d in top:
            print(f'    {t:%d %b %H:%M} dQ={d:+.0f} m3/s; K.55A dQ at +0/+4/+6/+8 h: '
                  + ', '.join(f'{iB.get(t + datetime.timedelta(hours=h), float("nan")):+.0f}' for h in (0, 4, 6, 8)))
