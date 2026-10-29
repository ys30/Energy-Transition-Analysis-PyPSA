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
        ("sort[1][column]", "respondent"), ("sort[1][direction]", "asc"),
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
    data["value"] = pd.to_numeric(data["value"], errors="coerce").astype("float64")
    if data.duplicated(["period", "respondent"]).any():
        raise ValueError("Duplicate balancing authority-hour rows")
    # EIA publishes BA-level reported values as received, including anomalies.
    # Preserve observations and audit any replacement. Do not silently set negatives to zero.
    data = data.sort_values(["respondent", "period"]).reset_index(drop=True)
    bad = data["value"].isna() | (data["value"] <= 0)
    data["raw_value"] = data["value"]
    data["qc_flag"] = bad.map({True: "missing_or_nonpositive", False: "observed"})
    # Enforce the QC threshold for EACH BA before attempting any imputation.
    # A concentrated failure must not be hidden by a pooled low anomaly rate.
    by_ba = data.assign(_bad=bad).groupby("respondent")["_bad"].agg(["sum", "count"])
    excessive = by_ba[by_ba["sum"] / by_ba["count"] > 0.01]
    if not excessive.empty:
        raise ValueError("BA-specific EIA demand QC exceeds 1%: " + excessive.to_json())
    n_bad = int(bad.sum())
    if n_bad:
        print(f"EIA demand QC: {n_bad} missing/nonpositive observations among {len(data)}", flush=True)
        # Diagnose consecutive missing blocks without modifying raw_values.
        # Short gaps <=3 hours use time interpolation; longer gaps up to 24h
        # use matching UTC hour on adjacent days (assumption, flagged).
        # A longer block is left unresolved and fails the run.
        for ba, idx in data.groupby("respondent").groups.items():
            subset = data.loc[idx].sort_values("period")
            vals = subset["value"].where(subset["value"] > 0).copy()
            missing = vals.isna()
            blocks = (missing != missing.shift(fill_value=False)).cumsum()
            for _, group in subset.loc[missing].groupby(blocks[missing]):
                positions = group.index
                length = len(positions)
                first = subset.index.get_loc(positions[0])
                last = subset.index.get_loc(positions[-1])
                before = first - 1
                after = last + 1
                if before < 0 or after >= len(subset):
                    continue
                # Demand must be consecutive hourly observations before imputing.
                periods = subset["period"].reset_index(drop=True)
                segment = periods.iloc[before:after + 1]
                if not segment.diff().dropna().eq(pd.Timedelta(hours=1)).all():
                    continue
                if length <= 3:
                    left = float(vals.iloc[before])
                    right = float(vals.iloc[after])
                    if pd.notna(left) and pd.notna(right):
                        for j, ix in enumerate(positions, 1):
                            data.loc[ix, "value"] = left + (right - left) * j / (length + 1)
                            data.loc[ix, "qc_flag"] = "interpolated_le3h"
                elif length <= 24:
                    # Same-hour previous/next day must both be observed.
                    for ix in positions:
                        pos = subset.index.get_loc(ix)
                        if pos - 24 < 0 or pos + 24 >= len(subset):
                            continue
                        prev = subset.iloc[pos - 24]
                        nxt = subset.iloc[pos + 24]
                        current = subset.loc[ix]
                        if (current["period"] - prev["period"] != pd.Timedelta(hours=24)
                            or nxt["period"] - current["period"] != pd.Timedelta(hours=24)):
                            continue
                        a = prev["raw_value"]
                        b = nxt["raw_value"]
                        if pd.notna(a) and pd.notna(b) and a > 0 and b > 0:
                            data.loc[ix, "value"] = (float(a) + float(b)) / 2
                            data.loc[ix, "qc_flag"] = "neighboring_day_imputation"
                print(f"  BA={ba} gap start={group.period.min()} length={length}h "
                      f"remaining={int(data.loc[positions, 'value'].isna().sum())}", flush=True)
        remaining = data["value"].isna() | (data["value"] <= 0)
        if remaining.any():
            examples = data.loc[remaining, ["period", "respondent", "raw_value"]].head(8).to_dict("records")
            raise ValueError(f"Unresolved EIA data quality: {int(remaining.sum())} rows; examples={examples}")
    data.attrs["qc_anomaly_rows"] = n_bad
    data.attrs["qc_fraction"] = n_bad / len(data)
    if n_bad / len(data) > 0.01:
        raise ValueError(f"Too many EIA anomalies: {n_bad}/{len(data)} > 1% QC limit")
    # A pooled threshold alone could conceal severe corruption in one small BA.
    by_ba = data.groupby("respondent").agg(
        rows=("value", "size"),
        anomalies=("qc_flag", lambda flags: int((flags != "observed").sum())),
    )
    by_ba["anomaly_share"] = by_ba.anomalies / by_ba.rows
    failed = by_ba.loc[by_ba.anomaly_share > 0.01]
    if not failed.empty:
        raise ValueError(f"BA-specific EIA QC anomaly rate > 1%: {failed.to_dict('index')}")
    present = set(data.respondent)
    if set(bas) - present:
        raise ValueError(f"Missing balancing authorities: {set(bas) - present}")
    # Verify full UTC hourly coverage, including absent timestamps shared by all BAs.
    expected = pd.date_range(f"{year}-01-01", f"{year+1}-01-01",
                             freq="h", inclusive="left", tz="UTC")
    actual = pd.DatetimeIndex(data["period"].unique()).sort_values()
    if not actual.equals(expected):
        missing = expected.difference(actual)
        unexpected = actual.difference(expected)
        raise ValueError(
            f"Incomplete hourly timestamp coverage for {year}: "
            f"missing={len(missing)}, unexpected={len(unexpected)}; "
            f"examples={list(missing[:5])}"
        )
    coverage = data.groupby("period").respondent.nunique()
    if len(coverage) != len(expected) or coverage.min() != len(bas):
        # A missing API record is distinct from a reported zero or NaN.
        # Report exact BA/time pairs rather than silently forward-filling them.
        complete = pd.MultiIndex.from_product(
            [expected, list(bas)], names=["period", "respondent"]
        )
        observed = pd.MultiIndex.from_frame(data[["period", "respondent"]])
        missing_pairs = complete.difference(observed)
        samples = [(str(t), ba) for t, ba in missing_pairs[:12]]
        raise ValueError(
            f"Incomplete BA coverage: {len(missing_pairs)} absent BA-hour records; "
            f"examples={samples}"
        )
    return data.sort_values(["period", "respondent"]).reset_index(drop=True)


def representative_hours(observations: pd.DataFrame, year: int):
    """Compress a fully observed BA-year to 288 UTC month-hour snapshots.

    For each month and UTC hour, average the summed hourly BA demand over all
    calendar days. Snapshot weights equal calendar days, so annual weighted
    MWh exactly preserves the input annual MWh (up to floating-point error).
    These snapshots cannot reproduce hourly extremes or chronological storage.
    """
    d = observations[["period", "respondent", "value"]].copy()
    d["period"] = pd.to_datetime(d["period"], utc=True, errors="raise")
    d["value"] = pd.to_numeric(d["value"], errors="raise")
    if d.empty or d["value"].isna().any() or (d["value"] <= 0).any():
        raise ValueError("Missing or nonpositive hourly demand")
    if d.duplicated(["period", "respondent"]).any():
        raise ValueError("Duplicate BA-hour demand observations")
    if not d["period"].dt.year.eq(year).all():
        raise ValueError("Input contains timestamps outside requested year")
    bas = d["respondent"].unique()
    expected = pd.date_range(f"{year}-01-01", f"{year+1}-01-01",
                             freq="h", inclusive="left", tz="UTC")
    if len(d) != len(expected) * len(bas):
        raise ValueError("Incomplete year: incorrect BA-hour observation count")
    for ba, part in d.groupby("respondent"):
        if not pd.DatetimeIndex(part["period"]).sort_values().equals(expected):
            raise ValueError(f"Incomplete year or missing hourly timestamps for BA {ba}")
    hourly = d.groupby("period", sort=True)["value"].sum()
    grouped = hourly.groupby([hourly.index.month, hourly.index.hour]).mean()
    rows = []
    for month in range(1, 13):
        days = calendar.monthrange(year, month)[1]
        for hour in range(24):
            rows.append((pd.Timestamp(year=year, month=month, day=15, hour=hour),
                         float(grouped.loc[(month, hour)]), days))
    rep = pd.DataFrame(rows, columns=["snapshot", "value", "weight_h"])
    raw_mwh = float(d["value"].sum())
    weighted_mwh = float((rep["value"] * rep["weight_h"]).sum())
    if abs(raw_mwh - weighted_mwh) > max(1e-5, abs(raw_mwh) * 1e-10):
        raise ValueError("Representative-hour energy conservation failed")
    return rep

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
        requested = set(args.bas)
        observed = set(counts["respondent"])
        if observed != requested:
            raise ValueError(
                f"BA coverage mismatch for {year}: missing={sorted(requested-observed)}, "
                f"unexpected={sorted(observed-requested)}"
            )
        counts["input_source"] = "EIA-930 hourly reported demand, type D"
        counts["observed_energy_units"] = "MWh"
        counts["peak_units"] = "MW"
        counts["expected_hours"] = 8784 if calendar.isleap(year) else 8760
        counts["coverage_fraction"] = counts["observations"] / counts["expected_hours"]
        if "raw_value" in hourly:
            raw_audit = hourly.groupby("respondent").agg(
                raw_observed_energy_mwh=("raw_value", "sum"),
                raw_nonpositive_or_missing_hours=("raw_value", lambda x: int((x.isna() | (x <= 0)).sum())),
            )
            counts["raw_observed_energy_mwh"] = counts.respondent.map(raw_audit.raw_observed_energy_mwh)
            counts["raw_nonpositive_or_missing_hours"] = counts.respondent.map(raw_audit.raw_nonpositive_or_missing_hours)
        if "qc_flag" in hourly:
            bad = hourly.assign(interpolated=hourly.qc_flag.str.startswith(("interpolated_", "neighboring_day_"))).groupby("respondent").interpolated.sum()
            counts["interpolated_hours"] = counts.respondent.map(bad).fillna(0).astype(int)
            counts["imputation_share"] = counts["interpolated_hours"] / counts["expected_hours"]
        expected_hours = 8784 if calendar.isleap(year) else 8760
        if (counts.observations != expected_hours).any():
            raise ValueError(f"BA year incomplete, expected {expected_hours} hourly records each: {counts.to_dict('records')}")
        counts.to_csv(args.output / f"ba_audit_{year}.csv", index=False)
        rep = representative_hours(hourly, year)
        raw_energy = float(hourly["value"].sum())
        represented_energy = float((rep["value"] * rep["weight_h"]).sum())
        energy_audit = {
            "year": year,
            "balancing_authorities": sorted(hourly.respondent.unique().tolist()),
            "hourly_rows": int(len(hourly)),
            "raw_demand_mwh_after_qc": raw_energy,
            "representative_demand_mwh": represented_energy,
            "absolute_energy_difference_mwh": abs(raw_energy - represented_energy),
            "relative_energy_difference": abs(raw_energy - represented_energy) / raw_energy,
            "peak_observed_mw": float(hourly.groupby("period")["value"].sum().max()),
            "peak_representative_mw": float(rep["value"].max()),
            "peak_information_loss_warning": "Representative hours smooth observed peaks; do not use for adequacy or extreme-weather claims.",
        }
        (args.output / f"energy_audit_{year}.json").write_text(json.dumps(energy_audit, indent=2))
        rep.to_csv(args.output / f"representative_hours_{year}.csv", index=False)
        result = build_and_solve(rep, args.output / str(year))
        results.append({"year": year, **{k: v for k, v in result.items() if isinstance(v, (int, float, str))}})
    pd.DataFrame(results).to_csv(args.output / "yearly_summary.csv", index=False)


if __name__ == "__main__":
    main()
