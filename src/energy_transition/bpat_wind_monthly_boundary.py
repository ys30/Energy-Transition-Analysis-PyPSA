"""Monthly BPAT wind source-boundary discrepancy with explicit hourly coverage.

EIA-923 Page 1 monthly plant values are not inherently equivalent to EIA-930
BA-reported signed hourly net generation. No scaling, filling or causal claim.
"""
import argparse,json
from pathlib import Path
import pandas as pd

def compare(monthly, hourly, ba="BPAT", fuel="WND"):
    required={"ba_code","fuel","month","netgen_mwh"}
    if required-set(monthly):raise ValueError("Missing EIA-923 month fields")
    x=monthly[monthly.ba_code.eq(ba)&monthly.fuel.eq(fuel)].copy()
    x["month"]=pd.to_numeric(x.month,errors="raise")
    if x.empty:raise ValueError("No matching EIA-923 plant/month generation")
    y=hourly[hourly.respondent.eq(ba)&hourly.fueltype.eq(fuel)].copy()
    y["period"]=pd.to_datetime(y.period,utc=True)
    if y.duplicated("period").any():raise ValueError("Duplicate EIA-930 BA/fuel hours")
    y["value"]=pd.to_numeric(y.value,errors="coerce")
    y=y[y.period.dt.year.eq(2024)]
    y["month"]=y.period.dt.month
    rows=[]
    for m in range(1,13):
        p=x[x.month.eq(m)]
        h=y[y.month.eq(m)]
        expected=pd.date_range(pd.Timestamp(2024,m,1,tz="UTC"),
           pd.Timestamp(2024,m,1,tz="UTC")+pd.offsets.MonthBegin(1),freq="h",inclusive="left")
        received=h[h.period.isin(expected)]
        valid=received.value.dropna()
        rows.append({"month":m,"expected_utc_hours":len(expected),
          "eia930_valid_hours":len(valid),
          "eia930_missing_or_null_hours":len(expected)-len(valid),
          "eia930_signed_wind_mwh":float(valid.sum()),
          "eia923_observed_plant_month_wind_mwh":float(pd.to_numeric(p.netgen_mwh,errors="coerce").sum()),
          "eia923_plant_fuel_month_rows":len(p)})
    out=pd.DataFrame(rows)
    out["difference_eia923_minus_eia930_mwh"]=out.eia923_observed_plant_month_wind_mwh-out.eia930_signed_wind_mwh
    out["comparison_classification"]="different_reporting_accounting_boundary_not_reconciled"
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--eia923-monthly",type=Path,required=True)
    p.add_argument("--eia930-hourly",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    out=compare(pd.read_csv(a.eia923_monthly),pd.read_csv(a.eia930_hourly))
    out.to_csv(a.output/"bpat_wind_eia923_eia930_monthly_comparison.csv",index=False)
    (a.output/"provenance.json").write_text(json.dumps({
      "year":2024,"BA":"BPAT","fuel":"WND","temporal_boundary":"UTC month for EIA-930; EIA-923 reported calendar month",
      "limits":"EIA-923 Page1 plant fuel reported values vs EIA-930 BA-operational hourly signed net values. May differ in BA attribution, reporting population, time zones and accounting. No missing-hour extrapolation; no curtailment or losses inferred."
    },indent=2))
    print(out.to_string(index=False))
if __name__=="__main__":main()
