"""Audit official EIA-860 generator fleet for evidence-backed PyPSA supply input.

Source: existing generator_ba_audit_{year}.csv with original generator
identifiers, reported nameplate, status, primary fuel and BA crosswalk.
An EIA nameplate MW is NOT dependable hourly capacity or a generator bus.
"""
import argparse,json
from pathlib import Path
import pandas as pd

def inspect(path,year):
 d=pd.read_csv(path,dtype={"plant_id":"string","generator_id":"string"})
 must={"plant_id","generator_id","state","fuel","capacity_mw","status","ba_code","crosswalk_status"}
 missing=must-set(d.columns)
 if missing:raise ValueError(f"Missing original EIA-860 fields: {sorted(missing)}")
 op=d[d.status.astype("string").str.strip().str.upper().eq("OP")].copy()
 op["capacity_mw"]=pd.to_numeric(op.capacity_mw,errors="coerce")
 valid=op.loc[op.crosswalk_status.eq("matched") & op.capacity_mw.notna() & op.capacity_mw.ge(0)].copy()
 if valid.empty:raise ValueError("No verified operating EIA generators")
 if valid[["plant_id","generator_id"]].isna().any().any():raise ValueError("Generator IDs absent")
 duplicates=int(valid.duplicated(["plant_id","generator_id"]).sum())
 if duplicates: raise ValueError(f"Duplicate generator identities: {duplicates}")
 total=float(op.loc[op.capacity_mw.ge(0),"capacity_mw"].sum())
 mapped=float(valid.capacity_mw.sum())
 if total<=0:raise ValueError("EIA operating nameplate denominator unavailable")
 fraction=mapped/total
 if fraction<0.95:raise ValueError(f"Mapped operating MW coverage below 95%: {fraction:.4f}")
 per_fuel=valid.groupby("fuel").capacity_mw.sum().sort_values(ascending=False)
 return {"year":year,"official_dataset":"EIA-860 operable generator inventory",
  "operating_gen_rows":len(op),"ba_matched_operating_gen_rows":len(valid),
  "unique_operating_plants":int(valid.plant_id.nunique()),
  "operating_nameplate_mw":total,"ba_mapped_operating_nameplate_mw":mapped,
  "ba_mapping_mw_fraction":fraction,
  "nameplate_mw_by_primary_fuel":{str(k):float(v) for k,v in per_fuel.items()},
  "states":sorted(valid.state.astype(str).unique().tolist()),
  "generation_plant_level_ids_verified":True,
  "actual_generator_bus_mapping_verified":False,
  "hourly_availability_verified":False,"marginal_fuel_cost_verified":False,
  "ready_for_full_real_generation_dispatch":False,
  "note":"EIA-860 nameplate is real source evidence, not hourly deliverable supply or forecast fleet."}

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--audit",type=Path,required=True)
 p.add_argument("--year",type=int,required=True)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args();r=inspect(a.audit,a.year)
 a.out.parent.mkdir(parents=True,exist_ok=True)
 a.out.write_text(json.dumps(r,indent=2)+"\n")
 print(json.dumps(r,indent=2))
if __name__=="__main__":main()
