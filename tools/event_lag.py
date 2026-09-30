#!/usr/bin/env python3
"""Measure water travel time between adjacent main-stem stations.

Method — rise-rate timing (not correlation).
For each station the series is resampled to hourly, then "rise events" are picked as
local maxima of the 12-hour rise rate, at least 0.10 m per 12 h and 48 h apart. For
every upstream event the matching time downstream is the strongest 12-hour rise in the
following WINDOW hours; the lag is the difference. Correlation of the raw series was
tried first and rejected: both gauges see the same basin-wide rain, so increments align
at zero lag and swamp the translation signal (see stats/notes in skills/station_network.md).

Regulated reaches are flagged, not silently mixed in: C.13 is the Chao Phraya Dam
tailrace, CPY004 the dam headpond and CPY003 the Manorom regulator, so their levels jump
with gate operations and a "travel time" into them is not a routing time.

Data: public waterlevel_graph. The endpoint 500s ("out of shared memory") on wide date
ranges or bursts, so it pulls CHUNK-day slices with retries and caches to
data/series_raw.json — re-runs reuse the cache and skip fetching.

Outputs
  data/event_lag_<YYYYMMDD>.csv   one row per matched event
  data/event_lag_<YYYYMMDD>.json  same + per-pair medians, parameters, data coverage
"""
import argparse
import csv
import datetime
import json
import os
import sys
import time
import urllib.request

API = 'https://api-v3.thaiwater.net/api/v1/thaiwater30/public/waterlevel_graph'
OLDC = 'https://api-v3.thaiwater.net/api/v1/thaiwater30/public/waterlevel_graph_oldcode'

PAIRS = [('C.2', 'CPY002'), ('CPY002', 'CPY004'), ('CPY004', 'C.13'),
         ('C.13', 'CPY005'), ('CPY005', 'CPY006'), ('CPY006', 'C.3'),
         ('C.3', 'CPY007'), ('CPY007', 'C.7A'), ('CPY008', 'CPY012'),
         ('CPY012', 'CPY014'), ('PIN002', 'PIN003'), ('PIN004', 'PIN005'),
         ('NAN007', 'NAN006'), ('NAN014', 'NAN011'), ('YOM009', 'CPY001')]

REGULATED = {
    'C.13': 'Chao Phraya Dam tailrace (gate-controlled)',
    'CPY004': 'Chao Phraya Dam headpond (backwater)',
    'CPY003': 'Manorom regulator',
    'CPY005': 'just below the dam, release-controlled',
}

RATE_WIN = 12            # h, rise-rate window defining an event
RATE_MIN = 0.15          # m per RATE_WIN to count as an event
EVENT_SEP = 72           # h between events at the same station
DOWN_MIN = 0.05          # m per RATE_WIN required downstream to accept a match
WINDOW = 36              # h searched downstream (reaches here are 10-35 km)
DAYS = 45
CHUNK = 14               # days per request

FETCH_TRIES = [3]
FETCH_PAUSE = [10]


# ---------------------------------------------------------------- fetching

def fetch_chunk(sid, start, end, tries, pause, oldcode=None):
    urls = [f'{API}?station_type=tele_waterlevel&station_id={sid}&start_date={start}&end_date={end}']
    if oldcode:
        urls.append(f'{OLDC}?station_id={oldcode}&agency_id=9&start_date={start}&end_date={end}')
    last = 'no attempt'
    for i in range(tries):
        for url in urls:
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                body = json.loads(urllib.request.urlopen(req, timeout=120).read().decode())
                data = body.get('data')
                if isinstance(data, dict):
                    rows = data.get('graph_data') or []
                    if rows:
                        return rows
                    last = 'empty'
                else:
                    last = str(data)[:60]
            except Exception as e:
                last = type(e).__name__
            time.sleep(6)
        time.sleep(pause * (i + 1))
    print(f'  chunk {start}..{end} failed: {last}', file=sys.stderr)
    return []


def fetch_series(sid, days, tries, pause, oldcode=None):
    end = datetime.date.today()
    start = end - datetime.timedelta(days=days)
    rows, seen = [], set()
    cur = start
    while cur < end:
        nxt = min(cur + datetime.timedelta(days=CHUNK), end)
        for r in fetch_chunk(sid, cur, nxt, tries, pause, oldcode):
            key = r.get('datetime')
            if key and key not in seen:
                seen.add(key)
                rows.append(r)
        cur = nxt
        time.sleep(3)
    if not rows:
        raise RuntimeError(f'{oldcode or sid}: no rows')
    return rows


def hourly(code, ids, days, cache=None):
    """-> {datetime: level}; the cache stores the hourly dict with ISO keys."""
    if cache is not None and cache.get(code):
        return {datetime.datetime.fromisoformat(k): float(v) for k, v in cache[code].items()}
    sid = ids.get(code)
    if not sid:
        return {}
    raw = fetch_series(sid, days, FETCH_TRIES[0], FETCH_PAUSE[0], oldcode=code)
    time.sleep(3)
    acc = {}
    for row in raw:
        if row.get('value') in (None, ''):
            continue
        try:
            dt = datetime.datetime.strptime(row['datetime'][:16], '%Y-%m-%d %H:%M')
            key = dt.replace(minute=0)
            acc.setdefault(key, []).append(float(row['value']))
        except Exception:
            pass
    out = {k: sum(v) / len(v) for k, v in acc.items()}
    if cache is not None:
        cache[code] = {k.isoformat(): v for k, v in out.items()}
    return out


# ---------------------------------------------------------------- analysis

def rate_events(series, win=RATE_WIN, amp=RATE_MIN, sep=EVENT_SEP):
    """Rise events: local maxima of the `win`-hour rise rate, >= amp, `sep` h apart."""
    ts = sorted(series)
    if len(ts) <= win:
        return []
    v = [series[t] for t in ts]
    cand = [(v[i] - v[i - win], ts[i]) for i in range(win, len(ts))]
    cand = [c for c in cand if c[0] >= amp]
    cand.sort(reverse=True)
    picked = []
    for r, t in cand:
        if all(abs((t - p[1]).total_seconds()) / 3600 >= sep for p in picked):
            picked.append((r, t))
    return sorted(picked, key=lambda x: x[1])


def match_pairs(up, dn, su, sd, max_lag=WINDOW, win=RATE_WIN, down_min=DOWN_MIN):
    """For each upstream event, the strongest downstream rise within max_lag hours."""
    out = []
    dgrid = sorted(sd)
    dv = [sd[t] for t in dgrid]
    for amp_u, t_u in rate_events(su, win=win):
        best = None
        for i in range(len(dgrid) - win):
            t = dgrid[i]
            if not (t_u < t <= t_u + datetime.timedelta(hours=max_lag)):
                continue
            rise = dv[i + win] - dv[i]
            if best is None or rise > best[1]:
                best = (t, rise)
        if best and best[1] >= down_min:
            lag = (best[0] - t_u).total_seconds() / 3600
            out.append({'upstream': up, 'downstream': dn,
                        'upstream_event': t_u.isoformat(), 'downstream_event': best[0].isoformat(),
                        'lag_h': round(lag, 1), 'up_rise_m': round(amp_u, 3),
                        'down_rise_m': round(best[1], 3),
                        'up_regulated': REGULATED.get(up, ''), 'down_regulated': REGULATED.get(dn, '')})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--raw-dir', default='data')
    ap.add_argument('--wl-json', default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'waterlevel_load.json'))
    ap.add_argument('--days', type=int, default=DAYS)
    ap.add_argument('--tries', type=int, default=FETCH_TRIES[0])
    ap.add_argument('--pause', type=int, default=FETCH_PAUSE[0])
    ap.add_argument('--no-fetch', action='store_true',
                    help='analyse only the cached series, do not hit the API')
    ap.add_argument('--rate-min', type=float, default=RATE_MIN)
    ap.add_argument('--window', type=int, default=WINDOW)
    a = ap.parse_args()
    FETCH_TRIES[0], FETCH_PAUSE[0] = a.tries, a.pause

    ids = {}
    try:
        wl = json.load(open(a.wl_json))
        for s in (wl.get('waterlevel_data') or {}).get('data') or []:
            st = s.get('station') or {}
            c = str(st.get('tele_station_oldcode') or '')
            if c:
                ids[c] = st.get('id')
    except Exception as e:
        print(f'warn: no station id table ({type(e).__name__}); using oldcode endpoint only',
              file=sys.stderr)

    os.makedirs(a.raw_dir, exist_ok=True)
    cache_path = os.path.join(a.raw_dir, 'series_raw.json')
    try:
        cache = json.load(open(cache_path))
        if not isinstance(cache, dict):
            cache = {}
    except Exception:
        cache = {}

    series_ok = {}
    for up, dn in PAIRS:
        for c in (up, dn):
            if c in series_ok:
                continue
            if a.no_fetch:
                series_ok[c] = len(cache.get(c) or {})
                continue
            try:
                hourly(c, ids, a.days, cache=cache)          # populates the cache
                series_ok[c] = len(cache.get(c) or {})
            except Exception as e:
                print(f'warn {c}: {str(e)[:60]}', file=sys.stderr)
                series_ok[c] = 0
            json.dump(cache, open(cache_path, 'w'), ensure_ascii=False)

    rows, per_pair = [], []
    for up, dn in PAIRS:
        su = {datetime.datetime.fromisoformat(k): float(v) for k, v in (cache.get(up) or {}).items()}
        sd = {datetime.datetime.fromisoformat(k): float(v) for k, v in (cache.get(dn) or {}).items()}
        if not su or not sd:
            continue
        m = match_pairs(up, dn, su, sd, max_lag=a.window, win=RATE_WIN)
        m = [x for x in m if x['up_rise_m'] >= a.rate_min]
        rows.extend(m)
        if m:
            lags = sorted(x['lag_h'] for x in m)
            per_pair.append({'upstream': up, 'downstream': dn, 'events': len(m),
                             'median_lag_h': lags[len(lags) // 2], 'min': lags[0], 'max': lags[-1],
                             'lags': lags,
                             'regulated': REGULATED.get(dn, '') or REGULATED.get(up, '')})

    date = datetime.date.today().strftime('%Y%m%d')
    with open(os.path.join(a.raw_dir, f'event_lag_{date}.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['upstream', 'downstream', 'upstream_event', 'downstream_event',
                                          'lag_h', 'up_rise_m', 'down_rise_m',
                                          'up_regulated', 'down_regulated'])
        w.writeheader()
        w.writerows(rows)
    json.dump({'pairs': per_pair, 'hours_of_data': series_ok,
               'params': {'rate_win_h': RATE_WIN, 'rate_min_m': RATE_MIN, 'event_sep_h': EVENT_SEP,
                          'down_min_m': DOWN_MIN, 'window_h': WINDOW, 'days': a.days,
                          'chunk_days': CHUNK},
               'method': 'rise-rate timing; dam-controlled stations flagged in REGULATED'},
              open(os.path.join(a.raw_dir, f'event_lag_{date}.json'), 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(per_pair, ensure_ascii=False))


if __name__ == '__main__':
    main()
