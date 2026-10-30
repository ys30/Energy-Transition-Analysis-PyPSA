"""Conservative EIA-930 observed-vs-modeled hourly generation diagnostics.

Requires actual 1-hour UTC timestamps. Never interpolates gaps, expands
representative hours, or labels a descriptive comparison calibrated.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd


def compare_hourly(observed: pd.DataFrame, modeled: pd.DataFrame, year: int, bas):
    """Return aligned BA-hour observations and BA-level descriptive error metrics.

    Both inputs contain respondent, period, value (MW). A metric is reported
    only for fully observed overlapping hours; coverage is against all year hours.
    """
    if not bas or len(set(bas)) != len(bas):
        raise ValueError("Expected nonempty, unique BA list")
    expected = pd.date_range(f"{year}-01-01", f"{year+1}-01-01", freq="h",
                             inclusive="left", tz="UTC")
    grid = pd.MultiIndex.from_product([bas, expected], names=["respondent", "period"])
    values = {}
    for label, frame in (("observed", observed), ("modeled", modeled)):
        if {"respondent", "period", "value"} - set(frame):
            raise ValueError(f"{label}: expected respondent, period and value")
        data = frame[["respondent", "period", "value"]].copy()
        data["period"] = pd.to_datetime(data.period, utc=True, errors="coerce")
        if data.period.isna().any() or not data.respondent.isin(bas).all():
            raise ValueError(f"{label}: invalid timestamp or out-of-scope BA")
        if (~data.period.isin(expected)).any():
            raise ValueError(f"{label}: outside calendar year or non-hourly timestamp")
        if data.duplicated(["respondent", "period"]).any():
            raise ValueError(f"{label}: duplicate BA-hour observations")
        data["value"] = pd.to_numeric(data.value, errors="coerce")
        if np.isinf(data.value.to_numpy(dtype=float)).any():
            raise ValueError(f"{label}: infinite MW values")
        # Explicitly reject nonnumeric strings instead of silently turning
        # malformed source values into missing-hour coverage.
        raw_nonmissing = frame["value"].notna().to_numpy()
        if (raw_nonmissing & data["value"].isna().to_numpy()).any():
            raise ValueError(f"{label}: nonnumeric MW value")

        # Missing observations remain NaN for coverage accounting, but
        # negative net generation is not a valid positive-output comparison.
        if label == "modeled" and (data["value"].dropna() < -1e-6).any():
            raise ValueError("modeled: negative generator production")
        # EIA-930 BA net-generation may legitimately be negative at some
        # hours; preserve its sign and report those observations separately.


        values[label] = data.set_index(["respondent", "period"]).value.reindex(grid)
    pairs = pd.DataFrame(values).reset_index()
    pairs["complete_pair"] = pairs[["observed", "modeled"]].notna().all(axis=1)
    pairs["model_minus_observed_mw"] = (pairs.modeled-pairs.observed).where(pairs.complete_pair)
    result = []
    for ba in bas:
        data = pairs[pairs.respondent.eq(ba)]
        good = data[data.complete_pair]
        residual = good.model_minus_observed_mw
        result.append({
            "ba_code": ba,
            "expected_hours": len(expected),
            "observed_hours": int(data.observed.notna().sum()),
            "modeled_hours": int(data.modeled.notna().sum()),
            "paired_hours": len(good),
            "paired_coverage": len(good)/len(expected),
            "observed_negative_hours": int((data.observed < 0).sum()),
            "observed_zero_hours": int(data.observed.eq(0).sum()),
            "mae_mw": float(residual.abs().mean()) if len(good) else np.nan,
            "rmse_mw": float(np.sqrt((residual**2).mean())) if len(good) else np.nan,
            "peak_absolute_error_mw": float(residual.abs().max()) if len(good) else np.nan,
            "mean_bias_mw": float(residual.mean()) if len(good) else np.nan,
            "comparison_status": "complete_hourly_descriptive" if len(good)==len(expected)
                else "partial_hours_not_calibrated",
            "validated_calibration": False,
        })
    return pairs, pd.DataFrame(result)



def extract_full_year_dispatch(network, year: int, bas):
    """Export BA hourly generator production only for real full-year UTC snapshots.

    Storage, cross-border flows and synthetic unserved energy are excluded;
    generation alone is not the full accounting identity.
    """
    expected=pd.date_range(f"{year}-01-01",f"{year+1}-01-01",
                           freq="h",inclusive="left",tz="UTC")
    snapshots=pd.DatetimeIndex(network.snapshots)
    if snapshots.tz is None:
        raise ValueError("PyPSA snapshots require an explicit UTC timezone")
    if not snapshots.tz_convert("UTC").equals(expected):
        raise ValueError("Full-year hourly UTC snapshots required; representative hours cannot be expanded")
    dispatch=network.generators_t.p
    if not dispatch.index.equals(network.snapshots):
        raise ValueError("PyPSA dispatch index differs from snapshots")
    if network.generators.index.has_duplicates or dispatch.columns.has_duplicates:
        raise ValueError("Duplicate PyPSA generators")
    records=[]
    for ba in bas:
        columns=[]
        for name,row in network.generators.iterrows():
            if str(row.bus)!=ba:
                continue
            if not str(name).startswith(ba+"_"):
                raise ValueError("Ambiguous BA generator prefix")
            if str(name)==ba+"_unserved":
                continue
            if name not in dispatch.columns:
                raise ValueError("Missing PyPSA generator dispatch")
            columns.append(name)
        if not columns:
            continue
        production=dispatch[columns].apply(pd.to_numeric,errors="coerce")
        if not np.isfinite(production.to_numpy(dtype=float)).all():
            raise ValueError("Nonfinite PyPSA generation")
        records.append(pd.DataFrame({
            "respondent":ba,"period":expected,
            "value":production.sum(axis=1).to_numpy(dtype=float)
        }))
    return pd.concat(records,ignore_index=True) if records else pd.DataFrame(
        columns=["respondent","period","value"])


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--observed",type=Path,required=True)
    parser.add_argument("--modeled",type=Path,help="Prepared BA-hour modeled MW CSV")
    parser.add_argument("--network",type=Path,help="Solved full-year PyPSA NetCDF, not representative-hour network")
    parser.add_argument("--year",type=int,default=2024)
    parser.add_argument("--bas",nargs="+",default=["CISO","BPAT"])
    parser.add_argument("--output",type=Path,default=Path("outputs/hourly_generation_comparison"))
    args=parser.parse_args()
    if bool(args.modeled) == bool(args.network):
        parser.error("Supply exactly one of --modeled or --network")
    args.output.mkdir(parents=True,exist_ok=True)
    if args.network:
        import pypsa
        modeled=extract_full_year_dispatch(pypsa.Network(args.network),args.year,args.bas)
    else:
        modeled=pd.read_csv(args.modeled)
    pairs,summary=compare_hourly(pd.read_csv(args.observed),modeled,
                                 args.year,args.bas)
    pairs.to_csv(args.output/"hourly_pairs.csv",index=False)
    summary.to_csv(args.output/"ba_hourly_error_summary.csv",index=False)
    print(summary.to_string(index=False))


if __name__=="__main__":
    main()
