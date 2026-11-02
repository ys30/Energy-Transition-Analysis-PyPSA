"""Audit plant-ID coverage between qualified EIA-923 Page 1 rows and EIA-860 operating inventory.

Report nonoverlap without equating plant records to generator-level calibration.
"""
import argparse,json
from pathlib import Path
import pandas as pd
def run(e860,e923,out):
 g=pd.read_csv(e860,dtype={"plant_id":"string","generator_id":"string","ba_code":"string"})
 q=pd.read_csv(e923,dtype={"plant_id":"string","ba_code":"string"})
 need={"plant_id","status","crosswalk_status","ba_code","capacity_mw"}
 if need-set(g):raise ValueError("EIA860 required fields absent")
 need2={"plant_id","ba_code","reconciles","fully_numeric","annual_reported_mwh"}
 if need2-set(q):raise ValueError("EIA923 reconciliation fields absent")
 op=g[g.status.astype(str).str.upper().eq("OP")&g.crosswalk_status.eq("matched")].copy()
 op.capacity_mw=pd.to_numeric(op.capacity_mw,errors="coerce")
 op=op[op.capacity_mw.ge(0)&op.capacity_mw.notna()]
 if op.empty:raise ValueError("No qualified EIA860 operating plants")
 q.annual_reported_mwh=pd.to_numeric(q.annual_reported_mwh,errors="coerce")
 if "missing_months" not in q.columns:
  raise ValueError("EIA923 monthly coverage column missing: refusing to certify records")
 q["missing_months"]=pd.to_numeric(q.missing_months,errors="coerce")
 if q.missing_months.isna().any() or q.missing_months.lt(0).any() or q.missing_months.gt(12).any():
  raise ValueError("Invalid EIA923 missing_months")
 q["qualified"]=(q.reconciles.astype(str).str.lower().eq("true")
  & q.fully_numeric.astype(str).str.lower().eq("true")
  & q.missing_months.eq(0)
  & q.annual_reported_mwh.notna())
 rows=[]
 for ba in sorted(q.ba_code.dropna().unique()):
  a=op[op.ba_code.eq(ba)]
  b=q[q.ba_code.eq(ba)]
  ids=set(a.plant_id.dropna());qids=set(b.plant_id.dropna())
  qualids=set(b.loc[b.qualified,"plant_id"].dropna())
  common=ids&qualids
  rows.append({"ba_code":ba,"operating_eia860_plants":len(ids),"eia923_reported_plants":len(qids),
   "eia923_qualified_plants":len(qualids),"qualified_plant_id_overlap":len(common),
   "eia860_only_operating_plants":len(ids-qualids),
   "eia923_only_qualified_plants":len(qualids-ids),
   "operating_nameplate_on_qualified_plant_ids_mw":float(a.loc[a.plant_id.isin(common),"capacity_mw"].sum()),
   "eia860_total_operating_nameplate_mw":float(a.capacity_mw.sum()),
   "qualified_eia923_mwh_on_common_plant_ids":float(b.loc[b.qualified&b.plant_id.isin(common),"annual_reported_mwh"].sum()),
   "qualified_eia923_mwh_not_on_eia860_operating_plant_ids":float(b.loc[b.qualified&~b.plant_id.isin(ids),"annual_reported_mwh"].sum()),
   "generator_level_matching_verified":False})
 frame=pd.DataFrame(rows)
 if frame.empty:raise ValueError("No EIA923 BA observations")
 out.parent.mkdir(parents=True,exist_ok=True);frame.to_csv(out,index=False)
 report={"ba_results":rows,"year":2024,"full_plant_and_generator_coverage_verified":False,
 "warning":"EIA-923 Page1 plant/fuel source and EIA-860 year-end operating inventory are not identical reporting universes."}
 out.with_suffix(".json").write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps(report,indent=2))
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--eia860",type=Path,required=True)
 p.add_argument("--eia923",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args();run(a.eia860,a.eia923,a.out)
