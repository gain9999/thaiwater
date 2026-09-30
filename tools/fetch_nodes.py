#!/usr/bin/env python3
"""Build a merged river-node inventory for the Chao Phraya basin system.

Sources
  waterlevel_load   (public API, key-free)  : live water-level gauges, nationwide
  watergate_load?basin_code=6..26           : gates / regulators / dams (HII)
  full chart page node list (2013 chaopraya.php, downloaded HTML)
  brief chart SVG node list (waterchart.thaiwater.net assets)

Outputs
  data/watergate_load.json   raw cache, one key per basin_code
  data/waterlevel_load.json  raw cache
  data/station_nodes.csv     merged inventory (one row per station code)
  data/station_nodes.json    same, with the raw records kept

Usage: python3 tools/fetch_nodes.py [--raw-dir data]
"""
import argparse
import csv
import json
import os
import re
import urllib.request

API = 'https://api-v3.thaiwater.net/api/v1/thaiwater30/public/'
BASINS = list(range(6, 27))          # Ping .. Bang Pakong system (brief chart's range)


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return json.loads(urllib.request.urlopen(req, timeout=90).read().decode())


def norm(code):
    return re.sub(r'[.\-/]', '', str(code or '')).upper()


def family(code):
    c = str(code)
    if re.match(r'^C\.?\d', c) or re.match(r'^[PNYWSKRC]\.', c):
        return 'RID'
    if c.startswith(('CPY', 'PIN', 'NAN', 'YOM', 'PAS', 'THA', 'TCP', 'BKC', 'CHM', 'WAN',
                     'KWN', 'NYK', 'BPK', 'SKG', 'LBI', 'S26', 'YOM')):
        return 'HII'
    if c.startswith(('BBD', 'SKD', 'MKVKD', 'RAJ')):
        return 'EGAT'
    if c.startswith('DAM-') or c.startswith('m-dam'):
        return 'dam'
    if c.startswith('REG-'):
        return 'regulator'
    return 'canal/other'


def th(node, key):
    v = (node or {}).get(key)
    if isinstance(v, dict):
        return v.get('th') or v.get('en') or ''
    return v or ''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--raw-dir', default='data')
    ap.add_argument('--chart-html', default='/home/droid/wcheck/hii_chaophraya.html')
    ap.add_argument('--brief-svg', default='/home/droid/wcheck/cp.svg')
    a = ap.parse_args()
    os.makedirs(a.raw_dir, exist_ok=True)

    nodes = {}

    def rec(code):
        return nodes.setdefault(norm(code), {'code': code, 'family': family(code),
                                             'name_th': '', 'agency': '', 'lat': '', 'lon': '',
                                             'basin': '', 'wl': 0, 'gate': 0,
                                             'full_chart': 0, 'brief_chart': 0})

    # ---- 1. waterlevel_load (national)
    wl = fetch(API + 'waterlevel_load')
    json.dump(wl, open(os.path.join(a.raw_dir, 'waterlevel_load.json'), 'w'), ensure_ascii=False)
    wl_rows = (wl.get('waterlevel_data') or {}).get('data') or []
    for s in wl_rows:
        st = s.get('station') or {}
        c = st.get('tele_station_oldcode')
        if not c:
            continue
        r = rec(c)
        r['wl'] = 1
        r['name_th'] = r['name_th'] or th(st, 'tele_station_name')
        r['agency'] = r['agency'] or th(s.get('agency'), 'agency_shortname')
        r['lat'] = r['lat'] or (st.get('tele_station_lat') or '')
        r['lon'] = r['lon'] or (st.get('tele_station_long') or '')
        r['basin'] = r['basin'] or th(s.get('basin'), 'basin_name')

    # ---- 2. watergate_load, basins 6-26
    gates = {}
    for b in BASINS:
        try:
            j = fetch(API + f'watergate_load?basin_code={b}')
        except Exception as e:                       # keep going; note the gap
            gates[str(b)] = {'error': type(e).__name__}
            continue
        gates[str(b)] = j
        for row in ((j.get('watergate_data') or {}).get('data') or []):
            st = row.get('station') or {}
            c = st.get('tele_station_oldcode')
            if not c:
                continue
            r = rec(c)
            r['gate'] = 1
            r['name_th'] = r['name_th'] or th(st, 'tele_station_name')
            r['agency'] = r['agency'] or th(row.get('agency'), 'agency_shortname')
            r['lat'] = r['lat'] or (st.get('tele_station_lat') or '')
            r['lon'] = r['lon'] or (st.get('tele_station_long') or '')
            r['basin'] = r['basin'] or th(row.get('basin'), 'basin_name')
    json.dump(gates, open(os.path.join(a.raw_dir, 'watergate_load.json'), 'w'), ensure_ascii=False)

    # ---- 3. chart node lists
    full = []
    try:
        H = open(a.chart_html, encoding='utf-8', errors='replace').read()
        for m in re.finditer(r'<div id="([^"]+)"></div>', H):
            n = m.group(1)
            if n.startswith(('WARN', 'CCTV')) or n in full:
                continue
            full.append(n)
    except OSError:
        pass
    for c in full:
        r = rec(c)
        r['full_chart'] = 1
    brief = []
    try:
        S = open(a.brief_svg, encoding='utf-8', errors='replace').read()
        brief = sorted({m.group(1) for m in re.finditer(
            r'id="([A-Za-z][\w.\-]*?)(?:-title|-line|-box|-icon|-wl|-cms|-discharge|-wl-in|-wl-out|-path)"', S)})
    except OSError:
        pass
    for c in brief:
        r = rec(c)
        r['brief_chart'] = 1

    # ---- 4. write out
    rows = sorted(nodes.values(), key=lambda r: (r['family'], str(r['code'])))
    fields = ['code', 'family', 'name_th', 'agency', 'basin', 'lat', 'lon',
              'wl', 'gate', 'full_chart', 'brief_chart']
    with open(os.path.join(a.raw_dir, 'station_nodes.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, '') for k in fields})
    json.dump(rows, open(os.path.join(a.raw_dir, 'station_nodes.json'), 'w'), ensure_ascii=False, indent=1)

    def cnt(pred):
        return sum(1 for r in rows if pred(r))

    summary = {
        'nodes_total': len(rows),
        'with_wl': cnt(lambda r: r['wl']),
        'with_gate': cnt(lambda r: r['gate']),
        'on_full_chart': cnt(lambda r: r['full_chart']),
        'on_brief_chart': cnt(lambda r: r['brief_chart']),
        'drawing_only': cnt(lambda r: r['full_chart'] and not r['wl'] and not r['gate']),
        'gates_by_basin_type': {t: cnt(lambda r, t=t: r['gate'] and r['family'] == t)
                                for t in ('dam', 'regulator', 'canal/other', 'HII', 'RID', 'EGAT')},
        'basins_fetched': len([k for k, v in gates.items() if 'error' not in v]),
        'basins_failed': [k for k, v in gates.items() if 'error' in v],
    }
    json.dump(summary, open(os.path.join(a.raw_dir, 'node_summary.json'), 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()
