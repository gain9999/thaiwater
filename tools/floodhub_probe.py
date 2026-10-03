#!/usr/bin/env python3
"""Probe Google Flood Forecasting API reachability and auth from this machine.

Auth: an API key (env FLOODHUB_API_KEY, else ~/.floodhub-api-key). API-key auth is what the
Flood Hub endpoints accept; a service-account/ADC token is NOT interchangeable here, and an
API key never works on Cloud Storage.

Usage: python3 tools/floodhub_probe.py
"""
import json
import os
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://floodforecasting.googleapis.com/v1"


def api_key():
    k = os.environ.get("FLOODHUB_API_KEY", "").strip()
    if k:
        return k
    p = os.path.expanduser("~/.floodhub-api-key")
    if os.path.exists(p):
        return open(p).read().strip()
    raise SystemExit("set FLOODHUB_API_KEY to a Google Flood Forecasting API key")


KEY = api_key()
print(f"key loaded ({len(KEY)} chars)")


def call(path, body=None, method="GET"):
    url = BASE + path + ("&" if "?" in path else "?") + urllib.parse.urlencode({"key": KEY})
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"},
                                 method=method)
    try:
        r = urllib.request.urlopen(req, timeout=45)
        return r.status, r.read()[:800].decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:600].decode("utf-8", "replace")
    except Exception as e:  # noqa: BLE001
        return "ERR", str(e)


print("--- 1. gauges:searchGaugesByArea (TH) ---")
s, b = call("/gauges:searchGaugesByArea", {"regionCode": "TH"}, "POST")
print(s, b[:700])
print("--- 2. floodStatus:searchLatestFloodStatusByArea (TH) ---")
s, b = call("/floodStatus:searchLatestFloodStatusByArea", {"regionCode": "TH"}, "POST")
print(s, b[:500])
