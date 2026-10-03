#!/usr/bin/env python3
"""Crop + upscale a region of an image (PIL). Usage:
crop_zoom.py SRC OUT x0 y0 x1 y1 [scale]"""
import sys
from PIL import Image

if len(sys.argv) < 7:
    raise SystemExit(__doc__.strip().splitlines()[-1])
src, out, x0, y0, x1, y1 = sys.argv[1], sys.argv[2], *[int(v) for v in sys.argv[3:7]]
scale = float(sys.argv[7]) if len(sys.argv) > 7 else 2.0
im = Image.open(src).convert("RGB")
c = im.crop((x0, y0, x1, y1))
c = c.resize((int(c.width * scale), int(c.height * scale)), Image.LANCZOS)
c.save(out)
print(out, c.size)
