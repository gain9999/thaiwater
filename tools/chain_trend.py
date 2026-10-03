#!/usr/bin/env python3
"""Main-stem Chao Phraya level + discharge trend from the thaiwater graph API.

Fetches hourly series for the C.* / CPY* chain, prints the last N hours per station
with hour-to-hour deltas, and renders a 2-panel PNG (level MSL, discharge).

Usage: chain_trend.py [--hours 12] [--days 3] [--out FILE.png]
"""
import argparse
import datetime
import json
import os
import urllib.parse
import urllib.request

API = "https://api-v3.thaiwater.net/api/v1/thaiwater30/public/waterlevel_graph"
UA = {"User-Agent": "Mozilla/5.0"}

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(BASE, "out")

# (code, station_id) — id taken from waterlevel_load.station.id
CHAIN = [
    ("C.2", 2795),
    ("CPY002", None),
    ("C.13", 2744),
    ("C.3", 2723),
    ("C.7A", 2626),
    ("C.36", 2611),
    ("C.35", 2609),
    ("C.12", 2599),
]


def get(url):
    return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90).read().decode())


def series(sid, days=3):
    end = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
    start = end - datetime.timedelta(days=days)
    q = urllib.parse.urlencode({
        "station_type": "tele_waterlevel",
        "station_id": sid,
        "start_date": start.strftime("%Y-%m-%d %H:%M"),
        "end_date": end.strftime("%Y-%m-%d %H:%M"),
    })
    b = get(API + "?" + q)
    d = (b.get("data") or {}).get("graph_data") or []
    # The graph API pads the window with placeholder rows stamped a day ahead and
    # carrying null values; drop those or the "last N hours" slice comes back empty.
    cutoff = datetime.datetime.now() + datetime.timedelta(hours=8)  # naive: Thai wall clock + 1 h slop
    out = []
    for r in d:
        if not r.get("datetime"):
            continue
        try:
            t = datetime.datetime.strptime(r["datetime"], "%Y-%m-%d %H:%M")
        except ValueError:
            continue
        if t > cutoff:
            continue
        if r.get("value") in (None, "") and r.get("discharge") in (None, ""):
            continue
        out.append(r)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hours", type=int, default=12)
    ap.add_argument("--days", type=int, default=3)
    ap.add_argument("--out", default=os.path.join(OUTDIR, "chain_trend.png"))
    a = ap.parse_args()

    data = {}
    for code, sid in CHAIN:
        if sid is None:
            continue
        try:
            data[code] = series(sid, a.days)
        except Exception as e:  # noqa: BLE001
            print(f"{code}: ERROR {e!r}"[:120])

    print(f"=== last {a.hours} hourly readings (level = m MSL, Q = m3/s)")
    for code, rows in data.items():
        rows = sorted(rows, key=lambda r: r["datetime"])[-a.hours:]
        if not rows:
            continue
        first, last = rows[0], rows[-1]
        f = lambda v: None if v in (None, "") else float(v)
        dlvl = (f(last.get("value")) or 0) - (f(first.get("value")) or 0) if f(last.get("value")) is not None and f(first.get("value")) is not None else None
        dq = None
        if f(last.get("discharge")) is not None and f(first.get("discharge")) is not None:
            dq = f(last["discharge"]) - f(first["discharge"])
        print(f"\n{code}: {first['datetime']} -> {last['datetime']}  "
              f"level {last.get('value')} ({'' if dlvl is None else format(dlvl, '+.2f')} m over window)  "
              f"Q {last.get('discharge')} ({'' if dq is None else format(dq, '+.0f')})")
        for r in rows:
            print(f"   {r['datetime']}  lvl {r.get('value')}  out {r.get('value_out')}  Q {r.get('discharge')}")

    os.makedirs(os.path.join(BASE, "data"), exist_ok=True)
    json.dump(data, open(os.path.join(BASE, "data", "chain_trend.json"), "w"), ensure_ascii=False)

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as e:  # noqa: BLE001
        print("no matplotlib:", e)
        return
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
    for code, rows in data.items():
        rows = sorted(rows, key=lambda r: r["datetime"])
        if not rows:
            continue
        x = [datetime.datetime.strptime(r["datetime"], "%Y-%m-%d %H:%M") for r in rows]
        y = [None if r.get("value") in (None, "") else float(r["value"]) for r in rows]
        ax1.plot(x, y, marker=".", lw=1.2, label=code)
        yq = [None if r.get("discharge") in (None, "") else float(r["discharge"]) for r in rows]
        if any(v is not None for v in yq):
            ax2.plot(x, yq, marker=".", lw=1.2, label=code)
    ax1.set_ylabel("level (m MSL)")
    ax1.set_title("Chao Phraya main stem — level & discharge, last %d days" % a.days)
    ax1.grid(alpha=.3)
    ax1.legend(ncol=4, fontsize=8)
    ax2.set_ylabel("discharge (m3/s)")
    ax2.grid(alpha=.3)
    ax2.legend(ncol=4, fontsize=8)
    fig.autofmt_xdate()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    fig.tight_layout()
    fig.savefig(a.out, dpi=110)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
