"""Qualify official EIA-923 BA/fuel annual observations before model comparison.

Only original Page 1 rows whose 12 monthly values reconcile with their
reported annual values contribute to certified totals. Do not substitute zeros
for incomplete rows; publish the withheld annual amounts separately.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import pandas as pd

def qualify(reconciliation:pd.DataFrame):
    required={"source_row_id","ba_code","fuel","annual_reported_mwh",
              "reconciles","fully_numeric","missing_months"}
    missing=required-set(reconciliation)
    if missing:raise ValueError(f"Missing EIA-923 audit columns: {sorted(missing)}")
    x=reconciliation.copy()
    if x.source_row_id.duplicated().any():
        raise ValueError("Duplicate original EIA-923 source row ID")
    x["qualified"]=x.reconciles.astype(str).str.lower().eq("true") & x.fully_numeric.astype(str).str.lower().eq("true")
    x["annual_reported_mwh"]=pd.to_numeric(x.annual_reported_mwh,errors="coerce")
    x["qualified_mwh"]=x.annual_reported_mwh.where(x.qualified,0.)
    x["withheld_reported_mwh"]=x.annual_reported_mwh.where(~x.qualified,0.)
    summary=x.groupby(["ba_code","fuel"],dropna=False).agg(
        source_rows=("source_row_id","size"),
        qualified_rows=("qualified","sum"),
        qualified_annual_mwh=("qualified_mwh","sum"),
        withheld_reported_annual_mwh=("withheld_reported_mwh","sum"),
        missing_monthly_cells=("missing_months","sum"),
    ).reset_index()
    summary["qualification_fraction"]=summary.qualified_rows/summary.source_rows
    return x,summary

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--reconciliation",type=Path,required=True)
    p.add_argument("--output",type=Path,default=Path("outputs/eia923_generation"))
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    x,summary=qualify(pd.read_csv(a.reconciliation))
    x.to_csv(a.output/"generation_qualification_record_audit.csv",index=False)
    summary.to_csv(a.output/"generation_qualified_ba_fuel.csv",index=False)
    totals=summary.groupby("ba_code",as_index=False).agg(
        source_rows=("source_rows","sum"),qualified_rows=("qualified_rows","sum"),
        qualified_annual_mwh=("qualified_annual_mwh","sum"),
        withheld_reported_annual_mwh=("withheld_reported_annual_mwh","sum"),
        missing_monthly_cells=("missing_monthly_cells","sum"))
    totals.to_csv(a.output/"generation_qualified_ba_summary.csv",index=False)
    (a.output/"qualification_provenance.json").write_text(json.dumps({
        "source":"EIA-923 Page 1 annual/monthly reconciliation",
        "rule":"Only 12-month complete rows with matching reported annual sum are qualified.",
        "caveats":["Withheld annual values remain in separate audit column, not included in qualified generation.",
                   "Qualifying a subset does not mean the whole BA/fuel/year is complete.",
                   "Negative generation preserved; no imputation or Page 4 double counting."],
    },indent=2))
    print(totals.to_string(index=False))

if __name__=="__main__":main()
