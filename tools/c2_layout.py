#!/usr/bin/env python3
"""Locate the printed value labels on the F-C2 chart and map their x to a date.

The vision model can read the numbers but not reliably say which day each belongs to.
Here the chart's own layout is used instead: vertical gridlines are detected (light grey
columns), the darkest text clusters in the plot area are found, and each cluster's x is
converted into a date using two gridlines as anchors (found by their label text dates,
which the axis print gives: the axis runs 15 Sep -> 13 Oct).
"""
import os
import sys
from PIL import Image
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHART = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, 'out', 'F-C2.jpg')
im = Image.open(CHART).convert('RGB')
a = np.asarray(im).astype(int)
H, W, _ = a.shape
print('chart', W, 'x', H)

grey = np.abs(a[:, :, 0] - a[:, :, 1]) + np.abs(a[:, :, 1] - a[:, :, 2])
lum = a.mean(axis=2)
grid = (grey < 12) & (lum > 160) & (lum < 235)
colcount = grid[100:1100].sum(axis=0)
cand = [x for x in range(W) if colcount[x] > 400]
# merge adjacent
groups = []
for x in cand:
    if groups and x - groups[-1][-1] <= 3:
        groups[-1].append(x)
    else:
        groups.append([x])
centers = [int(sum(g) / len(g)) for g in groups]
print('gridline x (light grey, long):', centers[:40], '...' if len(centers) > 40 else '')

# dark text clusters inside the plot area (y band where labels sit)
dark = (lum < 110)
band = dark[200:1050, :]
colsum = band.sum(axis=0)
xs = [x for x in range(W) if colsum[x] > 0]
groups2 = []
for x in xs:
    if groups2 and x - groups2[-1][-1] <= 18:
        groups2[-1].append(x)
    else:
        groups2.append([x])
clusters = [(g[0], g[-1], int(sum(g) / len(g))) for g in groups2 if g[-1] - g[0] > 12]
print('\ndark text clusters (x0,x1,xcenter, width):')
for c in clusters:
    rows = band[:, c[0]:c[1] + 1].sum(axis=1)
    ys = np.nonzero(rows)[0]
    print(f'  {c[0]:>5}-{c[1]:<5} center {c[2]:>5} w {c[1]-c[0]:>3}  y {200+ys.min() if len(ys) else "?"}-{200+ys.max() if len(ys) else "?"}')
