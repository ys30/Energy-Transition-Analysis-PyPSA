"""Audited two-BA aggregate EIA-860 nameplate vs qualified EIA-923 generation.

The archived EIA-923 comparison is aggregated across BAs and includes only
qualified mapped rows. This is a descriptive coverage-limited screening ratio.
"""
import argparse,json
from pathlib import Path
import pandas as pd
from .eia923_pypsa_comparison import FUEL_TECH

def calculate(capacity,qualified,bas=("CISO","BPAT")):
    needed={"ba_code","fuel","capacity_mw"}
    if needed-set(capacity):raise ValueError("Missing EIA-860 columns")
    qcols={"carrier","observed_eia923_net_generation_mwh"}
    if qcols-set(qualified):raise ValueError("Missing qualified EIA-923 aggregate columns")
    c=capacity[capacity.ba_code.isin(bas)].copy()
    if c.duplicated(["ba_code","fuel"]).any():raise ValueError("Duplicate BA/fuel capacity")
    c["capacity_mw"]=pd.to_numeric(c.capacity_mw,errors="raise")
    if c.capacity_mw.isna().any() or c.capacity_mw.lt(0).any():raise ValueError("Invalid capacity")
    c["carrier"]=c.fuel.map(FUEL_TECH)
    c=c[c.carrier.notna()].groupby("carrier",as_index=False).capacity_mw.sum()
    q=qualified[["carrier","observed_eia923_net_generation_mwh"]].copy()
    if q.carrier.duplicated().any():raise ValueError("Duplicate aggregate carrier")
    q["observed_eia923_net_generation_mwh"]=pd.to_numeric(q.observed_eia923_net_generation_mwh,errors="raise")
    joined=c.merge(q,on="carrier",how="outer",indicator=True)
    joined["source_coverage_status"]=joined["_merge"].map({
      "both":"capacity_and_qualified_generation","left_only":"capacity_only",
      "right_only":"qualified_generation_only"}).astype(str)
    joined=joined.drop(columns="_merge")
    eligible=joined.capacity_mw.gt(0)&joined.observed_eia923_net_generation_mwh.notna()
    joined["qualified_generation_over_nameplate_hours"]=(
      joined.observed_eia923_net_generation_mwh/(8784*joined.capacity_mw)).where(eligible)
    joined["capacity_calibrated"]=False
    joined["caveat"]="Both BAs aggregate, qualified observed generation only; incomplete EIA-923 may understate actual output. Not hourly availability, dispatch, or firm capacity."
    return joined.sort_values("carrier")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--capacity",type=Path,required=True)
    p.add_argument("--qualified",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    frame=calculate(pd.read_csv(a.capacity),pd.read_csv(a.qualified))
    frame.to_csv(a.output/"eia2024_qualified_generation_nameplate_ratios.csv",index=False)
    (a.output/"provenance.json").write_text(json.dumps({
     "year":2024,"denominator_hours":8784,"scope":"CISO+BPAT combined (not separate BA ratios)",
     "qualified_source":"EIA-923 qualified mapped observations, previously audited two-BA comparison",
     "interpretation":"Coverage-constrained screening ratio, never calibrated hourly availability or capacity credit",
     "restriction":"Never use a qualified-source subset directly as p_max_pu or actual dispatch calibration."
    },indent=2))
    print(frame.to_string(index=False))
if __name__=="__main__":main()
