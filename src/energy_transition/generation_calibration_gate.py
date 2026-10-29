"""Guardrail for EIA-930 observed generation calibration.

Reject incomplete annual observations. Never turn partial annual sums into full
year statistics or silently impute missing source generation hours.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import pandas as pd

def validate_annual_generation(audit: pd.DataFrame, bas):
    required={"ba_code","complete","missing_timestamp_hours","missing_value_hours","outside_year_hours"}
    if required-set(audit):
        raise ValueError(f"Missing audit fields: {sorted(required-set(audit))}")
    if audit.ba_code.duplicated().any():
        raise ValueError("Duplicate BA rows in generation audit")
    selected=audit[audit.ba_code.isin(bas)].copy()
    if set(selected.ba_code)!=set(bas):
        raise ValueError(f"Missing requested BAs: {sorted(set(bas)-set(selected.ba_code))}")
    complete=selected.complete.astype(str).str.strip().str.lower().eq("true")
    good=complete & selected[["missing_timestamp_hours","missing_value_hours","outside_year_hours"]].eq(0).all(axis=1)
    return selected.assign(ready_for_annual_calibration=good,
                           calibration_status=good.map({True:"complete",False:"incomplete_exclude"}))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--audit",type=Path,required=True)
    p.add_argument("--bas",nargs="+",default=["CISO","BPAT"])
    p.add_argument("--output",type=Path,default=Path("outputs/generation_gate"))
    a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=True)
    result=validate_annual_generation(pd.read_csv(a.audit),a.bas)
    result.to_csv(a.output/"generation_calibration_readiness.csv",index=False)
    report={"requested_bas":a.bas,
            "ready_bas":result.loc[result.ready_for_annual_calibration,"ba_code"].tolist(),
            "excluded_bas":result.loc[~result.ready_for_annual_calibration,"ba_code"].tolist(),
            "rule":"Complete annual timestamp and value coverage required; no silent imputation."}
    (a.output/"readiness_manifest.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))

if __name__=="__main__":
    main()
