#!/usr/bin/env python3
"""Snap waterchart.thaiwater.net SVG station attach-points onto the drawn river
polylines and print the chart's own downstream order."""
import json, math, re
import importlib.util

spec = importlib.util.spec_from_file_location('svgnet', '/home/droid/wcheck/svgnet.py')
sn = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sn)  # module-level main() is guarded

import xml.etree.ElementTree as ET
NS = '{http://www.w3.org/2000/svg}'

paths = json.load(open('/home/droid/wcheck/svg_paths.json'))
leaders = json.load(open('/home/droid/wcheck/svg_leaders.json'))

root = ET.parse('/home/droid/wcheck/cp.svg').getroot()
boxes = {}
for el in root.iter():
    eid = el.get('id') or ''
    if eid.endswith('-box') and el.get('d'):
        pts = sn.path_to_poly(el.get('d'))
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        boxes[eid[:-4]] = (min(xs), min(ys), max(xs), max(ys))

attach = {}
for code, ends in leaders.items():
    box = boxes.get(code)
    if not box:
        continue
    cx, cy = (box[0]+box[2])/2, (box[1]+box[3])/2
    best = max(ends, key=lambda p: math.dist(p, (cx, cy)))
    attach[code] = best

river = [(pid, pts) for pid, pts, grp in paths if grp and grp[0] == 'River_line']
green = [(pid, pts) for pid, pts, grp in paths if grp and grp[0] == 'Green_line']
print(f'river polylines: {len(river)}  green-line polylines: {len(green)}  stations with attach point: {len(attach)}')

def report(polys, label, codes=None, min_stations=2):
    print(f'\n=== snapping to {label} ===')
    rows = []
    for code, p in attach.items():
        if codes and code not in codes:
            continue
        best = (1e9, -1, 0.0, None)
        for idx, (pid, pts) in enumerate(polys):
            d, arc = sn.snap(pts, p)
            if d < best[0]:
                best = (d, idx, arc, pts)
        rows.append((best[1], best[2], code, round(best[0], 1), p, best[3]))
    from collections import defaultdict
    byp = defaultdict(list)
    info = {}
    for idx, arc, code, d, p, pts in rows:
        byp[idx].append((arc, code, d, p))
        info[idx] = (len(pts), sn.plen(pts), pts[0], pts[-1])
    print('path#  npts   length   start->end        stations')
    for idx, items in sorted(byp.items(), key=lambda kv: -len(kv[1])):
        n, L, s, e = info[idx]
        print(f'  #{idx:<4} {n:<6} {L:7.0f}  ({s[0]:.0f},{s[1]:.0f})->({e[0]:.0f},{e[1]:.0f})  {len(items)} stations')
    for idx, items in sorted(byp.items(), key=lambda kv: -len(kv[1])):
        items.sort()
        if len(items) < min_stations:
            continue
        print(f'\n-- path #{idx}  ({len(items)} stations, drawn order along polyline)')
        for arc, code, d, p in items:
            print(f'   arc={arc:7.1f}  snap={d:6.1f}px  {code:9} at ({p[0]:.0f},{p[1]:.0f})')

report(river, 'River_line (main river paths)')
