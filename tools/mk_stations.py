#!/usr/bin/env python3
"""Which Mae Klong (ลุ่มน้ำแม่กลอง) stations actually publish discharge / level?

Scans the node inventory for the basin, then probes each code on the thaiwater
graph endpoint for a recent 3-day window and reports which fields are populated.

Usage: mk_stations.py [family_filter]
"""
import json
import os
import sys
import time
import urllib.request

API = 'https://api-v3.thaiwater.net/api/v1/thaiwater30/public/waterlevel_graph_oldcode'
FORECAST_API = 'https://api-v3.thaiwater.net/api/v1/thaiwater30/public/waterlevel_load'
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INV = json.load(open(os.path.join(BASE, 'data', 'station_nodes.json')))


def probe(code, start='2026-09-29', end='2026-10-02'):
    url = f'{API}?station_id={code}&agency_id=12&start_date={start}&end_date={end}'
    try:
        b = json.loads(urllib.request.urlopen(
            urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=60).read().decode())
    except Exception as e:
        return ('error', type(e).__name__)
    d = b.get('data') or {}
    rows = d.get('graph_data') or []
    lv = sum(1 for r in rows if r.get('value') is not None)
    q = sum(1 for r in rows if r.get('discharge') is not None)
    return (len(rows), lv, q)


if __name__ == '__main__':
    fam = sys.argv[1] if len(sys.argv) > 1 else None
    nodes = [r for r in INV if r.get('basin') == 'ลุ่มน้ำแม่กลอง']
    nodes.sort(key=lambda r: -(r.get('lat') or 0))
    print(f'{len(nodes)} nodes in ลุ่มน้ำแม่กลอง')
    for r in nodes:
        if fam and r.get('family') != fam:
            continue
        print(f"{r['code']:<10} {r.get('family','?'):<6} {r.get('name_th','')[:34]:<34} {r.get('lat'):.4f} {r.get('lon'):.4f}  probe...", end=' ', flush=True)
        res = probe(r['code'])
        print(res, flush=True)
        time.sleep(1.5)
    print('ALL DONE', flush=True)
