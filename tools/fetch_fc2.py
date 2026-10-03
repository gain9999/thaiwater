#!/usr/bin/env python3
"""Fetch the RID C.2 discharge-forecast chart (F-C2.jpg) into out/.

Source: the Royal Irrigation Department forecast page for station C.2 on the Chao Phraya,
`http://water.rid.go.th/itcwater/utok/F-C2.jpg` (re-issued daily, usually 07:00-08:30 Thai).
Override with env RID_CHART_URL (e.g. .../F-P1.jpg) or by passing DEST/URL arguments.

Usage: python3 tools/fetch_fc2.py [DEST]
The chart is not committed (it is re-issued daily and out/ is scratch); the c2_* tools call
ensure() so they download it on first use.
"""
import os
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = os.environ.get('RID_CHART_URL', 'http://water.rid.go.th/itcwater/utok/F-C2.jpg')
DEFAULT = os.path.join(ROOT, 'out', 'F-C2.jpg')


def fetch(path=None, url=None):
    """Download the chart to path (default out/F-C2.jpg) and report freshness."""
    path = path or DEFAULT
    url = url or URL
    os.makedirs(os.path.dirname(path), exist_ok=True)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
        last_modified = r.headers.get('Last-Modified')
    with open(path, 'wb') as fh:
        fh.write(data)
    print(f'{path}  {len(data)} bytes  Last-Modified: {last_modified}')
    return path


def ensure(path=None, url=None):
    """Return path, downloading the chart first if it is not there yet."""
    path = path or DEFAULT
    if not os.path.exists(path):
        fetch(path, url)
    return path


if __name__ == '__main__':
    fetch(sys.argv[1] if len(sys.argv) > 1 else None)
