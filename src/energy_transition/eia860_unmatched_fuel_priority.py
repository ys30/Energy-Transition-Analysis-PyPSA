"""Rank EIA-860/EIA-923 uncovered BA capacity by fuel and reporting reason."""
import argparse,json
from pathlib import Path
import pandas as pd
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--unmatched",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
 a=p.parse_args()
 d=pd.read_csv(a.unmatched,dtype={"plant_id":"string","ba_code":"string","fuel":"string"})
 req={"plant_id","ba_code","fuel","nameplate_mw","reason_to_review"}
 if req-set(d):raise ValueError(f"Missing fields: {sorted(req-set(d))}")
 d["nameplate_mw"]=pd.to_numeric(d.nameplate_mw,errors="raise")
 if d.nameplate_mw.isna().any() or d.nameplate_mw.lt(0).any():raise ValueError("Invalid official MW")
 groups=d.groupby(["ba_code","reason_to_review","fuel"],dropna=False).agg(
  uncovered_mw=("nameplate_mw","sum"),
  plants=("plant_id","nunique"),
  plant_fuel_rows=("plant_id","size")).reset_index().sort_values("uncovered_mw",ascending=False)
 sums=d.groupby(["ba_code","reason_to_review"],dropna=False).nameplate_mw.sum()
 if abs(groups.uncovered_mw.sum()-d.nameplate_mw.sum())>1e-5:raise ValueError("Capacity conservation failed")
 a.out.parent.mkdir(parents=True,exist_ok=True);groups.to_csv(a.out,index=False)
 report={"uncovered_mw_by_ba_and_reason":{str(ba):{str(reason):float(mw) for (keyba,reason),mw in sums.items() if keyba==ba} for ba in sorted(d.ba_code.unique())},
  "top_fuel_reason_groups":groups.head(12).to_dict(orient="records"),
  "scope":"2024 official operating EIA860 plants not matched to qualified EIA923 Page1 BA rows",
  "not_proven":"Retirement, missing generation, hourly dispatch availability, or actual electrical bus connections"}
 a.out.with_suffix(".json").write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
