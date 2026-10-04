#!/usr/bin/env python3
"""Locate the F-C2 data table by tiling the chart and asking the vision model per tile."""
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_fc2 import ensure  # noqa: E402  (downloads the chart when it is not there yet)

# Your own image->text helper, called as: PY VISION <png> "<question>".
VISION = os.environ.get('VISION_SCRIPT', '')
if not VISION:
    raise SystemExit('set VISION_SCRIPT=/path/to/vision.py (called as: python vision.py IMAGE "question")')

CHART = os.environ.get('F_C2_JPG') or ensure()
PY = sys.executable
CROP = os.path.join(BASE, 'tools', 'crop_zoom.py')

TILES = [
    ('left', 0, 0, 700, 1319),
    ('mid', 660, 0, 1360, 1319),
    ('right', 1320, 0, 2012, 1319),
]
Q = ('This is one vertical slice of an official RID (Royal Irrigation Department) discharge '
     'forecast chart for station C.2 on the Chao Phraya river. Describe ONLY what is visibly '
     'printed in this exact crop: axis labels, dates, any table columns/rows with numbers. '
     'If there is a table of forecast values, transcribe every number and date verbatim. '
     'If there is no table, say "no table" and list the axis labels and title text you can read.')

for name, x0, y0, x1, y1 in TILES:
    out = os.path.join(BASE, 'out', f'tile_{name}.png')
    subprocess.run([PY, CROP, CHART, out, str(x0), str(y0), str(x1), str(y1), '1.5'], check=True)
    print(f'\n===== {name} ({x0},{y0})-({x1},{y1}) =====', flush=True)
    r = subprocess.run([PY, VISION, out, Q], capture_output=True, text=True)
    print(r.stdout.strip() or r.stderr.strip(), flush=True)
