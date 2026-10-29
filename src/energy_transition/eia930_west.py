"""EIA-930 observed hourly demand -> transparent Western US PyPSA dispatch case.

This is NOT a calibrated WECC network, an investment forecast, or a verified grid simulation.
Only demand is observed. Supply, prices, emissions, and capacity factors are assumptions.
"""
from __future__ import annotations

import argparse
import calendar
import json
import os
from pathlib import Path
import time
import urllib.parse
import urllib.request

import pandas as pd

API = "https://api.eia.gov/v2/electricity/rto/region-data/data/"
# A documented, non-exhaustive subset of western balancing authorities.
DEFAULT_BAS = ("CISO", "BPAT", "PACE", "PACW", "AZPS", "NEVP", "PNM", "IPCO")
CARRIERS = {
    "gas": dict(p_nom=100000, marginal_cost=65, co2_emissions=0.40),
    "wind": dict(p_nom=24000, marginal_cost=2, co2_emissions=0),
    "solar": dict(p_nom=26000, marginal_cost=2, co2_emissions=0),
}
# Explicit *scenario assumptions*, not reported generation capacity or renewable resource data.
AVAILABILITY = {"gas": 1.0, "wind": 0.35, "solar": 0.26}


def fetch_eia_demand(year: int, bas=DEFAULT_BAS, api_key=None, length=5000):
    """Fetch EIA-930 hourly reported demand (MW), paginating with deterministic sorting."""
    key = api_key or os.getenv("EIA_API_KEY")
    if not key:
        raise ValueError("Set EIA_API_KEY. An EIA API key is required for this workflow.")
    if not bas:
        raise ValueError("At least one balancing authority is required")
    params = [
        ("api_key", key), ("frequency", "hourly"), ("data[0]", "value"),
        ("facets[type][]", "D"), ("start", f"{year}-01-01T00"),
        ("end", f"{year}-12-31T23"), ("length", str(length)),
        ("sort[0][column]", "period"), ("sort[0][direction]", "asc"),
    ]
    params += [("facets[respondent][]", ba) for ba in bas]
    offset = 0
    frames = []
    total = None
    while total is None or offset < total:
        query = urllib.parse.urlencode(params + [("offset", str(offset))])
        request = urllib.request.Request(API + "?" + query,
                                         headers={"User-Agent": "pypsa-western-us-research/0.1"})
        for attempt in range(4):
            try:
                with urllib.request.urlopen(request, timeout=60) as response:
                    payload = json.load(response)
                break
            except Exception:
                if attempt == 3:
                    raise
                time.sleep(2 ** attempt)
        result = payload.get("response", {})
        if "data" not in result:
            raise ValueError(f"EIA response missing data: {str(payload)[:250]}")
        rows = result["data"]
        total = int(result.get("total", 0))
        if not rows:
            break
        frames.append(pd.DataFrame(rows))
        offset += len(rows)
    if not frames:
        raise ValueError(f"No EIA demand observations for {year} and {bas}")
    data = pd.concat(frames, ignore_index=True)
    require = {"period", "respondent", "value"}
    if not require.issubset(data.columns):
        raise ValueError(f"Missing fields: {require - set(data.columns)}")
    data = data[["period", "respondent", "value"]].copy()
    data["period"] = pd.to_datetime(data["period"], utc=True, errors="raise")
    data["value"] = pd.to_numeric(data["value"], errors="coerce")
    if data.duplicated(["period", "respondent"]).any():
        raise ValueError("Duplicate balancing authority-hour rows")
    # EIA publishes BA-level reported values as received, including anomalies.
    # Preserve observations and audit any replacement. Do not silently set negatives to zero.
    data = data.sort_values(["respondent", "period"]).reset_index(drop=True)
    bad = data["value"].isna() | (data["value"] <= 0)
    data["raw_value"] = data["value"]
    data["qc_flag"] = bad.map({True: "missing_or_nonpositive", False: "observed"})
    n_bad = int(bad.sum())
    if n_bad:
        print(f"EIA demand QC: {n_bad} missing/nonpositive observations among {len(data)}", flush=True)
        # Per-BA local time-series interpolation is used only for isolated gaps,
        # never for a full missing BA or long gaps. Preserve raw_values and flags.
        for ba, idx in data.groupby("respondent").groups.items():
            subset = data.loc[idx].sort_values("period")
            v = subset["value"].where(subset["value"] > 0)
            filled = v.interpolate(method="linear", limit=3, limit_area="inside")
            replaced = v.isna() & filled.notna()
            data.loc[subset.index, "value"] = filled
            data.loc[subset.index[replaced], "qc_flag"] = "interpolated_max_3h"
        remaining = data["value"].isna() | (data["value"] <= 0)
        if remaining.any():
            examples = data.loc[remaining, ["period", "respondent", "raw_value"]].head(8).to_dict("records")
            raise ValueError(f"Unresolved EIA data quality: {int(remaining.sum())} rows; examples={examples}")
    data.attrs["qc_anomaly_rows"] = n_bad
    data.attrs["qc_fraction"] = n_bad / len(data)
    if n_bad / len(data) > 0.01:
        raise ValueError(f"Too many EIA anomalies: {n_bad}/{len(data)} > 1% QC limit")
    present = set(data.respondent)
    if set(bas) - present:
        raise ValueError(f"Missing balancing authorities: {set(bas) - present}")
    if data.groupby("period").respondent.nunique().min() != len(bas):
        raise ValueError("Incomplete BA coverage in at least one hourly snapshot")
    return data.sort_values(["period", "respondent"]).reset_index(drop=True)


def representative_hours(observations: pd.DataFrame, year: int):
    """Observed BA loads averaged by UTC month and hour; every 24h block represents its month.

    Weight is number of calendar days represented. Full calendar year must be present.
    This compresses variation and must NOT be used for reliability or adequacy analysis.
    """
    d = observations.copy()
    d["period"] = pd.to_datetime(d["period"], utc=True)
    d["month"] = d.period.dt.month
    d["hour"] = d.period.dt.hour
    # All 12 months and each hour of each month are required.
    counts = d.groupby(["month", "hour"]).period.nunique()
    if len(counts) != 288 or counts.min() < 20:
        raise ValueError("Incomplete year/month/hour demand input")
    d = d.groupby(["month", "hour"], as_index=False)["value"].sum()
    d = d.groupby(["month", "hour"], as_index=False)["value"].mean()
    # The first grouping sums BA demand per month/hour; divide by observed number of days.
    days_seen = observations.assign(month=lambda x: pd.to_datetime(x.period, utc=True).dt.month,
                                    hour=lambda x: pd.to_datetime(x.period, utc=True).dt.hour)
    n_days = days_seen.groupby(["month", "hour"]).period.nunique()
    d["value"] = [v / n_days.loc[m, h] for m, h, v in d[["month", "hour", "value"]].itertuples(index=False, name=None)]
    # Use fixed representative timestamps for every month: UTC 15th.
    d["snapshot"] = pd.to_datetime([f"{year}-{m:02d}-15 {h:02d}:00" for m, h in zip(d.month, d.hour)])
    d["weight_h"] = [calendar.monthrange(year, m)[1] for m in d.month]
    return d[["snapshot", "value", "weight_h"]].sort_values("snapshot").reset_index(drop=True)


def build_and_solve(reps: pd.DataFrame, output: Path):
    import pypsa
    n = pypsa.Network()
    n.add("Bus", "western_subset")
    snapshots = pd.DatetimeIndex(reps.snapshot)
    n.set_snapshots(snapshots)
    n.snapshot_weightings.loc[:, ["objective", "generators", "stores"]] = reps.weight_h.to_numpy()[:, None]
    n.add("Load", "eia930_observed_demand", bus="western_subset", p_set=reps.value.to_numpy())
    for carrier, cfg in CARRIERS.items():
        n.add("Carrier", carrier, co2_emissions=cfg["co2_emissions"])
        n.add("Generator", carrier, bus="western_subset", carrier=carrier,
              p_nom=cfg["p_nom"], marginal_cost=cfg["marginal_cost"],
              p_max_pu=AVAILABILITY[carrier])
    # Load shedding makes infeasibility visible; it must never be mistaken for physical generation.
    n.add("Generator", "unserved", bus="western_subset", p_nom=1e7,
          marginal_cost=10000)
    status, condition = n.optimize(solver_name="highs")
    if status != "ok" or condition != "optimal":
        raise RuntimeError(f"PyPSA did not solve: {status}, {condition}")
    generation = n.generators_t.p.mul(reps.weight_h.to_numpy(), axis=0).sum()
    total_mwh = float((reps.value * reps.weight_h).sum())
    unserved_mwh = float(generation["unserved"])
    result = {
        "solve_status": condition, "observed_demand_mwh": total_mwh,
        "unserved_mwh": unserved_mwh, "unserved_share": unserved_mwh / total_mwh,
        "dispatch_mwh_by_carrier": {k: float(generation[k]) for k in CARRIERS},
        "operational_tco2_assumed": float(sum(generation[k] * CARRIERS[k]["co2_emissions"] for k in CARRIERS)),
        "objective_usd_assumed": float(n.objective),
        "evidence_boundary": "Observed EIA-930 BA demand; assumed technology supply, prices and emissions; no network constraints or investment optimization."
    }
    output.mkdir(parents=True, exist_ok=True)
    n.export_to_netcdf(output / "solved_network.nc")
    (output / "metrics.json").write_text(json.dumps(result, indent=2))
    return result


def main():
    p = argparse.ArgumentParser(description="EIA-930 based, assumption-driven Western BA PyPSA dispatch")
    p.add_argument("--years", type=int, nargs="+", default=[2023, 2024])
    p.add_argument("--bas", nargs="+", default=list(DEFAULT_BAS))
    p.add_argument("--output", type=Path, default=Path("outputs/eia930_west"))
    p.add_argument("--cached", action="store_true", help="Use previously downloaded per-year CSVs; never synthesize inputs")
    args = p.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    manifest = {"source": "EIA-930 region-data hourly actual demand, type D",
                "source_url": API, "respondents": args.bas,
                "units": "MW", "years": args.years, "model": "single-bus economic dispatch; assumed supply"}
    (args.output / "input_manifest.json").write_text(json.dumps(manifest, indent=2))
    results = []
    for year in args.years:
        raw = args.output / f"eia930_demand_{year}.csv"
        if args.cached:
            if not raw.exists():
                raise FileNotFoundError(raw)
            hourly = pd.read_csv(raw)
        else:
            hourly = fetch_eia_demand(year, args.bas)
            hourly.to_csv(raw, index=False)
        # Region-specific observed-demand audit, before aggregation into one model bus.
        hourly["period"] = pd.to_datetime(hourly["period"], utc=True)
        counts = hourly.groupby("respondent").agg(
            observations=("value", "size"),
            observed_energy_mwh=("value", "sum"),
            peak_mw=("value", "max"),
        ).reset_index()
        counts["year"] = year
        if "qc_flag" in hourly:
            bad = hourly.assign(interpolated=hourly.qc_flag.eq("interpolated_max_3h")).groupby("respondent").interpolated.sum()
            counts["interpolated_hours"] = counts.respondent.map(bad).fillna(0).astype(int)
        expected_hours = 8784 if calendar.isleap(year) else 8760
        if (counts.observations != expected_hours).any():
            raise ValueError(f"BA year incomplete, expected {expected_hours} hourly records each: {counts.to_dict('records')}")
        counts.to_csv(args.output / f"ba_audit_{year}.csv", index=False)
        rep = representative_hours(hourly, year)
        rep.to_csv(args.output / f"representative_hours_{year}.csv", index=False)
        result = build_and_solve(rep, args.output / str(year))
        results.append({"year": year, **{k: v for k, v in result.items() if isinstance(v, (int, float, str))}})
    pd.DataFrame(results).to_csv(args.output / "yearly_summary.csv", index=False)


if __name__ == "__main__":
    main()
