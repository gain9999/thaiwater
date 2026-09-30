#!/usr/bin/env python3
"""Extract water travel times from the brief chart SVG, and check node coverage
of each of Gain's two chart links against the telemetry payload."""
import json, math, os, re, importlib.util
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.environ.get('THAIWATER_RAW', os.path.join(os.path.dirname(HERE), 'data', 'raw'))
spec = importlib.util.spec_from_file_location('svgnet', os.path.join(HERE, 'svgnet.py'))
sn = importlib.util.module_from_spec(spec); spec.loader.exec_module(sn)
XMLNS = '{http://www.w3.org/2000/svg}'

SVG_PATH = os.path.join(RAW, 'cp.svg')
svg = open(SVG_PATH, encoding='utf-8', errors='replace').read()
root = ET.parse(SVG_PATH).getroot()
paths = json.load(open(os.path.join(RAW, 'svg_paths.json')))
leaders = json.load(open(os.path.join(RAW, 'svg_leaders.json')))

# ---- 1. travel-time labels (text nodes with a matrix translate)
TIME = re.compile(r'^\s*(\d+(?:\.\d+)?)\s*(ชม\.?|ชั่วโมง|วัน)\s*$')
travel = []
for el in root.iter():
    if el.tag.replace(XMLNS, '') != 'text':
        continue
    txt = re.sub(r'\s+', ' ', ''.join(el.itertext())).strip()
    m = TIME.match(txt)
    if not m:
        continue
    tr = el.get('transform') or ''
    mm = re.search(r'matrix\(1 0 0 1 ([-.\d]+) ([-.\d]+)\)', tr)
    if not mm:
        continue
    travel.append((float(mm.group(1)), float(mm.group(2)), txt))
print(f'travel-time labels found in brief-chart SVG: {len(travel)}')

# ---- 2. station attach points (leader far end from box)
boxes = {}
for el in root.iter():
    eid = el.get('id') or ''
    if eid.endswith('-box') and el.get('d'):
        pts = sn.path_to_poly(el.get('d'))
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        boxes[eid[:-4]] = (min(xs), min(ys), max(xs), max(ys))
attach = {}
for code, ends in leaders.items():
    b = boxes.get(code)
    if not b:
        continue
    attach[code] = max(ends, key=lambda p: math.dist(p, ((b[0]+b[2])/2, (b[1]+b[3])/2)))

polys = [(i, pid, pts, grp[0] if grp else '') for i, (pid, pts, grp) in enumerate(paths)]

def best_fit(p, groups=('River_line',)):
    best = (1e9, None, 0.0)
    for i, pid, pts, g in polys:
        if groups and g not in groups:
            continue
        d, arc = sn.snap(pts, p)
        if d < best[0]:
            best = (d, i, arc)
    return best

# station arcs per path
from collections import defaultdict
arcs = defaultdict(list)
for code, p in attach.items():
    d, idx, arc = best_fit(p)
    if idx is not None and d < 40:
        arcs[idx].append((arc, code, d))
for idx in arcs:
    arcs[idx].sort()

print('\nlabel                    path#  arc   snap  bracketing stations (upstream -> downstream)')
for x, y, txt in sorted(travel, key=lambda t: t[1]):
    d, idx, arc = best_fit((x, y))
    if idx is None:
        continue
    near = arcs.get(idx, [])
    up = [s for s in near if s[0] <= arc]
    dn = [s for s in near if s[0] > arc]
    u = up[-1][1] if up else '-'
    v = dn[0][1] if dn else '-'
    print(f'{txt:24} #{idx:<4} {arc:6.1f} {d:5.1f}  {u} -> {v}   at ({x:.0f},{y:.0f})')

# ---- 3. coverage of the two chart links
def norm(c):
    return re.sub(r'[.\-]', '', c).upper()

full = []
for m in re.finditer(r'<div id="([^"]+)"></div>', open(os.path.join(RAW, 'hii_chaophraya.html'), encoding='utf-8', errors='replace').read()):
    n = m.group(1)
    if n.startswith(('WARN', 'CCTV')):
        continue
    if n not in full:
        full.append(n)
brief = sorted({m.group(1) for m in re.finditer(r'id="([A-Za-z][\w.\-]*?)(?:-title|-line|-box|-icon|-wl|-cms|-discharge|-wl-in|-wl-out|-path)"', svg)})
print(f'\ncodes in brief-chart SVG: {len(brief)}   nodes in full chart page: {len(full)}')

d = json.load(open(os.path.join(os.path.dirname(RAW), 'waterlevel_load.json')))
have = {norm(str((s.get('station') or {}).get('tele_station_oldcode') or '')) for s in d['waterlevel_data']['data']} - {''}
RID_EXTRA = ['P5', 'W10A', 'Y14', 'Y6', 'N27', 'N22', 'N8A', 'C29A', 'C22', 'C4', 'C54', 'C39', 'S28A', 'S39']
HII_EXTRA = ['CHM006', 'WAN005', 'YOM001', 'YOM002', 'KWN002', 'CPY013', 'THA011', 'THA002', 'PAS010', 'PAS004', 'BPK002', 'NYK014', 'YOM011']
def inlist(code, lst):
    return any(norm(x) == norm(code) for x in lst)
print('\nwater-level stations absent from waterlevel_load — which chart has them?')
print(f'{"code":9} {"brief SVG":10} {"full chart"}')
for c in RID_EXTRA + HII_EXTRA:
    print(f'{c:9} {"yes" if inlist(c, brief) else "-":10} {"yes" if inlist(c, full) else "-"}')
for fam, sample in [('DAM-*', sorted([n for n in full if n.startswith('DAM-')])[:5]),
                    ('REG-*', sorted([n for n in full if n.startswith('REG-')])[:5]),
                    ('m-dam-*', sorted([n for n in brief if n.startswith('m-dam')])[:5]),
                    ('canal ATG*/BKK*/WR*', [n for n in full if n.startswith(('ATG', 'BKK', 'WR'))][:5])]:
    print(f'{fam:22} full={len([n for n in full if n.startswith(fam.split("*")[0])])}  brief={len([n for n in brief if n.startswith(fam.split("*")[0])])}  e.g. {sample}')
