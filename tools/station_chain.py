#!/usr/bin/env python3
"""Derive station topology (chain order per river + co-located cross-agency pairs)
from the thaiwater.net waterlevel_load payload.

There is no explicit station-to-station link table in the thaiwater API, so the
ordering is reconstructed: group by river_name, then walk a greedy
nearest-neighbour chain starting from the northern-most station of the group
(Thai rivers in the payload flow roughly south / south-west).

Usage:
    python3 station_chain.py [path-to-waterlevel_load.json] [river-substring]

Prints markdown. Read-only: never writes to a repo.
"""
import json
import math
import os
import sys
from collections import defaultdict

EARTH_R = 6371.0088


def hav(a, b):
    la1, lo1, la2, lo2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    dla, dlo = la2 - la1, lo2 - lo1
    h = math.sin(dla / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin(dlo / 2) ** 2
    return 2 * EARTH_R * math.asin(math.sqrt(h))


def load(path):
    d = json.load(open(path))
    out = []
    for s in d["waterlevel_data"]["data"]:
        st = s.get("station") or {}
        lat, lon = st.get("tele_station_lat"), st.get("tele_station_long")
        if lat is None or lon is None:
            continue
        out.append({
            "code": str(st.get("tele_station_oldcode") or st.get("tele_station_code") or "-"),
            "name": (st.get("tele_station_name") or {}).get("th", ""),
            "ll": (lat, lon),
            "river": str(s.get("river_name") or ""),
            "agency": (s.get("agency") or {}).get("agency_shortname", {}).get("en", ""),
            "msl": s.get("waterlevel_msl"),
            "sit": s.get("situation_level"),
            "bank": s.get("diff_wl_bank"),
            "bank_txt": s.get("diff_wl_bank_text"),
            "dt": s.get("waterlevel_datetime"),
        })
    return out


def chain(stations):
    """Greedy nearest-neighbour path, seeded at the northern-most station."""
    rest = sorted(stations, key=lambda s: -s["ll"][0])
    cur = rest.pop(0)
    path = [cur]
    total = 0.0
    while rest:
        nxt = min(rest, key=lambda s: hav(cur["ll"], s["ll"]))
        d = hav(cur["ll"], nxt["ll"])
        total += d
        path.append(nxt)
        rest.remove(nxt)
        cur = nxt
    return path, total


def main():
    default_wl = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                              "data", "waterlevel_load.json")
    path = sys.argv[1] if len(sys.argv) > 1 else default_wl
    filt = sys.argv[2] if len(sys.argv) > 2 else None
    if not os.path.exists(path):
        raise SystemExit(
            f"snapshot not found: {path}\n"
            "Run tools/fetch_nodes.py once (it writes data/waterlevel_load.json from the "
            "key-free public API), or pass a snapshot path as the first argument.")
    st = load(path)
    print(f"# station chain reconstruction — {len(st)} stations with coordinates\n")
    rivers = defaultdict(list)
    for s in st:
        if s["river"]:
            rivers[s["river"]].append(s)

    keys = [r for r in rivers if (filt is None or filt in r)]
    keys.sort(key=lambda r: -len(rivers[r]))
    for r in keys:
        grp = rivers[r]
        if len(grp) < 2:
            continue
        p, total = chain(grp)
        print(f"## {r}  ({len(grp)} stations, chain length {total:.0f} km)")
        prev = None
        for s in p:
            leg = f"{hav(prev['ll'], s['ll']):5.2f} km" if prev else "  start"
            print(f"  {leg}  {s['code']:9} {s['name'][:30]:32} {s['ll'][0]:.4f},{s['ll'][1]:.4f} "
                  f"{s['agency']:4} msl={s['msl']} sit={s['sit']} {s['bank_txt'] or ''}")
            prev = s
        print()

    # co-located pairs across agencies (<0.5 km) — "same site, two station families"
    print("\n# co-located station pairs (different code families, <0.5 km apart)\n")
    st2 = sorted(st, key=lambda s: (s["ll"][0], s["ll"][1]))
    pairs = []
    for i, a in enumerate(st2):
        for b in st2[i + 1:]:
            if b["ll"][0] - a["ll"][0] > 0.01:  # ~1.1 km lat window
                break
            d = hav(a["ll"], b["ll"])
            if d < 0.5 and a["agency"] != b["agency"] and a["code"][:2] != b["code"][:2]:
                pairs.append((d, a, b))
    pairs.sort()
    for d, a, b in pairs:
        print(f"  {d*1000:5.0f} m  {a['code']:9} {a['name'][:26]:28} <-> {b['code']:9} {b['name'][:26]:28} "
              f"[{a['agency']}/{b['agency']}] river={a['river'] or b['river']}")
    print(f"\n{len(pairs)} pairs")


if __name__ == "__main__":
    main()
