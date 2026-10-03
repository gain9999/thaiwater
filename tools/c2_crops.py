#!/usr/bin/env python3
"""Tight crops around the C.2 forecast point labels."""
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

JOBS = [
    ('lfoot', 0, 950, 760, 1319, 2.0,
     'Transcribe every line of text visible in this footer/legend crop of a Thai '
     'irrigation-department chart, verbatim. Include any dates or numbers. Be brief.'),
    ('f1', 1280, 250, 1560, 950, 3.0,
     'Transcribe, verbatim and in reading order, the printed number labels on the plotted '
     'curve(s) in this Thai hydrograph crop. For each number also say the day-month label '
     'printed nearest to it. Do not guess; write "unclear" if a number is unreadable. Be brief.'),
    ('f2', 1520, 250, 1800, 950, 3.0,
     'Transcribe, verbatim and in reading order, the printed number labels on the plotted '
     'curve(s) in this Thai hydrograph crop. For each number also say the day-month label '
     'printed nearest to it. Do not guess; write "unclear" if a number is unreadable. Be brief.'),
    ('f3', 1760, 250, 2012, 950, 3.0,
     'Transcribe, verbatim, the printed number labels on the plotted curves in this Thai '
     'hydrograph crop, plus the x-axis day labels at the bottom. Say "unclear" rather than '
     'guessing. Be brief.'),
]

for name, x0, y0, x1, y1, sc, q in JOBS:
    out = os.path.join(BASE, 'out', f'c2_{name}.png')
    subprocess.run([PY, CROP, CHART, out, str(x0), str(y0), str(x1), str(y1), str(sc)], check=True)
    print(f'\n===== {name} ({x0},{y0})-({x1},{y1}) =====', flush=True)
    r = subprocess.run([PY, VISION, out, q], capture_output=True, text=True)
    print((r.stdout or '').strip(), flush=True)
    if not r.stdout.strip():
        print('STDERR:', r.stderr.strip()[:500], flush=True)
