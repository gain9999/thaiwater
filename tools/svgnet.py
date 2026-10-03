#!/usr/bin/env python3
"""Cross-check the thaiwater-derived station chain against the official
waterchart.thaiwater.net Chao Phraya schematic (chaophraya.svg).

Method: every station in the SVG has a leader line/polyline from its label box
to the river ("<CODE>-line"). The far end of that leader is the station's
position on the drawn river network. Snapping those points to the drawn river
polylines and ordering them by arc length gives the chart's own ordering.

Output: chain per drawn river polyline + nearest neighbours per station.
"""
import json
import math
import os
import re
import sys
import xml.etree.ElementTree as ET

RAW = os.environ.get('THAIWATER_RAW', os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'raw'))
SVG = os.path.join(RAW, 'cp.svg')
NS = '{http://www.w3.org/2000/svg}'
NUM = re.compile(r'[-+]?\d*\.?\d+(?:e[-+]?\d+)?')


def toks(d):
    return re.findall(r'[MmLlHhVvCcSsQqTtAaZz]|[-+]?\d*\.?\d+(?:e[-+]?\d+)?', d)


def sample_cubic(p0, p1, p2, p3, n=10):
    out = []
    for i in range(1, n + 1):
        t = i / n
        mt = 1 - t
        x = mt**3*p0[0] + 3*mt*mt*t*p1[0] + 3*mt*t*t*p2[0] + t**3*p3[0]
        y = mt**3*p0[1] + 3*mt*mt*t*p1[1] + 3*mt*t*t*p2[1] + t**3*p3[1]
        out.append((x, y))
    return out


def sample_quad(p0, p1, p2, n=8):
    out = []
    for i in range(1, n + 1):
        t = i / n
        mt = 1 - t
        x = mt*mt*p0[0] + 2*mt*t*p1[0] + t*t*p2[0]
        y = mt*mt*p0[1] + 2*mt*t*p1[1] + t*t*p2[1]
        out.append((x, y))
    return out


def path_to_poly(d):
    t = toks(d)
    i = 0
    cur = (0.0, 0.0)
    start = (0.0, 0.0)
    prev_ctrl = None
    pts = []
    cmd = None
    while i < len(t):
        if re.match(r'[A-Za-z]', t[i]):
            cmd = t[i]
            i += 1
        rel = cmd.islower()
        c = cmd.upper()
        if c == 'M':
            x, y = float(t[i]), float(t[i+1]); i += 2
            cur = (cur[0]+x, cur[1]+y) if rel else (x, y)
            pts.append(cur); start = cur; prev_ctrl = None
            cmd = 'l' if rel else 'L'
        elif c == 'L':
            x, y = float(t[i]), float(t[i+1]); i += 2
            cur = (cur[0]+x, cur[1]+y) if rel else (x, y)
            pts.append(cur); prev_ctrl = None
        elif c == 'H':
            x = float(t[i]); i += 1
            cur = (cur[0]+x, cur[1]) if rel else (x, cur[1])
            pts.append(cur); prev_ctrl = None
        elif c == 'V':
            y = float(t[i]); i += 1
            cur = (cur[0], cur[1]+y) if rel else (cur[0], y)
            pts.append(cur); prev_ctrl = None
        elif c == 'C':
            x1, y1, x2, y2, x, y = [float(v) for v in t[i:i+6]]; i += 6
            if rel:
                p1 = (cur[0]+x1, cur[1]+y1); p2 = (cur[0]+x2, cur[1]+y2); p3 = (cur[0]+x, cur[1]+y)
            else:
                p1, p2, p3 = (x1, y1), (x2, y2), (x, y)
            pts += sample_cubic(cur, p1, p2, p3); prev_ctrl = p2; cur = p3
        elif c == 'S':
            x2, y2, x, y = [float(v) for v in t[i:i+4]]; i += 4
            if rel:
                p2 = (cur[0]+x2, cur[1]+y2); p3 = (cur[0]+x, cur[1]+y)
            else:
                p2, p3 = (x2, y2), (x, y)
            p1 = prev_ctrl if prev_ctrl else cur
            pts += sample_cubic(cur, p1, p2, p3); prev_ctrl = p2; cur = p3
        elif c == 'Q':
            x1, y1, x, y = [float(v) for v in t[i:i+4]]; i += 4
            if rel:
                p1 = (cur[0]+x1, cur[1]+y1); p2 = (cur[0]+x, cur[1]+y)
            else:
                p1, p2 = (x1, y1), (x, y)
            pts += sample_quad(cur, p1, p2); prev_ctrl = p1; cur = p2
        elif c == 'T':
            x, y = float(t[i]), float(t[i+1]); i += 2
            p2 = (cur[0]+x, cur[1]+y) if rel else (x, y)
            p1 = prev_ctrl if prev_ctrl else cur
            pts += sample_quad(cur, p1, p2); prev_ctrl = p1; cur = p2
        elif c == 'Z':
            pts.append(start); cur = start
        else:
            i += 1
    return pts


def plen(pts):
    return sum(math.dist(pts[k], pts[k+1]) for k in range(len(pts)-1))


def point_seg_dist(p, a, b):
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx-ax, by-ay
    if dx == 0 and dy == 0:
        return math.dist(p, a), 0.0
    t = ((px-ax)*dx + (py-ay)*dy) / (dx*dx + dy*dy)
    t = max(0.0, min(1.0, t))
    return math.dist(p, (ax+t*dx, ay+t*dy)), t


def snap(poly, p):
    best = (1e9, 0.0)
    arc = 0.0
    for k in range(len(poly)-1):
        d, t = point_seg_dist(p, poly[k], poly[k+1])
        seg = math.dist(poly[k], poly[k+1])
        if d < best[0]:
            best = (d, arc + t*seg)
        arc += seg
    return best  # (distance, arc position)


def parse(svg=SVG, verbose=True):
    """Parse the chart SVG -> (paths, leaders, parent, root).

    paths   : [(id, [ (x,y) ... ], [group ancestry])]
    leaders : {station code: (attach point, label point)}
    """
    tree = ET.parse(svg)
    root = tree.getroot()

    # parent map to know group ancestry
    parent = {}
    for el in root.iter():
        for ch in el:
            parent[ch] = el

    def ancestry(el):
        out = []
        while el in parent:
            el = parent[el]
            out.append(el.get('id') or '')
        return out

    paths = []      # (id, pts, group)
    leaders = {}    # code -> river attach point
    for el in root.iter():
        tag = el.tag.replace(NS, '')
        eid = el.get('id') or ''
        if tag == 'path' and el.get('d'):
            if eid.endswith('-box') or eid.endswith('-icon'):
                continue
            pts = path_to_poly(el.get('d'))
            if len(pts) >= 2:
                paths.append((eid, pts, [a for a in ancestry(el) if a][:3]))
        elif tag in ('line', 'polyline') and eid.endswith('-line'):
            code = eid[:-len('-line')]
            if tag == 'line':
                p1 = (float(el.get('x1')), float(el.get('y1')))
                p2 = (float(el.get('x2')), float(el.get('y2')))
                leaders[code] = (p1, p2)
            else:
                nums = NUM.findall(el.get('points') or '')
                pp = [(float(nums[i]), float(nums[i+1])) for i in range(0, len(nums)-1, 2)]
                if len(pp) >= 2:
                    leaders[code] = (pp[0], pp[-1])

    if verbose:
        print(f'paths: {len(paths)}  stations with leader: {len(leaders)}')
        # group stats
        from collections import Counter
        print('path groups:', Counter(tuple(g) for _, _, g in paths).most_common(12))
    return paths, leaders, parent, root


def dump(raw_dir=RAW, svg=None):
    """Write raw_dir/svg_paths.json + svg_leaders.json from the chart SVG."""
    svg = svg or os.path.join(raw_dir, 'cp.svg')
    paths, leaders, _parent, _root = parse(svg, verbose=False)
    json.dump({k: v for k, v in leaders.items()},
              open(os.path.join(raw_dir, 'svg_leaders.json'), 'w'))
    json.dump([[i, p, g] for i, p, g in paths],
              open(os.path.join(raw_dir, 'svg_paths.json'), 'w'))
    return paths, leaders


def ensure_paths(raw_dir=RAW, svg=None):
    """Return (paths, leaders) for the chart SVG, building the cache if absent.

    svg_paths.json is a large derived file that is not committed, so the
    chart-reading tools build it on first use from data/raw/cp.svg."""
    p = os.path.join(raw_dir, 'svg_paths.json')
    l = os.path.join(raw_dir, 'svg_leaders.json')
    if os.path.exists(p) and os.path.exists(l):
        return json.load(open(p)), json.load(open(l))
    src = svg or os.path.join(raw_dir, 'cp.svg')
    if not os.path.exists(src):
        raise SystemExit(f'chart SVG not found: {src} (see data/README.md)')
    paths, leaders = dump(raw_dir, src)
    return [[i, pt, g] for i, pt, g in paths], {k: v for k, v in leaders.items()}


if __name__ == '__main__':
    paths, leaders, parent, root = parse()
    # attach point = leader end farthest from the station box
    for code, (p1, p2) in list(leaders.items())[:10]:
        print(code, p1, p2)
    json.dump({k: v for k, v in leaders.items()}, open(os.path.join(RAW, 'svg_leaders.json'), 'w'))
    json.dump([[i, p, g] for i, p, g in paths], open(os.path.join(RAW, 'svg_paths.json'), 'w'))
