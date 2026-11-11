"""Synthetic-only Paper T downstream timing sensitivity; no EFS/ReEDS physical-hour join."""
import argparse
import csv
import json
import math
from pathlib import Path

N = 8760

def profiles():
    demand, solar = [], []
    for t in range(N):
        day, hour = divmod(t, 24)
        summer = (1 + math.cos(2 * math.pi * (day - 200) / 365)) / 2
        evening = math.exp(-0.5 * ((hour - 19) / 3.2) ** 2)
        morning = math.exp(-0.5 * ((hour - 8) / 2.2) ** 2)
        demand.append(850 + 150 * summer + 300 * evening + 90 * morning)
        daylight = max(0., math.sin(math.pi * (hour - 6) / 12))
        solar.append((850 + 450 * summer) * daylight ** 1.65)
    return demand, solar

def shift(x, lag):
    """Negative lag moves a demand value to an earlier index; circular year."""
    return [x[(t - lag) % len(x)] for t in range(len(x))]

def calculate(demand, solar, lag):
    d = shift(demand, lag)
    net = [a - b for a, b in zip(d, solar)]
    peak = max(net)
    overlap = sum(min(a, b) for a, b in zip(d, solar))
    return dict(
        lag_h=lag,
        peak_mw=round(peak, 6),
        peak_hour_index=net.index(peak),
        peak_clock_hour=net.index(peak) % 24,
        demand_mwh=round(sum(d), 6),
        solar_mwh=round(sum(solar), 6),
        coincident_solar_mwh=round(overlap, 6),
        solar_overlap_fraction=round(overlap / sum(solar), 8),
        potential_solar_surplus_mwh=round(sum(max(0, b - a) for a, b in zip(d, solar)), 6),
    )

def run():
    d, s = profiles()
    rows = [calculate(d, s, lag) for lag in (0, -2, -3)]
    base = rows[0]
    for row in rows:
        row["peak_delta_mw"] = round(row["peak_mw"] - base["peak_mw"], 6)
        row["peak_delta_pct"] = round(100 * (row["peak_mw"] / base["peak_mw"] - 1), 6)
        row["overlap_delta_pp"] = round(100 * (row["solar_overlap_fraction"] - base["solar_overlap_fraction"]), 6)
    return rows

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", type=Path, default=Path("results/paper_t_hypothetical_downstream"))
    out = parser.parse_args().outdir
    out.mkdir(parents=True, exist_ok=True)
    rows = run()
    with (out / "sensitivity.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (out / "metadata.json").write_text(json.dumps({
        "classification": "HYPOTHETICAL SYNTHETIC-ONLY, NOT OBSERVATIONAL",
        "profiles": "Both demand and solar are stylized normalized MW, not EFS/ReEDS or weather data",
        "time_index": "365 x 24 index slots, no DST, circular year",
        "lag_convention": "-2 h advances the demand series by two time indices against fixed solar",
        "boundary": "Annual energy conserved, year boundary wraps; no physical-hour join certified",
        "limitations": "Peak and overlap magnitudes depend on assumed profiles; no real-grid causal or operational inference",
        "results": rows
    }, indent=2) + "\n")
    print(json.dumps(rows, indent=2))

if __name__ == "__main__":
    main()
