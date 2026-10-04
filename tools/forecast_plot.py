#!/usr/bin/env python3
"""C.2 plot with the OBSERVED vs FORECAST split made explicit.

Observed: hourly telemetry from thaiwater graph API (tools/chain_trend.py --days 3
          -> data/chain_trend.json).
Forecast: RID ANNs 1-3 day chart http://water.rid.go.th/itcwater/utok/F-C2.jpg
          read via the image-vision skill (values printed on the chart).
          Keep RID_FORECAST in sync with the chart actually read; the issue
          timestamp is part of the label on the figure.

Usage: python3 tools/forecast_plot.py
"""
import datetime
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.font_manager as fm  # noqa: E402

# Thai glyphs: use Noto Sans Thai if present (env THAI_FONT, ~/.fonts, or the system path)
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _TP in [os.environ.get("THAI_FONT", ""), os.path.expanduser("~/.fonts/NotoSansThai.ttf"),
            "/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf"]:
    if _TP and os.path.exists(_TP):
        fm.fontManager.addfont(_TP)
        plt.rcParams["font.family"] = [fm.FontProperties(fname=_TP).get_name(), "DejaVu Sans"]
        break

TREND = os.environ.get("CHAIN_TREND") or os.path.join(BASE, "data", "chain_trend.json")
OUT = os.path.join(BASE, "out", "c2_observed_vs_forecast.png")

# --- RID ANNs forecast, read from F-C2.jpg ---------------------------------
# chart file Last-Modified 2026-09-30 01:10 UTC (08:10 Thai), data as of 06:00 Thai
FORECAST_ISSUED = "RID ANNs forecast — chart F-C2.jpg issued 30 Sep 2026 08:10 Thai (data to 06:00)"
# (label, datetime, discharge m3/s, level m MSL)
RID_FORECAST = [
    ("30 Sep\n(current)", datetime.datetime(2026, 9, 30, 6, 0), 2326, 23.51),
    ("1 Oct\n(+1d)", datetime.datetime(2026, 10, 1, 6, 0), 2713, 24.26),
    ("2 Oct\n(+2d)", datetime.datetime(2026, 10, 2, 6, 0), 2956, 24.64),
    ("3 Oct\n(+3d)", datetime.datetime(2026, 10, 3, 6, 0), 2952, 24.63),
]


def observed(code="C.2"):
    d = json.load(open(TREND))[code]
    rows = sorted(d, key=lambda r: r["datetime"])
    ts, lv, q = [], [], []
    for r in rows:
        t = datetime.datetime.strptime(r["datetime"], "%Y-%m-%d %H:%M")
        ts.append(t)
        lv.append(None if r.get("value") in (None, "") else float(r["value"]))
        q.append(None if r.get("discharge") in (None, "") else float(r["discharge"]))
    return ts, lv, q


def main():
    ts, lv, q = observed()
    obs_q = [(t, v) for t, v in zip(ts, q) if v is not None]
    obs_l = [(t, v) for t, v in zip(ts, lv) if v is not None]
    last_t = obs_l[-1][0]
    last_q, last_l = obs_q[-1][1], obs_l[-1][1]
    ft = [p[1] for p in RID_FORECAST]
    fq = [p[2] for p in RID_FORECAST]
    fl = [p[3] for p in RID_FORECAST]
    # join the last observation to the first forecast point so the dashed line is continuous
    fq_line = [last_q] + fq[1:]
    fl_line = [last_l] + fl[1:]
    ft_line = [last_t] + ft[1:]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11.5, 8.6), sharex=True)

    for ax, y, yf, unit in ((ax1, lv, fl_line, "level (m MSL)"), (ax2, q, fq_line, "discharge (m3/s)")):
        ax.plot(ts, y, color="#1f77b4", lw=1.6, marker=".", label="observed (thaiwater telemetry, hourly)")
        ax.axvspan(last_t, max(ft), color="#ffd6d6", alpha=.75, zorder=0)
        ax.plot(ft_line, yf, color="#d62728", lw=2.0, ls="--", marker="o", ms=5,
                label="FORECAST (shaded zone)")
        for (lab, t, qq, ll), v in zip(RID_FORECAST, yf):
            val = qq if unit.startswith("discharge") else ll
            ax.annotate(f"{val:,.2f}" if unit.startswith("level") else f"{val:,.0f}",
                        (t, v), textcoords="offset points", xytext=(6, 8), fontsize=9, color="#a00000")
        ax.axvline(last_t, color="#555", lw=1, ls=":")
        ax.set_ylabel(unit)
        ax.grid(alpha=.3)
        ax.legend(loc="upper left", fontsize=9)
        # data gaps: mark the hours with no reading
        gaps = [t for t, v in zip(ts, y) if v is None]
        for g in gaps:
            ax.axvline(g, color="#bbb", lw=.6, alpha=.4)

    ax1.annotate("last observed reading", (last_t, max(v for v in lv if v is not None)),
                 textcoords="offset points", xytext=(-135, 12), fontsize=9, color="#333",
                 arrowprops=dict(arrowstyle="-", color="#333", lw=.8))
    ax1.set_title("C.2 ค่ายจิรประวัติ — observed vs forecast\n" + FORECAST_ISSUED, fontsize=11)
    ax2.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 6, 12, 18]))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%d %b\n%H:%M"))
    ax2.set_xlim(min(ts), max(ft) + datetime.timedelta(hours=10))
    fig.autofmt_xdate(rotation=35)
    fig.tight_layout()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fig.savefig(OUT, dpi=110)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
