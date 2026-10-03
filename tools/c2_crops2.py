#!/usr/bin/env python3
"""Second pass on the F-C2 chart: footer legend/table + label positions."""
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_fc2 import ensure  # noqa: E402  (downloads the chart when it is not there yet)

CHART = os.environ.get('F_C2_JPG') or ensure()
PY = sys.executable
CROP = os.path.join(BASE, 'tools', 'crop_zoom.py')
# Your own image->text helper, called as: PY VISION <png> "<question>".
VISION = os.environ.get('VISION_SCRIPT', '')
if not VISION:
    raise SystemExit('set VISION_SCRIPT=/path/to/vision.py (called as: python vision.py IMAGE "question")')

JOBS = [
    ('legend', 640, 990, 1400, 1319, 2.0,
     'This is the footer band of a Thai irrigation-department hydrograph. Transcribe every '
     'line of Thai/English text and every number verbatim, in reading order. Be brief; if a '
     'line is unreadable write "unclear".'),
    ('legend2', 1380, 990, 2012, 1319, 2.0,
     'This is the bottom-right corner/footer band of a Thai irrigation-department hydrograph. '
     'Transcribe every line of Thai/English text and every number verbatim. Be brief; if '
     'unreadable write "unclear".'),
    ('curve', 1380, 250, 2012, 1010, 2.2,
     'This is the right part of a Thai discharge hydrograph (forecast section, dashed line). '
     'List every printed number label attached to a data point, left to right, and for each '
     'give its horizontal position as a fraction 0.0-1.0 of this crop width (0 = left edge). '
     'Also state how many labels there are in total. Do not guess numbers; write "unclear".'),
]

for name, x0, y0, x1, y1, sc, q in JOBS:
    out = os.path.join(BASE, 'out', f'c2b_{name}.png')
    subprocess.run([PY, CROP, CHART, out, str(x0), str(y0), str(x1), str(y1), str(sc)], check=True)
    print(f'\n===== {name} ({x0},{y0})-({x1},{y1}) =====', flush=True)
    r = subprocess.run([PY, VISION, out, q], capture_output=True, text=True)
    print((r.stdout or '').strip(), flush=True)
    if not r.stdout.strip():
        print('STDERR:', r.stderr.strip()[:400], flush=True)
