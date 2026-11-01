"""Rank actual EIA-860 operating plants not covered by qualified 2024 EIA-923 rows.

Retain reported BA and fuel; flag possible year-end universe differences.
"""
import argparse,json
from pathlib import Path
import pandas as pd

def audit(eia860,eia923,out):
 g=pd.read_csv(eia860,dtype={"plant_id":"string","generator_id":"string","ba_code":"string"})
 q=pd.read_csv(eia923,dtype={"plant_id":"string","ba_code":"string"})
 g["capacity_mw"]=pd.to_numeric(g.capacity_mw,errors="coerce")
 op=g[g.status.astype("string").str.strip().str.upper().eq("OP")&
      g.crosswalk_status.eq("matched")&g.capacity_mw.ge(0)].copy()
 q["qualified"]=q.reconciles.astype(str).str.lower().eq("true")&q.fully_numeric.astype(str).str.lower().eq("true")
 records=[]
 for ba in ("BPAT","CISO"):
  active=op[op.ba_code.eq(ba)].copy()
  published=q[q.ba_code.eq(ba)]
  qualified_ids=set(published.loc[published.qualified,"plant_id"].dropna())
  reported_ids=set(published.plant_id.dropna())
  excluded=active[~active.plant_id.isin(qualified_ids)].copy()
  if excluded.empty:continue
  group=excluded.groupby(["plant_id","state","fuel"],dropna=False).agg(
   operating_generators=("generator_id","size"),
   nameplate_mw=("capacity_mw","sum")).reset_index()
  group["ba_code"]=ba
  group["plant_in_eia923_ba_any_quality"]=group.plant_id.isin(reported_ids)
  group["reason_to_review"]=group.plant_in_eia923_ba_any_quality.map({
   True:"reported_but_no_qualified_eia923_rows",
   False:"absent_from_eia923_ba_rows"})
  records.append(group)
 if not records:raise ValueError("No uncovered operating plant records; check cross-source inputs")
 result=pd.concat(records,ignore_index=True)
 result=result.sort_values(["ba_code","nameplate_mw"],ascending=[True,False])
 out.parent.mkdir(parents=True,exist_ok=True);result.to_csv(out,index=False)
 summary={}
 for ba in ("BPAT","CISO"):
  x=result[result.ba_code.eq(ba)]
  summary[ba]={"uncovered_fuel_plant_rows":len(x),
   "uncovered_unique_plants":int(x.plant_id.nunique()),
   "uncovered_nameplate_mw":float(x.nameplate_mw.sum()),
   "plants_reported_but_not_qualified":int(x.loc[x.plant_in_eia923_ba_any_quality,"plant_id"].nunique()),
   "plants_absent_in_eia923_ba":int(x.loc[~x.plant_in_eia923_ba_any_quality,"plant_id"].nunique())}
 note={"year":2024,"ba":summary,"plant_generator_bus_mapping_verified":False,
  "warning":"Missing qualified EIA-923 Page 1 rows does not mean idle generation or retired capacity."}
 out.with_suffix(".json").write_text(json.dumps(note,indent=2)+"\n")
 print(json.dumps(note,indent=2))
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--eia860",required=True,type=Path)
 p.add_argument("--eia923",required=True,type=Path);p.add_argument("--out",required=True,type=Path)
 a=p.parse_args();audit(a.eia860,a.eia923,a.out)
