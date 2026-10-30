"""Per-BA technology annual energy/nameplate feasibility gate, not hourly calibration."""
import argparse,json
from pathlib import Path
import pandas as pd
from .eia923_pypsa_comparison import FUEL_TECH

def screen(capacity,qualified):
    cols={"ba_code","fuel","capacity_mw"}
    qcols={"ba_code","fuel","qualified_annual_mwh","withheld_reported_annual_mwh","source_rows","qualified_rows"}
    if cols-set(capacity) or qcols-set(qualified):raise ValueError("Missing required fields")
    c=capacity.copy();q=qualified.copy()
    c=c[c.ba_code.isin(["CISO","BPAT"])]
    q=q[q.ba_code.isin(["CISO","BPAT"])]
    if c.duplicated(["ba_code","fuel"]).any() or q.duplicated(["ba_code","fuel"]).any():raise ValueError("Duplicate BA fuel")
    c["technology"]=c.fuel.map(FUEL_TECH);q["technology"]=q.fuel.map(FUEL_TECH)
    c=c[c.technology.notna()].groupby(["ba_code","technology"],as_index=False).agg(nameplate_mw=("capacity_mw","sum"))
    q=q[q.technology.notna()].groupby(["ba_code","technology"],as_index=False).agg(
      qualified_mwh=("qualified_annual_mwh","sum"),withheld_mwh=("withheld_reported_annual_mwh","sum"),
      source_rows=("source_rows","sum"),qualified_rows=("qualified_rows","sum"))
    d=c.merge(q,on=["ba_code","technology"],how="outer",indicator=True)
    d["coverage"]=d["_merge"].astype(str);d=d.drop(columns="_merge")
    d["annual_nameplate_ceiling_mwh"]=d.nameplate_mw*8784
    d["qualified_generation_over_nameplate"]=d.qualified_mwh/d.annual_nameplate_ceiling_mwh
    d.loc[d.annual_nameplate_ceiling_mwh.le(0),"qualified_generation_over_nameplate"]=float("nan")
    d["qualified_rows_complete"]=d.source_rows.eq(d.qualified_rows)
    d["energy_exceeds_nameplate"]=d.qualified_mwh.gt(d.annual_nameplate_ceiling_mwh).where(d.annual_nameplate_ceiling_mwh.notna())
    d["ready_for_hourly_calibration"]=False
    d["interpretation"]="BA+technology annual matched-source screening only; capacity and generation accounting may differ; no hourly dispatchability inferred"
    return d.sort_values(["ba_code","technology"])
def main():
    p=argparse.ArgumentParser();p.add_argument("--capacity",type=Path,required=True)
    p.add_argument("--qualified",type=Path,required=True);p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    d=screen(pd.read_csv(a.capacity),pd.read_csv(a.qualified))
    d.to_csv(a.output/"ba_technology_annual_energy_feasibility.csv",index=False)
    manifest={"year":2024,"hours":8784,"exceeding_technology_rows":d.loc[d.energy_exceeds_nameplate.eq(True),["ba_code","technology"]].to_dict("records"),
     "policy":"Never use qualified EIA-923 annual subset divided by EIA-860 capacity as hourly p_max_pu; validate BA boundaries, completeness, commitment, hydro and reserves first."}
    (a.output/"provenance.json").write_text(json.dumps(manifest,indent=2));print(d.to_string(index=False))
if __name__=="__main__":main()
