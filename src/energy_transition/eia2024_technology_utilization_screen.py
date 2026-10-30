"""Audited technology capacity-to-qualified-generation ratios for two 2024 BAs.

These ratios are LOWER-BOUND SCREENING INDICATORS when EIA-923 qualified
generation does not cover all source rows. They are not physical availability,
hourly capacity factors, or calibrated generator constraints.
"""
import argparse,json
from pathlib import Path
import pandas as pd
from .eia923_pypsa_comparison import FUEL_TECH

def calculate(capacity, qualified, bas=("CISO","BPAT")):
    c=capacity[capacity.ba_code.isin(bas)].copy()
    q=qualified[qualified.ba_code.isin(bas)].copy()
    if c.duplicated(["ba_code","fuel"]).any() or q.duplicated(["ba_code","fuel"]).any():
        raise ValueError("Duplicate BA-fuel aggregate")
    c["capacity_mw"]=pd.to_numeric(c.capacity_mw,errors="raise")
    q["qualified_annual_mwh"]=pd.to_numeric(q.qualified_annual_mwh,errors="raise")
    if c.capacity_mw.isna().any() or c.capacity_mw.lt(0).any() or q.qualified_annual_mwh.isna().any():
        raise ValueError("Invalid historical input")
    c["technology"]=c.fuel.map(FUEL_TECH)
    q["technology"]=q.fuel.map(FUEL_TECH)
    c=c[c.technology.notna()].groupby(["ba_code","technology"],as_index=False).capacity_mw.sum()
    q=q[q.technology.notna()].groupby(["ba_code","technology"],as_index=False).agg(
        qualified_mwh=("qualified_annual_mwh","sum"),
        source_rows=("source_rows","sum"),qualified_rows=("qualified_rows","sum"))
    joined=c.merge(q,on=["ba_code","technology"],how="outer",indicator=True)
    joined["source_coverage_status"]=joined["_merge"].map({
        "both":"capacity_and_qualified_generation","left_only":"capacity_only",
        "right_only":"generation_only"}).astype(str)
    joined=joined.drop(columns="_merge")
    valid=joined.capacity_mw.gt(0)&joined.qualified_mwh.notna()
    joined["qualified_generation_over_nameplate_hours"]=(
        joined.qualified_mwh/(joined.capacity_mw*8784)).where(valid)
    joined["qualified_rows_complete"]=joined.source_rows.eq(joined.qualified_rows).where(joined.source_rows.notna())
    joined["ratio_calibrated"]=False
    joined["caveat"]="Qualified EIA-923 generation may omit source rows; matched EIA-860 BA nameplate and Page 1 net generation have different coverage. Not hourly availability, capacity credit, or fitted dispatch."
    return joined.sort_values(["ba_code","technology"])

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--capacity",type=Path,required=True)
    p.add_argument("--qualified",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    frame=calculate(pd.read_csv(a.capacity),pd.read_csv(a.qualified))
    frame.to_csv(a.output/"eia2024_qualified_generation_nameplate_ratios.csv",index=False)
    (a.output/"provenance.json").write_text(json.dumps({
      "year":2024,"hours":8784,
      "scope":"EIA-860 2024 two-BA supported generator nameplate and EIA-923 qualified Page 1 annual BA-fuel generation",
      "interpretation":"Coverage-constrained descriptive utilization screening only, not calibrated availability or dependable capacity",
      "restriction":"Never force the qualified-row utilization ratio into p_max_pu without complete BA/plant data and hourly dispatch evidence."
    },indent=2))
    print(frame.to_string(index=False))
if __name__=="__main__":main()
