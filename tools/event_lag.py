#!/usr/bin/env python3
"""Measure real water travel time between adjacent main-stem stations.

Method: flood-event peak/onset matching. For each station, resample the public
waterlevel_graph series to hourly, smooth it, and find "rise onsets" (level rises
>= THRESH above its trailing 24-h minimum, with a cool-down so one flood counts
once). For each upstream onset, the matching downstream onset is the first one in
the following window; ambiguous matches are dropped. The lag is the time the rise
took to reach the next gauge.

Outputs
  data/event_lag_<YYYYMMDD>.csv   one row per event match
  data/event_lag_<YYYYMMDD>.json  same + per-pair medians
  (medians are folded back into skills/station_network.md by hand/§8)
"""
import argparse
import csv
import datetime
import json
import os
import sys
import time
import urllib.request
from collections import defaultdict

API = 'https://api-v3.thaiwater.net/api/v1/thaiwater30/public/waterlevel_graph'
PAIRS = [('C.2', 'CPY002'), ('CPY002', 'CPY004'), ('CPY004', 'C.13'),
         ('C.13', 'CPY005'), ('CPY005', 'CPY006'), ('CPY006', 'C.3'),
         ('C.3', 'CPY007'), ('CPY007', 'C.7A'), ('CPY008', 'CPY012'),
         ('CPY012', 'CPY014'), ('PIN002', 'PIN003'), ('PIN004', 'PIN005'),
         ('NAN007', 'NAN006'), ('NAN014', 'NAN011'), ('YOM009', 'CPY001')]
THRESH = 0.20            # m above the trailing 24-h minimum
COOLDOWN = 48            # h between onsets at the same station
WINDOW = 96              # max lag searched, h
DAYS = 60
FETCH_TRIES = [4]
FETCH_PAUSE = [12]


def fetch_series(sid, days, tries=4, pause=12, oldcode=None):
    end = datetime.date.today()
    start = end - datetime.timedelta(days=days)
    urls = [f'{API}?station_type=tele_waterlevel&station_id={sid}'
            f'&start_date={start}&end_date={end}']
    if oldcode:
        urls.append('https://api-v3.thaiwater.net/api/v1/thaiwater30/public/'
                    f'waterlevel_graph_oldcode?station_id={oldcode}&agency_id=9'
                    f'&start_date={start}&end_date={end}')
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
                    last = str(data)[:80]
            except Exception as e:
                last = type(e).__name__
            time.sleep(6)
        time.sleep(pause * (i + 1))
    raise RuntimeError(f'{oldcode or sid}: {last}')


def hourly(code, ids, days=DAYS, cache=None):
    """-> {datetime: level}, hour-resampled; cache persists the hourly dict as ISO keys."""
    if cache is not None and cache.get(code):
        return {datetime.datetime.fromisoformat(k): float(v) for k, v in cache[code].items()}
    sid = ids.get(code)
    if not sid:
        return {}
    raw = fetch_series(sid, days, tries=FETCH_TRIES[0], pause=FETCH_PAUSE[0], oldcode=code)
    time.sleep(3)
    acc = defaultdict(list)
    for row in raw:
        if row.get('value') in (None, ''):
            continue
        try:
            dt = datetime.datetime.strptime(row['datetime'][:16], '%Y-%m-%d %H:%M')
            acc[dt.replace(minute=0)].append(float(row['value']))
        except Exception:
            pass
    out = {k: sum(v) / len(v) for k, v in acc.items()}
    if cache is not None:
        cache[code] = {k.isoformat(): v for k, v in out.items()}
    return out


def onsets(series):
    """-> list of (datetime, level) rise onsets."""
    ts = sorted(series)
    if len(ts) < 48:
        return []
    vals = [series[t] for t in ts]
    sm = []
    for i in range(len(vals)):
        w = vals[max(0, i-1):i+2]
        sm.append(sum(w) / len(w))
    out = []
    for i in range(len(ts)):
        lo = min(sm[max(0, i-24):i+1])
        rise = sm[i] - lo
        prev = (sm[i-1] - min(sm[max(0, i-25):i])) if i else -1
        if rise >= THRESH and prev < THRESH:
            if out and (ts[i] - out[-1][0]).total_seconds() / 3600 < COOLDOWN:
                continue
            out.append((ts[i], sm[i]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--raw-dir', default='data')
    ap.add_argument('--wl-json', default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'waterlevel_load.json'))
    ap.add_argument('--days', type=int, default=DAYS)
    ap.add_argument('--tries', type=int, default=4)
    ap.add_argument('--pause', type=int, default=12)
    a = ap.parse_args()
    FETCH_TRIES[0] = a.tries
    FETCH_PAUSE[0] = a.pause
    wl = json.load(open(a.wl_json))
    ids = {}
    for s in (wl.get('waterlevel_data') or {}).get('data') or []:
        st = s.get('station') or {}
        c = str(st.get('tele_station_oldcode') or '')
        if c:
            ids[c] = st.get('id')

    scache_path = os.path.join(a.raw_dir, 'series_raw.json')
    try:
        scache = json.load(open(scache_path))
        if not isinstance(scache, dict):
            scache = {}
    except Exception:
        scache = {}
    series_ok = {}
    for up, dn in PAIRS:
        for c in (up, dn):
            if c in series_ok:
                continue
            try:
                s = hourly(c, ids, days=a.days, cache=scache)
                series_ok[c] = len(s)
            except Exception as e:
                print(f'warn {c}: {str(e)[:60]}', file=sys.stderr)
                series_ok[c] = 0
            json.dump(scache, open(scache_path, 'w'), ensure_ascii=False)
    cache = scache
    on = {c: onsets(cache[c]) for c in cache}

    date = datetime.date.today().strftime('%Y%m%d')
    os.makedirs(a.raw_dir, exist_ok=True)
    rows, per_pair = [], []
    for up, dn in PAIRS:
        ou, od = on.get(up, []), on.get(dn, [])
        matches = []
        for t_u, v_u in ou:
            later = [(t, v) for t, v in od if t > t_u and (t - t_u).total_seconds() / 3600 <= WINDOW]
            if not later:
                continue
            t_d = later[0][0]
            if any(t_u < t2 < t_d for t2, _ in ou):        # ambiguous: another upstream flood in between
                continue
            lag = (t_d - t_u).total_seconds() / 3600
            matches.append((t_u, lag, v_u, later[0][1]))
        for t_u, lag, v_u, v_d in matches:
            rows.append({'upstream': up, 'downstream': dn, 'upstream_onset': t_u.isoformat(),
                         'lag_h': round(lag, 1), 'up_level': round(v_u, 3), 'down_level': round(v_d, 3)})
        if matches:
            lags = sorted(m[1] for m in matches)
            med = lags[len(lags) // 2]
            per_pair.append({'upstream': up, 'downstream': dn, 'events': len(matches),
                             'median_lag_h': round(med, 1), 'min': lags[0], 'max': lags[-1],
                             'lags': [round(x, 1) for x in lags]})

    with open(os.path.join(a.raw_dir, f'event_lag_{date}.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['upstream', 'downstream', 'upstream_onset', 'lag_h',
                                          'up_level', 'down_level'])
        w.writeheader()
        w.writerows(rows)
    json.dump({'pairs': per_pair, 'hours_of_data': series_ok,
               'params': {'thresh_m': THRESH, 'cooldown_h': COOLDOWN, 'window_h': WINDOW, 'days': DAYS}},
              open(os.path.join(a.raw_dir, f'event_lag_{date}.json'), 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(per_pair, ensure_ascii=False))


if __name__ == '__main__':
    main()
