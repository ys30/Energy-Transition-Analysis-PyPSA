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
            "mae_mw": float(residual.abs().mean()) if len(good) else np.nan,
            "rmse_mw": float(np.sqrt((residual**2).mean())) if len(good) else np.nan,
            "peak_absolute_error_mw": float(residual.abs().max()) if len(good) else np.nan,
            "mean_bias_mw": float(residual.mean()) if len(good) else np.nan,
            "comparison_status": "complete_hourly_descriptive" if len(good)==len(expected)
                else "partial_hours_not_calibrated",
            "validated_calibration": False,
        })
    return pairs, pd.DataFrame(result)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--observed",type=Path,required=True)
    parser.add_argument("--modeled",type=Path,required=True)
    parser.add_argument("--year",type=int,default=2024)
    parser.add_argument("--bas",nargs="+",default=["CISO","BPAT"])
    parser.add_argument("--output",type=Path,default=Path("outputs/hourly_generation_comparison"))
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    pairs,summary=compare_hourly(pd.read_csv(args.observed),pd.read_csv(args.modeled),
                                 args.year,args.bas)
    pairs.to_csv(args.output/"hourly_pairs.csv",index=False)
    summary.to_csv(args.output/"ba_hourly_error_summary.csv",index=False)
    print(summary.to_string(index=False))


if __name__=="__main__":
    main()
