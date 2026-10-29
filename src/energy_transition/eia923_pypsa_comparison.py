"""Compare qualified EIA-923 BA/fuel generation with solved 2024 PyPSA dispatch.

Observed source rows are only EIA-923 Page 1 fully reconciled records.
No model fitting, no rescaling of source data, no implied EIA-930 equivalence.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

FUEL_TECH = {
 "NG":"gas","BFG":"gas","OG":"gas","PG":"gas",
 "BIT":"coal","SUB":"coal","LIG":"coal","WC":"coal","RC":"coal",
 "NUC":"nuclear","WAT":"hydro","WND":"wind",
 "SUN":"solar","GEO":"geothermal","MWH":"storage",
 "DFO":"oil","RFO":"oil","KER":"oil","JF":"oil",
 "WDS":"biomass","WDL":"biomass","BLQ":"biomass","LFG":"biomass","MSW":"biomass",
}
def compare(qualified, network):
    q=qualified.copy()
    required={"ba_code","fuel","qualified_annual_mwh","source_rows","qualified_rows","withheld_reported_annual_mwh"}
    if required-set(q):raise ValueError("EIA-923 qualification columns missing")
    q["tech"]=q.fuel.map(FUEL_TECH).fillna("unmapped_"+q.fuel.astype(str))
    if q.duplicated(["ba_code","fuel"]).any():raise ValueError("Duplicate BA/fuel qualified records")
    bytech=q.groupby(["ba_code","tech"],as_index=False).agg(
        eia923_qualified_mwh=("qualified_annual_mwh","sum"),
        withheld_reported_mwh=("withheld_reported_annual_mwh","sum"),
        source_rows=("source_rows","sum"),qualified_rows=("qualified_rows","sum"))
    records=[]
    weight=network.snapshot_weightings.generators
    for name,row in network.generators.iterrows():
        ba=str(row.bus)
        tech=str(name).removeprefix(ba+"_")
        if tech=="unserved":continue
        if tech not in ("gas","coal","nuclear","hydro","wind","solar"):continue
        generation=float((network.generators_t.p[name]*weight).sum())
        records.append({"ba_code":ba,"tech":tech,"pypsa_dispatch_mwh":generation})
    model=pd.DataFrame(records).groupby(["ba_code","tech"],as_index=False).pypsa_dispatch_mwh.sum()
    joined=bytech.merge(model,on=["ba_code","tech"],how="outer",indicator=True)
    joined["comparison_status"]=joined["_merge"].map({"both":"both_sources","left_only":"observed_only","right_only":"model_only"}).astype(str)
    joined=joined.drop(columns="_merge")
    comparable=joined.comparison_status.eq("both_sources")
    joined["model_minus_qualified_observed_mwh"]=(joined.pypsa_dispatch_mwh-joined.eia923_qualified_mwh).where(comparable)
    joined["relative_difference_vs_qualified_observed"]=(joined.model_minus_qualified_observed_mwh/joined.eia923_qualified_mwh).where(comparable & joined.eia923_qualified_mwh.ne(0))
    joined["full_source_row_coverage"]=joined.qualified_rows.eq(joined.source_rows)
    joined["interpretation"]="Descriptive benchmark, not calibrated model accuracy; incomplete EIA-923 rows and BA boundary mismatches limit inference"
    return joined.sort_values(["ba_code","tech"])

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--qualification",type=Path,required=True)
    p.add_argument("--network",type=Path,required=True)
    p.add_argument("--output",type=Path,default=Path("outputs/ba_calibration"))
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    import pypsa
    network=pypsa.Network(a.network)
    joined=compare(pd.read_csv(a.qualification),network)
    joined.to_csv(a.output/"eia923_vs_pypsa_2024.csv",index=False)
    manifest={"period":2024,"observed":"EIA-923 Page 1 annual qualified BA/fuel rows",
      "model":"2024 two-BA representative-hour PyPSA dispatch with assumed costs and availability",
      "limits":["EIA-923 reported BA may include plant reporting boundaries different from EIA-930 balancing operations.",
                "EIA-923 unqualified annual rows withheld; resulting sum is a subset, not full observed BA output.",
                "No numeric model accuracy metric should be interpreted as validated until reporting boundaries and excluded fuel groups are reconciled."]}
    (a.output/"comparison_provenance.json").write_text(json.dumps(manifest,indent=2))
    print(joined[["ba_code","tech","comparison_status","eia923_qualified_mwh","pypsa_dispatch_mwh"]].to_string(index=False))
if __name__=="__main__":main()
