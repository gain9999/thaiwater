#!/usr/bin/env python3
"""Flood watch snapshot for one location.

Pulls live data from thaiwater.net (สสน.), HII tide tables and Open-Meteo,
then writes one JSON snapshot that a dashboard can render.

    python3 tools/flood_watch.py --lat 13.9656 --lon 100.6026 --primary BKK002 \
        --compare BKK001,BKK021,CPY014 --out snapshot.json

The alert level is a personal heuristic built on the primary canal station's
bank height, its rate of rise, and the nearest road-flood sensors. It is not
an official warning.
"""
import argparse
import json
import math
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

API = "https://api-v3.thaiwater.net/api/v1/thaiwater30"
TIDE = "https://fews2.hii.or.th/model-output/data_portal/tide_table/summary.txt"
BKK = timezone(timedelta(hours=7))

LEVELS = ["ปกติ", "เฝ้าดู", "เตรียมตัว", "ลงมือ"]


def get(url, as_json=True, timeout=90):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read().decode("utf-8")
    return json.loads(body) if as_json else body


def km(lat1, lon1, lat2, lon2):
    return math.hypot((lat1 - lat2) * 111.0, (lon1 - lon2) * 111.0 * math.cos(math.radians(lat1)))


def num(v):
    try:
        return None if v is None else float(v)
    except (TypeError, ValueError):
        return None


def series(station_id, start, end, step_min=30):
    url = (f"{API}/public/waterlevel_graph?station_type=tele_waterlevel&station_id={station_id}"
           f"&start_date={start:%Y-%m-%d}&end_date={end:%Y-%m-%d}")
    d = get(url)["data"]
    pts = [(p["datetime"], p["value"]) for p in d["graph_data"] if p["value"] is not None]
    out = [[t, round(v, 3)] for t, v in pts if int(t[14:16]) % step_min == 0]
    if pts and (not out or out[-1][0] != pts[-1][0]):
        out.append([pts[-1][0], round(pts[-1][1], 3)])
    return out, pts, d.get("min_bank")


def change(pts, hours):
    """Level change over the last `hours`, from the raw 10-min series."""
    if not pts:
        return None
    t_end = datetime.strptime(pts[-1][0], "%Y-%m-%d %H:%M")
    target = t_end - timedelta(hours=hours)
    past = [v for t, v in pts if datetime.strptime(t, "%Y-%m-%d %H:%M") <= target]
    return round(pts[-1][1] - past[-1], 3) if past else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lat", type=float, required=True)
    ap.add_argument("--lon", type=float, required=True)
    ap.add_argument("--primary", default="BKK002", help="tele_station_oldcode of the canal gauge to judge by")
    ap.add_argument("--compare", default="BKK001,BKK021,CPY014")
    ap.add_argument("--gate", default="ATG101", help="tele_station_oldcode of an upstream floodgate to track")
    ap.add_argument("--hours", type=int, default=72)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    now = datetime.now(BKK)
    errors = []

    # Stations and latest readings
    wl = get(f"{API}/public/waterlevel_load")["waterlevel_data"]["data"]
    by_code = {r["station"].get("tele_station_oldcode"): r for r in wl}
    codes = [a.primary] + [c for c in a.compare.split(",") if c]
    stations = []
    for code in codes:
        r = by_code.get(code)
        if not r:
            errors.append(f"station {code} not in waterlevel_load")
            continue
        s = r["station"]
        try:
            ser, raw, bank = series(s["id"], now - timedelta(hours=a.hours), now)
        except Exception as e:  # keep the snapshot usable if one graph fails
            errors.append(f"graph {code}: {e}")
            ser, raw, bank = [], [], None
        bank = num(bank) or num(s.get("min_bank"))
        level = raw[-1][1] if raw else num(r.get("waterlevel_msl"))
        stations.append({
            "code": code,
            "name": s["tele_station_name"]["th"],
            "amphoe": r["geocode"]["amphoe_name"]["th"],
            "province": r["geocode"]["province_name"]["th"],
            "km": round(km(a.lat, a.lon, s["tele_station_lat"], s["tele_station_long"]), 1),
            "lat": s["tele_station_lat"], "lon": s["tele_station_long"],
            "bank": bank,
            "level": level,
            "at": raw[-1][0] if raw else r.get("waterlevel_datetime"),
            "over_bank": round(level - bank, 3) if level is not None and bank else None,
            "d1h": change(raw, 1),
            "d3h": change(raw, 3),
            "d24h": change(raw, 24),
            "series": ser,
        })

    # Rainfall, 10 km radius
    rain = []
    try:
        for r in get(f"{API}/public/rain_24h")["data"]:
            s = r.get("station") or {}
            la, lo = s.get("tele_station_lat"), s.get("tele_station_long")
            if la and lo and km(a.lat, a.lon, la, lo) <= 10:
                rain.append({
                    "name": s["tele_station_name"]["th"],
                    "km": round(km(a.lat, a.lon, la, lo), 1),
                    "lat": round(la, 5), "lon": round(lo, 5),
                    "r24": num(r.get("rain_24h")),
                    "r1": num(r.get("rain_1h")),
                    "at": r.get("rainfall_datetime"),
                })
        rain.sort(key=lambda x: x["km"])
    except Exception as e:
        errors.append(f"rain: {e}")

    # Road flood sensors, 6 km radius, reported today
    roads = []
    try:
        today = now.strftime("%Y-%m-%d")
        for r in get(f"{API}/public/flood_road")["data"]:
            s = r["station"]
            la, lo = s.get("floodroad_lat"), s.get("floodroad_long")
            if la and lo and (r.get("floodroad_datetime") or "").startswith(today):
                d = km(a.lat, a.lon, la, lo)
                if d <= 6:
                    roads.append({"name": s["floodroad_name"]["th"].replace(" *", ""), "km": round(d, 1),
                                  "lat": round(la, 5), "lon": round(lo, 5),
                                  "cm": num(r.get("floodroad_value")), "at": r["floodroad_datetime"]})
        roads.sort(key=lambda x: x["km"])
    except Exception as e:
        errors.append(f"flood_road: {e}")

    # Upstream floodgate: level above (in) and below (out) the gate
    gate = None
    try:
        for r in get(f"{API}/public/watergate_load")["watergate_data"]["data"]:
            s = r.get("station") or {}
            if s.get("tele_station_oldcode") == a.gate:
                gate = {"code": a.gate, "name": (s.get("tele_station_name") or {}).get("th"),
                        "km": round(km(a.lat, a.lon, s["tele_station_lat"], s["tele_station_long"]), 1),
                        "lat": s["tele_station_lat"], "lon": s["tele_station_long"],
                        "in": num(r.get("watergate_in")), "out": num(r.get("watergate_out")),
                        "at": r.get("watergate_datetime_in")}
                break
        else:
            errors.append(f"gate {a.gate} not in watergate_load")
    except Exception as e:
        errors.append(f"watergate: {e}")

    # Hourly rain forecast (Open-Meteo), next 36 h
    forecast = []
    try:
        om = get("https://api.open-meteo.com/v1/forecast?latitude=%.4f&longitude=%.4f"
                 "&hourly=precipitation,precipitation_probability&timezone=Asia/Bangkok&forecast_days=3"
                 % (a.lat, a.lon))["hourly"]
        start = now.strftime("%Y-%m-%dT%H")
        for t, p, pp in zip(om["time"], om["precipitation"], om["precipitation_probability"]):
            if t >= start and len(forecast) < 36:
                forecast.append([t.replace("T", " "), p, pp])
    except Exception as e:
        errors.append(f"forecast: {e}")

    # Chao Phraya tide, Bangkok Harbour (N02)
    tide = None
    try:
        for line in get(TIDE, as_json=False).splitlines():
            f = line.split(",")
            if f[0] == "N02":
                tide = {"date": f[5], "high": round(float(f[6]), 2), "high_at": f[7],
                        "low": round(float(f[8]), 2), "low_at": f[9]}
    except Exception as e:
        errors.append(f"tide: {e}")

    # Alert level
    p = stations[0] if stations and stations[0]["code"] == a.primary else None
    level, reasons = 0, []
    if p and p["over_bank"] is not None:
        ob, d1 = p["over_bank"], p["d1h"] or 0
        if ob >= 0:
            level = 1
            reasons.append(f"{p['name']} สูงกว่าตลิ่ง {ob * 100:.0f} ซม.")
        if ob >= 0.20:
            level = max(level, 2)
        if ob >= 0 and d1 >= 0.05:
            level = max(level, 2)
            reasons.append(f"ขึ้นเร็ว {d1 * 100:+.0f} ซม. ใน 1 ชม.")
        if ob >= 0.40:
            level = 3
        if ob < 0:
            reasons.append(f"{p['name']} ต่ำกว่าตลิ่ง {-ob * 100:.0f} ซม.")
    near = [r for r in roads if r["km"] <= 4 and r["cm"] is not None]
    worst = max(near, key=lambda r: r["cm"], default=None)
    if worst and worst["cm"] >= 5:
        level = max(level, 3 if worst["cm"] >= 15 else 2)
        reasons.append(f"ถนน{worst['name']} ท่วม {worst['cm']:.0f} ซม.")
    rain_next6 = round(sum(f[1] or 0 for f in forecast[:6]), 1)
    if rain_next6 >= 20 and level >= 1:
        reasons.append(f"พยากรณ์ฝน 6 ชม. ข้างหน้า {rain_next6:.0f} มม.")

    snap = {
        "checked_at": now.strftime("%Y-%m-%d %H:%M"),
        "level": level,
        "level_name": LEVELS[level],
        "reasons": reasons,
        "rain_next6": rain_next6,
        "primary": a.primary,
        "stations": stations,
        "rain": rain[:16],
        "roads": roads[:10],
        "forecast": forecast,
        "tide": tide,
        "gate": gate,
        "errors": errors,
    }
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(snap, fh, ensure_ascii=False)

    log = {"checked_at": snap["checked_at"], "level": level, "level_name": LEVELS[level],
           "primary_level": p["level"] if p else None, "over_bank": p["over_bank"] if p else None,
           "d1h": p["d1h"] if p else None, "reasons": reasons,
           "gate_in": gate["in"] if gate else None,
           "rain1h_max": max((r["r1"] or 0 for r in rain[:5]), default=None)}
    with open(a.out.replace(".json", "") + ".log.json", "w", encoding="utf-8") as fh:
        json.dump(log, fh, ensure_ascii=False)
    print(json.dumps(log, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
