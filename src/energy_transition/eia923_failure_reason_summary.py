"""Summarize EIA-923 qualification failures by BA, fuel and reason, with exact rows."""
import argparse,json
from pathlib import Path
import pandas as pd

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--failures",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
 a=p.parse_args()
 d=pd.read_csv(a.failures)
 req={"ba_code","fuel","failure_reason","failed_page1_rows","distinct_plants","missing_month_cells","reported_annual_mwh"}
 if req-set(d):raise ValueError("Missing diagnostic fields")
 if d.failed_page1_rows.lt(0).any():raise ValueError("Invalid record counts")
 d=d.sort_values(["ba_code","failed_page1_rows"],ascending=[True,False])
 a.out.parent.mkdir(parents=True,exist_ok=True)
 d.to_csv(a.out,index=False)
 result={"total_failed_page1_rows":int(d.failed_page1_rows.sum()),
  "by_ba":d.groupby("ba_code").failed_page1_rows.sum().astype(int).to_dict(),
  "by_reason":d.groupby(["ba_code","failure_reason"]).failed_page1_rows.sum().rename_axis(["ba","reason"]).reset_index().to_dict(orient="records"),
  "hydro_solar_fuel_rows":d[d.fuel.isin(["WAT","MWH","SUN"])].to_dict(orient="records"),
  "top_failure_groups":d.sort_values("failed_page1_rows",ascending=False).head(12).to_dict(orient="records"),
  "no_rule_relaxation_applied":True}
 a.out.with_suffix(".json").write_text(json.dumps(result,indent=2,default=str)+"\n")
 print(json.dumps(result,indent=2,default=str))
if __name__=="__main__":main()
