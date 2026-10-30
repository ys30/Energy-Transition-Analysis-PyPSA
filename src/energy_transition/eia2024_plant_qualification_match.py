"""Match audited EIA-923 plant annual rows to verified EIA-860 plant-BA mapping.

Plant ID is the join key; never allocate plant-level EIA-923 observations
across individual EIA-860 generators. Detect BA disagreements and unmatched
source energy, including negative net generation.
"""
import argparse,json
from pathlib import Path
import pandas as pd

def reconcile(qualification, generator_ba,bas=("CISO","BPAT")):
    q=qualification.copy()
    q=q[q.ba_code.isin(bas)]
    required={"source_row_id","plant_id","ba_code","fuel","qualified","annual_reported_mwh"}
    if required-set(q):raise ValueError("Missing EIA-923 qualification fields")
    g=generator_ba.copy()
    if {"plant_id","ba_code","crosswalk_status"}-set(g):raise ValueError("Missing EIA-860 crosswalk fields")
    for x in (q,g):x["plant_id"]=x.plant_id.astype("string").str.strip().str.replace(r"\.0$","",regex=True)
    if q.source_row_id.duplicated().any():raise ValueError("Duplicate source qualification rows")
    valid=g[g.crosswalk_status.eq("matched")][["plant_id","ba_code"]].dropna().drop_duplicates()
    ambiguous=valid.groupby("plant_id").ba_code.nunique()
    ambiguous=set(ambiguous[ambiguous.gt(1)].index)
    valid=valid[~valid.plant_id.isin(ambiguous)].drop_duplicates("plant_id")
    valid=valid.rename(columns={"ba_code":"eia860_plant_ba"})
    joined=q.merge(valid,on="plant_id",how="left",validate="many_to_one")
    joined["plant_match_status"]="matched"
    joined.loc[joined.eia860_plant_ba.isna(),"plant_match_status"]="unmatched_or_ambiguous"
    joined.loc[joined.eia860_plant_ba.notna()&joined.eia860_plant_ba.ne(joined.ba_code),
               "plant_match_status"]="ba_disagreement"
    joined["qualified"]=joined.qualified.astype(str).str.lower().eq("true")
    joined["annual_reported_mwh"]=pd.to_numeric(joined.annual_reported_mwh,errors="coerce")
    joined["qualified_generation_mwh"]=joined.annual_reported_mwh.where(joined.qualified)
    group=joined.groupby(["ba_code","fuel","plant_match_status"],dropna=False).agg(
       source_rows=("source_row_id","count"),qualified_rows=("qualified","sum"),
       qualified_signed_generation_mwh=("qualified_generation_mwh","sum"),
       qualified_absolute_generation_mwh=("qualified_generation_mwh",lambda v:v.abs().sum()),
       unqualified_rows=("qualified",lambda v:int((~v).sum()))).reset_index()
    overall={"matched_same_ba_qualified_abs_mwh":float(joined.loc[joined.plant_match_status.eq("matched"),"qualified_generation_mwh"].abs().sum()),
      "all_qualified_abs_mwh":float(joined.qualified_generation_mwh.abs().sum()),
      "ba_disagreement_rows":int(joined.plant_match_status.eq("ba_disagreement").sum()),
      "unmatched_or_ambiguous_rows":int(joined.plant_match_status.eq("unmatched_or_ambiguous").sum()),
      "interpretation":"Plant-level BA crosswalk only, not generator allocation, hourly dispatch or complete grid generation"}
    overall["qualified_abs_generation_matched_fraction"]=(overall["matched_same_ba_qualified_abs_mwh"]/overall["all_qualified_abs_mwh"] if overall["all_qualified_abs_mwh"] else None)
    return joined,group,overall

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--qualified",type=Path,required=True)
    p.add_argument("--generator-ba",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    joined,summary,report=reconcile(pd.read_csv(a.qualified,dtype={"plant_id":"string"}),
       pd.read_csv(a.generator_ba,dtype={"plant_id":"string"}))
    joined.to_csv(a.output/"plant_qualification_match_audit.csv",index=False)
    summary.to_csv(a.output/"ba_fuel_plant_match_summary.csv",index=False)
    (a.output/"plant_match_provenance.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
