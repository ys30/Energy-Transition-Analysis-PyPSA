"""Diagnose hourly EIA-930 official BA accounting residuals, without recalibration.

Inputs contain D, NG, and TI observations from the previously audited 2024
pipeline. Analyses are descriptive; a large residual does not establish
a transmission schedule, missing imports, or the source of reporting error.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd


def diagnose(hourly: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    expected = {"respondent", "period", "demand", "generation", "interchange"}
    if expected - set(hourly):
        raise ValueError(f"Missing hourly fields: {sorted(expected - set(hourly))}")
    d = hourly.copy()
    d["period"] = pd.to_datetime(d["period"], utc=True, errors="raise")
    if d.duplicated(["respondent", "period"]).any():
        raise ValueError("Duplicate BA-hour records")
    for key in ("demand", "generation", "interchange"):
        d[key] = pd.to_numeric(d[key], errors="coerce")
    d["month"] = d.period.dt.strftime("%Y-%m")
    d["valid_triple"] = d[["demand", "generation", "interchange"]].notna().all(axis=1)
    v = d[d.valid_triple].copy()
    v["official_residual_mw"] = v.demand - v.generation + v.interchange
    v["generation_minus_demand_mw"] = v.generation - v.demand
    v["abs_official_residual_mw"] = v.official_residual_mw.abs()
    v["positive_residual"] = v.official_residual_mw.gt(0)
    v["negative_residual"] = v.official_residual_mw.lt(0)
    monthly = v.groupby(["respondent", "month"], as_index=False).agg(
        common_hours=("period", "size"),
        sum_demand_mwh=("demand", "sum"),
        sum_generation_mwh=("generation", "sum"),
        sum_interchange_mwh=("interchange", "sum"),
        sum_official_residual_mwh=("official_residual_mw", "sum"),
        median_official_residual_mw=("official_residual_mw", "median"),
        mae_official_residual_mw=("abs_official_residual_mw", "mean"),
        p95_absolute_residual_mw=("abs_official_residual_mw", lambda x: float(x.quantile(.95))),
        positive_residual_hours=("positive_residual", "sum"),
        negative_residual_hours=("negative_residual", "sum"),
    )
    expected_counts = d.groupby(["respondent", "month"]).size().rename("expected_hours").reset_index()
    monthly = expected_counts.merge(monthly, on=["respondent", "month"], how="left")
    monthly["coverage_share"] = monthly.common_hours / monthly.expected_hours
    monthly["residual_share_of_demand"] = monthly.sum_official_residual_mwh / monthly.sum_demand_mwh
    # Only compare on the identical complete-hour sample; avoid imputing NG or TI.
    by_ba = []
    for ba, subset in v.groupby("respondent"):
        correlation = subset[["interchange", "generation_minus_demand_mw"]].corr().iloc[0, 1]
        by_ba.append({
            "respondent": ba,
            "common_hours": len(subset),
            "positive_residual_share": float(subset.positive_residual.mean()),
            "negative_residual_share": float(subset.negative_residual.mean()),
            "median_hourly_residual_mw": float(subset.official_residual_mw.median()),
            "sum_residual_mwh": float(subset.official_residual_mw.sum()),
            "p95_absolute_residual_mw": float(subset.abs_official_residual_mw.quantile(.95)),
            "ti_vs_generation_minus_demand_correlation": (
                float(correlation) if pd.notna(correlation) else np.nan
            ),
            "classification": "diagnostic_only_not_transmission_calibration",
        })
    return monthly, pd.DataFrame(by_ba)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--hourly", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    monthly, overview = diagnose(pd.read_csv(args.hourly))
    monthly.to_csv(args.output / "interchange_monthly_diagnostics.csv", index=False)
    overview.to_csv(args.output / "interchange_ba_diagnostics.csv", index=False)
    (args.output / "diagnostics_provenance.json").write_text(json.dumps({
        "definition": "official residual = EIA-930 D - NG + TI",
        "units": "MW hourly, MWh sum of hourly MW observations",
        "handling": "Only BA-hour records where all three original series exist are compared.",
        "limitations": [
            "Descriptive QA only; does not infer the cause of any discrepancy.",
            "No gap filling or transmission capacity inference.",
            "Hourly load was previously subjected to the EIA-930 audited QC process.",
        ],
    }, indent=2))
    print(overview.to_string(index=False))


if __name__ == "__main__":
    main()
