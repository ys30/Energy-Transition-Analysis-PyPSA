"""Cross-schedule and cross-BA audit of unlisted BPAT wind generator IDs.

Do not infer physical generation transfers from Schedule 4 membership.
"""
import argparse,io,json,urllib.request
from pathlib import Path
import pandas as pd
from .bpat_wind_generator_930a import EIA930A,normalize

def audit(generators,book):
    g=generators.copy()
    g["plant_id"]=normalize(g.plant_id);g["generator_id"]=normalize(g.generator_id)
    g=g[~g.in_bpat_sch2.astype(str).str.lower().eq("true")].copy()
    excel=pd.ExcelFile(io.BytesIO(book))
    records=[]
    for sheet in ("SCH 2","SCH 3","SCH 4"):
        d=pd.read_excel(excel,sheet_name=sheet)
        if not {"BA Code","EIA Plant ID","EIA Generator ID"}.issubset(d):raise ValueError(f"{sheet} unexpected schema")
        d["plant_id"]=normalize(d["EIA Plant ID"]);d["generator_id"]=normalize(d["EIA Generator ID"])
        d["reported_ba"]=d["BA Code"].astype("string").str.upper().str.strip()
        for row in d[["plant_id","generator_id","reported_ba"]].dropna().drop_duplicates().itertuples(index=False):
            records.append({"plant_id":row.plant_id,"generator_id":row.generator_id,
                            "reported_ba":row.reported_ba,"schedule":sheet})
    matched=pd.DataFrame(records)
    matched=matched.merge(g[["plant_id","generator_id"]],on=["plant_id","generator_id"],how="inner")
    status=g[["plant_id","generator_id","capacity_mw"]].copy()
    status["in_other_ba_sch2"]=False;status["in_bpat_sch3"]=False
    status["in_bpat_sch4"]=False;status["in_other_ba_sch4"]=False
    for label,cond in (
      ("in_other_ba_sch2",matched.schedule.eq("SCH 2")&matched.reported_ba.ne("BPAT")),
      ("in_bpat_sch3",matched.schedule.eq("SCH 3")&matched.reported_ba.eq("BPAT")),
      ("in_bpat_sch4",matched.schedule.eq("SCH 4")&matched.reported_ba.eq("BPAT")),
      ("in_other_ba_sch4",matched.schedule.eq("SCH 4")&matched.reported_ba.ne("BPAT"))):
        keys=matched.loc[cond,["plant_id","generator_id"]].drop_duplicates().assign(hit=True)
        tmp=status.merge(keys,on=["plant_id","generator_id"],how="left")
        status[label]=tmp.hit.fillna(False).to_numpy()
    report={"unlisted_bpat_sch2_wind_generators":len(status),
      **{c:int(status[c].sum()) for c in ("in_other_ba_sch2","in_bpat_sch3","in_bpat_sch4","in_other_ba_sch4")},
      "source":"2024 official EIA-930A Schedule 2, 3, 4; exact EIA plant + generator IDs",
      "caveat":"Schedule membership not proof of actual generation attribution or pseudo-tie energy. Missing direct keys may include self-reported unmatched identifiers."}
    return status,matched,report
def main():
    p=argparse.ArgumentParser();p.add_argument("--generators",type=Path,required=True);p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    with urllib.request.urlopen(urllib.request.Request(EIA930A,headers={"User-Agent":"Mozilla/5.0"}),timeout=120) as f:book=f.read()
    s,m,r=audit(pd.read_csv(a.generators,dtype={"plant_id":"string","generator_id":"string"}),book)
    s.to_csv(a.output/"bpat_unlisted_wind_generator_cross_schedule.csv",index=False)
    m.to_csv(a.output/"bpat_unlisted_wind_generator_matched_records.csv",index=False)
    (a.output/"provenance.json").write_text(json.dumps(r,indent=2))
    print(json.dumps(r,indent=2))
if __name__=="__main__":main()
