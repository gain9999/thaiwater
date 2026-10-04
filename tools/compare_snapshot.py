#!/usr/bin/env python3
"""Compare two waterlevel_load snapshots: level (m MSL) + discharge deltas.

Usage: compare_snapshot.py NEW.json OLD.json [--filter SUBSTR] [--all]
Prints rows whose river name (or station code) matches filters, plus top movers.
"""
import json
import sys

NUM = lambda v: None if v in (None, "", "-") else float(v)


def load(path, key="waterlevel_data"):
    b = json.load(open(path))
    return (b.get(key) or {}).get("data") or []


def meta(r):
    st = r.get("station") or {}
    nm = st.get("tele_station_name")
    nm = nm.get("th") if isinstance(nm, dict) else nm
    return {
        "id": str(st.get("id")),
        "code": str(st.get("tele_station_oldcode") or ""),
        "name": str(nm or ""),
        "lat": st.get("tele_station_lat"),
        "lon": st.get("tele_station_long"),
        "river": str(r.get("river_name") or ""),
        "t": str(r.get("waterlevel_datetime") or ""),
    }


def delta(r, o, field):
    a, b = NUM(r.get(field)), NUM(o.get(field))
    return None if (a is None or b is None) else a - b


def main():
    if len(sys.argv) < 3:
        raise SystemExit("usage: compare_snapshot.py NEW.json OLD.json [--filter SUBSTR] [--all]")
    new_path, old_path = sys.argv[1], sys.argv[2]
    filt = []
    show_all = False
    args = sys.argv[3:]
    i = 0
    while i < len(args):
        if args[i] == "--filter":
            filt.append(args[i + 1]); i += 2
        elif args[i] == "--all":
            show_all = True; i += 1
        else:
            i += 1
    new, old = load(new_path), load(old_path)
    no = {meta(r)["id"]: r for r in new}
    oo = {meta(r)["id"]: r for r in old}
    rows = []
    for k, r in no.items():
        if k not in oo:
            continue
        m = meta(r)
        rows.append((m, r, oo[k], delta(r, oo[k], "waterlevel_msl"), delta(r, oo[k], "discharge")))

    def line(m, r, o, dl, dq):
        return (f'{m["code"] or "-":9s} {m["name"][:24]:26s} {m["river"][:16]:18s} '
                f'{m["t"][5:]:16s} lvlMSL {str(r.get("waterlevel_msl")):>7s} '
                f'(prev {str(o.get("waterlevel_msl")):>7s} d {("" if dl is None else format(dl, "+.2f")):>6s})  '
                f'Q {str(r.get("discharge")):>8s} (prev {str(o.get("discharge")):>8s} '
                f'dQ {("" if dq is None else format(dq, "+.0f")):>6s})')

    if filt:
        for pat in filt:
            print(f"=== rows matching {pat!r}")
            hits = [x for x in rows if pat in x[0]["river"] or pat.upper() in x[0]["code"].upper()
                    or pat.upper() in x[0]["name"].upper()]
            hits.sort(key=lambda x: -(x[0]["lat"] or 0))
            for m, r, o, dl, dq in hits:
                print(line(m, r, o, dl, dq))
            print()

    movers = [x for x in rows if x[3] is not None and abs(x[3]) >= 0.02]
    movers.sort(key=lambda x: -abs(x[3]))
    print(f"=== level movers |dLevel| >= 0.02 m ({len(movers)} stations)")
    for m, r, o, dl, dq in movers[:20]:
        print(line(m, r, o, dl, dq))

    qs = [x for x in rows if x[4] is not None and abs(x[4]) >= 10]
    qs.sort(key=lambda x: -abs(x[4]))
    print(f"\n=== discharge movers |dQ| >= 10 m3/s ({len(qs)} stations)")
    for m, r, o, dl, dq in qs[:20]:
        print(line(m, r, o, dl, dq))

    if show_all:
        print(f"\n=== all matched ({len(rows)})")
        for m, r, o, dl, dq in sorted(rows, key=lambda x: -(x[0]["lat"] or 0)):
            print(line(m, r, o, dl, dq))


if __name__ == "__main__":
    main()
