"""Audit EIA-930A alternative submitted IDs and Schedule 4 relationship text.

No fuzzy generator identity match is accepted as confirmed.
"""
import argparse,io,json,urllib.request
from pathlib import Path
import pandas as pd
from .bpat_wind_generator_930a import EIA930A,normalize

def review(unlisted,book):
    u=unlisted.copy();u["plant_id"]=normalize(u.plant_id);u["generator_id"]=normalize(u.generator_id)
    excel=pd.ExcelFile(io.BytesIO(book));rows=[]
    for sheet in ("SCH 2","SCH 3","SCH 4"):
        d=pd.read_excel(excel,sheet_name=sheet)
        for field in ("EIA Plant ID","EIA Generator ID","Plant ID (EIA-930A)","Generator ID (EIA-930A)","BA Code"):
            if field not in d:raise ValueError(f"Missing {field} in {sheet}")
        for _,r in d.iterrows():
            rows.append({"schedule":sheet,"ba":str(r["BA Code"]).strip().upper(),
              "eia_plant_id":str(r["EIA Plant ID"]).strip().removesuffix(".0"),
              "eia_generator_id":str(r["EIA Generator ID"]).strip(),
              "submitted_plant_id":str(r["Plant ID (EIA-930A)"]).strip().removesuffix(".0"),
              "submitted_generator_id":str(r["Generator ID (EIA-930A)"]).strip(),
              "schedule4_pseudo_tie":str(r.get("BAs having a Pseudo-Tie or Dynamic Relationship",""))})
    inventory=pd.DataFrame(rows)
    findings=[]
    for x in u.itertuples(index=False):
        eq=inventory[(inventory.eia_plant_id==str(x.plant_id))&(inventory.eia_generator_id==str(x.generator_id))]
        submitted=inventory[(inventory.submitted_plant_id==str(x.plant_id))&(inventory.submitted_generator_id==str(x.generator_id))]
        sameplant=inventory[(inventory.eia_plant_id==str(x.plant_id))|(inventory.submitted_plant_id==str(x.plant_id))]
        findings.append({"plant_id":x.plant_id,"generator_id":x.generator_id,
          "exact_eia_key_rows":len(eq),"exact_submitted_key_rows":len(submitted),
          "same_plant_any_schedule_rows":len(sameplant),
          "same_plant_schedules":";".join(sorted(sameplant.schedule.unique())),
          "same_plant_bas":";".join(sorted(sameplant.ba.unique())),
          "same_plant_schedule4_relation_text":";".join(sorted(set(
            val for val in sameplant.loc[sameplant.schedule.eq("SCH 4"),"schedule4_pseudo_tie"] if val not in ("","nan","None")))),
          "identity_conclusion":"exact_eia" if len(eq) else ("exact_submitted" if len(submitted) else "unresolved")})
    result=pd.DataFrame(findings)
    report={"unlisted_generator_count":len(result),
      "exact_eia_matches":int(result.identity_conclusion.eq("exact_eia").sum()),
      "exact_alternate_submitted_matches":int(result.identity_conclusion.eq("exact_submitted").sum()),
      "still_unresolved":int(result.identity_conclusion.eq("unresolved").sum()),
      "rule":"Same-plant or Schedule4 text is context only; no fuzzy generator attribution permitted."}
    return result,report

def main():
    p=argparse.ArgumentParser();p.add_argument("--unlisted",type=Path,required=True);p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    with urllib.request.urlopen(urllib.request.Request(EIA930A,headers={"User-Agent":"Mozilla/5.0"}),timeout=120) as f:book=f.read()
    x,r=review(pd.read_csv(a.unlisted,dtype={"plant_id":"string","generator_id":"string"}),book)
    x.to_csv(a.output/"bpat_wind_submitted_id_schedule4_review.csv",index=False)
    (a.output/"provenance.json").write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
if __name__=="__main__":main()
