"""Machine-readable eligibility gate for observed EIA-930 BA interchange.

This is a conservative screening gate, not certification of BA interchange
statistics. An anomalous BA must not be used to infer net imports or line ratings.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import pandas as pd
import numpy as np


def evaluate(summary: pd.DataFrame, monthly: pd.DataFrame) -> list[dict]:
    needed={"respondent","complete_triple_share","official_balance_mae_share_of_load"}
    if needed-set(summary.columns):
        raise ValueError("Missing annual BA balance audit fields")
    if {"respondent","month","coverage","residual_share_of_demand"}-set(monthly.columns):
        raise ValueError("Missing monthly BA balance audit fields")
    if summary.respondent.duplicated().any() or monthly.duplicated(["respondent","month"]).any():
        raise ValueError("Duplicate BA/year or BA/month records")
    decisions=[]
    for _,row in summary.iterrows():
        ba=row.respondent
        months=monthly[monthly.respondent.eq(ba)]
        if len(months)!=12:
            raise ValueError(f"Expected 12 monthly BA records for {ba}; got {len(months)}")
        parsed_months=pd.to_datetime(months["month"],format="%Y-%m",errors="coerce")
        if parsed_months.isna().any() or parsed_months.dt.year.nunique()!=1 or set(parsed_months.dt.month)!=(set(range(1,13))):
            raise ValueError(f"Expected exactly January-December of one year for {ba}")
        poor_coverage=int(months.coverage.lt(.99).sum())
        bad_balance=int(months.residual_share_of_demand.abs().gt(.10).sum())
        coverage=float(row.complete_triple_share)
        mae=float(row.official_balance_mae_share_of_load)
        numeric=months[["coverage","residual_share_of_demand"]].apply(pd.to_numeric,errors="coerce")
        numeric_ok=bool(np.isfinite([coverage,mae]).all() and np.isfinite(numeric.to_numpy()).all())
        bounds_ok=bool(0 <= coverage <= 1 and mae >= 0 and numeric["coverage"].between(0,1).all())
        quality_ok=("quality_flag" not in months or
                    months["quality_flag"].eq("screening_only_not_verified").all())
        if "annual_max_residual_share_of_load" in summary:
            tail=pd.to_numeric(row.annual_max_residual_share_of_load,errors="coerce")
            tail_ok=bool(np.isfinite(tail) and tail<=.50)
        else:
            tail_ok=True
        eligible=bool(numeric_ok and bounds_ok and quality_ok and tail_ok and coverage>=.99
                      and mae<=.10 and poor_coverage==0 and bad_balance==0)
        decisions.append({"ba_code":ba,"interchange_calibration_eligible":eligible,
          "coverage_share":coverage,"official_mae_share_of_load":mae,
          "months_below_99pct_coverage":poor_coverage,
          "months_over_10pct_residual":bad_balance,
          "reason":"screening_gate_passed_not_independent_validation" if eligible
              else "EIA930_interchange_screening_failed",
          "warning":"A passed screening gate does not verify interchange reporting boundaries or transmission capacity."})
    return decisions


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--summary",type=Path,required=True)
    p.add_argument("--monthly",type=Path,required=True)
    p.add_argument("--output",type=Path,default=Path("outputs/eia930_balance"))
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    decisions=evaluate(pd.read_csv(a.summary),pd.read_csv(a.monthly))
    (a.output/"interchange_calibration_gate.json").write_text(json.dumps({
      "policy":"Do not infer net imports or transmission capacity from failed BA records.",
      "criteria":{"annual_complete_hour_fraction_min":.99,
                  "monthly_complete_hour_fraction_min":.99,
                  "monthly_absolute_energy_residual_fraction_max":.10,
                  "annual_mean_absolute_residual_fraction_max":.10},
      "decisions":decisions},indent=2))
    print(json.dumps(decisions,indent=2))


if __name__=="__main__":
    main()
