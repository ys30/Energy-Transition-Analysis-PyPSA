"""Audit BA-by-technology EIA-923 qualification coverage, no false calibration.

Uses the original Page-1 qualifying BA/fuel table; preserves withheld totals.
"""
import argparse,json
from pathlib import Path
import pandas as pd
from .eia923_pypsa_comparison import FUEL_TECH

def audit(frame,bas=("CISO","BPAT")):
    required={"ba_code","fuel","source_rows","qualified_rows","qualified_annual_mwh","withheld_reported_annual_mwh"}
    if missing:=required-set(frame):raise ValueError(f"Missing fields: {sorted(missing)}")
    d=frame[frame.ba_code.isin(bas)].copy()
    if d.duplicated(["ba_code","fuel"]).any():raise ValueError("Duplicate BA/fuel qualification")
    if set(d.ba_code)!=set(bas):raise ValueError("Missing selected BA")
    d["technology"]=d.fuel.map(FUEL_TECH).fillna("unmapped")
    result=d.groupby(["ba_code","technology"],as_index=False).agg(
       source_rows=("source_rows","sum"),qualified_rows=("qualified_rows","sum"),
       qualified_mwh=("qualified_annual_mwh","sum"),
       withheld_reported_mwh=("withheld_reported_annual_mwh","sum"))
    result["row_qualification_fraction"]=result.qualified_rows/result.source_rows
    result["all_source_rows_qualified"]=result.qualified_rows.eq(result.source_rows)
    result["usable_as_complete_ba_generation"]=False
    result["status"]="qualified_subset_only_no_completeness_claim"
    return result.sort_values(["ba_code","technology"])

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    d=audit(pd.read_csv(a.input))
    d.to_csv(a.output/"eia923_qualified_by_ba_technology.csv",index=False)
    (a.output/"provenance.json").write_text(json.dumps({
      "source":"Official EIA-923 Page 1 qualified BA/fuel rows, 2024",
      "note":"Qualified rows are a subset. Even all-row qualification does not establish full BA-fuel universe or hourly dependable capacity.",
      "forbid":"Do not apply observed annual ratio as hourly p_max_pu, calibrate firm capacity or assume BA mapping complete."
    },indent=2))
    print(d.to_string(index=False))
if __name__=="__main__":main()
