#!/usr/bin/env python3
"""Screenshot bands of a raster chart PNG with Chromium (playwright).

Usage: python3 clip_png.py PNG OUT_PREFIX Y0 Y1 [SCALE] [BAND_H]
Writes OUT_PREFIX_<y0>.png per band of BAND_H (default: one band).
"""
import asyncio
import sys

try:
    from playwright.async_api import async_playwright
except ImportError:
    raise SystemExit("playwright is required: pip install playwright && playwright install chromium")


async def main(png, prefix, y0, y1, scale, band_h, w):
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        page = await b.new_page(viewport={'width': int(w), 'height': 1000}, device_scale_factor=scale)
        await page.route('**://*', lambda r: asyncio.ensure_future(r.abort()))
        await page.goto('file://' + png, wait_until='domcontentloaded', timeout=60000)
        await page.wait_for_timeout(1500)
        y = y0
        n = 0
        while y < y1:
            h = min(band_h, y1 - y)
            out = f'{prefix}_{int(y)}.png'
            await page.screenshot(path=out, clip={'x': 0, 'y': y, 'width': w, 'height': h}, full_page=True)
            print('wrote', out, f'({w:.0f}x{h:.0f} @{scale}x)')
            y += h
            n += 1
        await b.close()


if __name__ == '__main__':
    png, prefix = sys.argv[1], sys.argv[2]
    y0, y1 = float(sys.argv[3]), float(sys.argv[4])
    scale = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
    band_h = float(sys.argv[6]) if len(sys.argv) > 6 else (y1 - y0)
    w = float(sys.argv[7]) if len(sys.argv) > 7 else 1534.0
    asyncio.run(main(png, prefix, y0, y1, scale, band_h, w))
