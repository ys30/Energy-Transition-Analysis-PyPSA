"""Reconcile BA generation coverage and nameplate denominators without claiming capacity-factor calibration."""
import argparse,json
from pathlib import Path
import pandas as pd
def main():
 p=argparse.ArgumentParser();p.add_argument("--screen",type=Path,required=True);p.add_argument("--coverage",type=Path,required=True);p.add_argument("--out",type=Path,required=True);a=p.parse_args()
 s=pd.read_csv(a.screen,dtype={"ba_code":"string"})
 c=pd.read_csv(a.coverage,dtype={"ba_code":"string"})
 if s.ba_code.duplicated().any() or c.ba_code.duplicated().any():raise ValueError("Duplicate BA")
 x=s.merge(c[["ba_code","qualified_row_fraction","withheld_reported_annual_mwh","withheld_share_of_reported","reported_annual_mwh_total"]],on="ba_code",validate="one_to_one")
 if len(x)!=len(s):raise ValueError("Missing BA reporting coverage")
 x["screen_ratio_with_all_reported_annual_mwh"]=x.reported_annual_mwh_total/(x.official_nameplate_mw*8784)
 x["difference_due_to_qualification"]=x.screen_ratio_with_all_reported_annual_mwh-x.qualified_generation_over_nameplate_hours
 x["matched_fleet_calibrated"]=False
 a.out.parent.mkdir(parents=True,exist_ok=True);x.to_csv(a.out,index=False)
 report={"BA_results":{str(r.ba_code):{"qualified_ratio":float(r.qualified_generation_over_nameplate_hours),
 "all_reported_ratio_screen":float(r.screen_ratio_with_all_reported_annual_mwh),
 "excluded_reported_share":float(r.withheld_share_of_reported),
 "ratio_change_from_qualification":float(r.difference_due_to_qualification)}
 for r in x.itertuples()},"actual_fleet_capacity_factor_verified":False,
 "warning":"All-reported annual numerator is exploratory only: EIA-860 operating-year stock and EIA-923 generation scope may differ."}
 a.out.with_suffix(".json").write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
