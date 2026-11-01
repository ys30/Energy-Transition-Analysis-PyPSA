"""Diagnose EIA-923 Page1 failures in EIA-860 operating plant overlap, by fuel.

Plant-level EIA-860 nameplate is counted once per BA and plant, regardless of
multiple Page1 prime movers/fuels; this prevents accidental MW multiplication.
"""
import argparse,json
from pathlib import Path
import pandas as pd

def audit(e860_path,recon_path,out):
 g=pd.read_csv(e860_path,dtype={"plant_id":"string","ba_code":"string"})
 q=pd.read_csv(recon_path,dtype={"plant_id":"string","ba_code":"string"})
 needed={"plant_id","ba_code","status","crosswalk_status","capacity_mw"}
 if needed-set(g):raise ValueError("EIA860 missing fields")
 needed={"plant_id","ba_code","fuel","reconciles","fully_numeric","missing_months","annual_reported_mwh"}
 if needed-set(q):raise ValueError("EIA923 missing reconciliation fields")
 g["capacity_mw"]=pd.to_numeric(g.capacity_mw,errors="coerce")
 g=g.loc[g.status.astype(str).str.strip().str.upper().eq("OP")&
  g.crosswalk_status.eq("matched")&g.capacity_mw.ge(0)]
 cap=g.groupby(["ba_code","plant_id"],as_index=False).capacity_mw.sum()
 q=q.loc[q.ba_code.isin(["CISO","BPAT"])].copy()
 q["qualified"]=q.reconciles.astype(str).str.lower().eq("true")&q.fully_numeric.astype(str).str.lower().eq("true")
 q["failure_reason"]="qualified"
 q.loc[~q.fully_numeric.astype(str).str.lower().eq("true"),"failure_reason"]="incomplete_months"
 q.loc[q.fully_numeric.astype(str).str.lower().eq("true")&~q.reconciles.astype(str).str.lower().eq("true"),"failure_reason"]="annual_mismatch_or_missing"
 q["annual_reported_mwh"]=pd.to_numeric(q.annual_reported_mwh,errors="coerce")
 q["missing_months"]=pd.to_numeric(q.missing_months,errors="coerce")
 plant=q.groupby(["ba_code","plant_id"],dropna=False).agg(
  page1_rows=("qualified","size"),qualified_rows=("qualified","sum"),
  failed_rows=("qualified",lambda s:int((~s).sum())),
  missing_month_cells=("missing_months","sum")).reset_index()
 plant=plant.merge(cap,on=["ba_code","plant_id"],how="left",validate="one_to_one")
 plant["plant_in_eia860_operating_inventory"]=plant.capacity_mw.notna()
 plant["no_qualified_page1_rows"]=plant.qualified_rows.eq(0)
 # Fuel-level diagnostic counts distinct plants; MW attribution is withheld because
 # one plant can have multiple Page1 fuels and generator primary fuels.
 fails=q.loc[~q.qualified]
 breakdown=fails.groupby(["ba_code","fuel","failure_reason"],dropna=False).agg(
   failed_page1_rows=("plant_id","size"),distinct_plants=("plant_id","nunique"),
   missing_month_cells=("missing_months","sum"),
   reported_annual_mwh=("annual_reported_mwh","sum")).reset_index()
 out.parent.mkdir(parents=True,exist_ok=True)
 breakdown.to_csv(out,index=False)
 plant.to_csv(out.with_name(out.stem+"_plant_level.csv"),index=False)
 report={"failures_by_ba":breakdown.groupby("ba_code").failed_page1_rows.sum().astype(int).to_dict(),
  "fuel_failure_groups":len(breakdown),"plants_with_no_qualified_page1_rows_by_ba":
   plant.loc[plant.no_qualified_page1_rows].groupby("ba_code").plant_id.nunique().astype(int).to_dict(),
  "warning":"Page1 reported fuels and EIA860 primary generator fuels are NOT equivalent; no unverified fuel-level MW attribution.",
  "capacity_factor_calibrated":False}
 out.with_suffix(".json").write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps(report,indent=2))
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--eia860",type=Path,required=True);p.add_argument("--eia923",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args();audit(a.eia860,a.eia923,a.out)
