"""Keep annually reported EIA-923 values separate from 12-month-certified generation.

No missing monthly observations are imputed. Annual-only records are explicitly
not certified for hourly profiles or generation calibration.
"""
import argparse,json
from pathlib import Path
import pandas as pd

def examine(source,output):
 d=pd.read_csv(source,dtype={"plant_id":"string","ba_code":"string","fuel":"string"})
 need={"source_row_id","plant_id","ba_code","fuel","fully_numeric","reconciles","annual_reported_mwh","missing_months"}
 if need-set(d):raise ValueError("Missing original EIA-923 reconciliation fields")
 if d.source_row_id.duplicated().any():raise ValueError("Duplicate Page1 records")
 d["annual_reported_mwh"]=pd.to_numeric(d.annual_reported_mwh,errors="coerce")
 d["missing_months"]=pd.to_numeric(d.missing_months,errors="coerce")
 if d.missing_months.isna().any() or d.missing_months.lt(0).any() or d.missing_months.gt(12).any():
  raise ValueError("Invalid or missing monthly-coverage counts")
 if d.source_row_id.isna().any():
  raise ValueError("Missing source record identifiers")
 d["monthly_certified"]=(d.fully_numeric.astype(str).str.lower().eq("true")
  & d.reconciles.astype(str).str.lower().eq("true")
  & d.missing_months.eq(0)
  & d.annual_reported_mwh.notna())
 d["annual_report_available"]=d.annual_reported_mwh.notna()
 d["evidence_tier"]="no_reported_annual_numeric_value"
 d.loc[d.annual_report_available,"evidence_tier"]="annual_reported_only_not_monthly_certified"
 d.loc[d.monthly_certified,"evidence_tier"]="twelve_month_reconciled"
 d["strict_monthly_certified_mwh"]=d.annual_reported_mwh.where(d.monthly_certified,0.0)
 d["annual_reported_sensitivity_mwh"]=d.annual_reported_mwh
 d["annual_only_mwh"]=d.annual_reported_mwh.where(d.annual_report_available & ~d.monthly_certified,0.0)
 d["usable_for_hourly_dispatch_calibration"]=False
 grouped=d.groupby(["ba_code","fuel","evidence_tier"],dropna=False).agg(
  source_rows=("source_row_id","size"),
  reported_annual_mwh=("annual_reported_mwh","sum"),
  strict_monthly_certified_mwh=("strict_monthly_certified_mwh","sum"),
  annual_only_mwh=("annual_only_mwh","sum"),
  unique_plants=("plant_id","nunique")).reset_index()
 if abs(grouped.annual_only_mwh.sum()-d.annual_only_mwh.sum())>1e-5:raise ValueError("Annual-only conservation failure")
 output.parent.mkdir(parents=True,exist_ok=True)
 grouped.to_csv(output,index=False)
 d[["source_row_id","plant_id","ba_code","fuel","missing_months","annual_reported_mwh","evidence_tier","usable_for_hourly_dispatch_calibration"]].to_csv(output.with_name(output.stem+"_record_audit.csv"),index=False)
 report={"by_ba":d.groupby(["ba_code","evidence_tier"]).agg(rows=("source_row_id","size"),annual_mwh=("annual_reported_mwh","sum")).reset_index().to_dict(orient="records"),
 "annual_only_records":int((d.evidence_tier=="annual_reported_only_not_monthly_certified").sum()),
 "annual_only_mwh":float(d.annual_only_mwh.sum()),
 "no_monthly_imputation":True,"verified_hourly_generation_profiles":False,
 "warning":"Official annual totals in failed monthly records are a separate sensitivity tier, not verified 12-month completeness or actual capacity factors."}
 output.with_suffix(".json").write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps(report,indent=2))
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--reconciliation",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args();examine(a.reconciliation,a.out)
