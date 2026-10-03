#!/usr/bin/env python3
"""Find the printed value labels on F-C2 by 2D dark-pixel density, then date-map them.

Axis anchor verified from the printed date labels: the leftmost daily gridline maps to
4 Sep (x=284) and the spacing is 44.7 px/day, which reproduces the 15 Sep (x=775),
1 Oct (x=1490) and 3 Oct (x=1580) gridlines in the detected series.
"""
import os
import sys
import numpy as np
from PIL import Image

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_fc2 import ensure  # noqa: E402  (downloads the chart when it is not there yet)

CHART = sys.argv[1] if len(sys.argv) > 1 else ensure()
im = Image.open(CHART).convert('RGB')
a = np.asarray(im).astype(int)
lum = a.mean(axis=2)
H, W = lum.shape

X0, DX, D0 = 284.0, 44.7, 0  # x of 4 Sep
def x2date(x):
    idx = (x - X0) / DX
    day = 4 + idx  # Sep 4 + idx days
    return day

dark = (lum < 120)
# density over 26x20 boxes
by, bx = 20, 26
h, w = H // by, W // bx
dens = np.zeros((h, w), dtype=int)
for j in range(h):
    for i in range(w):
        dens[j, i] = dark[j*by:(j+1)*by, i*bx:(i+1)*bx].sum()

# text boxes: dense AND not part of a long vertical/horizontal run
cand = []
for j in range(h):
    for i in range(w):
        if dens[j, i] < 25:
            continue
        y0, x0 = j*by, i*bx
        if y0 < 150 or y0 > 1000:
            continue
        cand.append((x0, y0, dens[j, i]))

# cluster candidates that touch
cand.sort()
used = [False]*len(cand)
clusters = []
for i, (x0, y0, d) in enumerate(cand):
    if used[i]:
        continue
    stack = [(x0, y0)]
    used[i] = True
    members = [(x0, y0)]
    while stack:
        cx, cy = stack.pop()
        for k, (x1, y1, _) in enumerate(cand):
            if used[k]:
                continue
            if abs(x1-cx) <= bx and abs(y1-cy) <= by:
                used[k] = True
                stack.append((x1, y1))
                members.append((x1, y1))
    xs = [m[0] for m in members]
    ys = [m[1] for m in members]
    if len(members)*1.0 >= 1:
        clusters.append((min(xs), max(xs)+bx, min(ys), max(ys)+by, len(members)))

clusters.sort()
print(f'{len(clusters)} text-like clusters in the plot area (x0,x1,y0,y1,boxes):')
for x0, x1, y0, y1, n in clusters:
    wpx = x1-x0
    day = x2date((x0+x1)/2)
    print(f'  x {x0:>4}-{x1:<4} y {y0:>4}-{y1:<4} boxes {n:>3}  w {wpx:>3}  -> approx day {day:.1f} (Sep-based)')
