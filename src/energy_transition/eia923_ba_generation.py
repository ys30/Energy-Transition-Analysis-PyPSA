"""Extract EIA-923 Page 1 monthly BA/fuel net generation (official 2024 layout).

Only Page 1 Generation and Fuel Data is included; Page 4 generator totals
are NOT added to Page 1. Mixed nonnumeric codes are separately audited.
"""
from __future__ import annotations
import argparse
import io
import json
import urllib.request
import zipfile
from pathlib import Path
import pandas as pd
from .eia923_schema_audit import URL

MONTHS=("January","February","March","April","May","June",
        "July","August","September","October","November","December")

def normalize_columns(columns):
    return {str(c).strip().lower().replace("\n"," ").replace("  "," "):c for c in columns}

def extract_page1(archive:bytes):
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        matches=[x for x in z.namelist() if "Schedules_2_3_4_5_" in x and x.lower().endswith(".xlsx")]
        if len(matches)!=1:
            raise ValueError(f"Expected one official EIA-923 Schedules 2-5 workbook; found {matches}")
        with io.BytesIO(z.read(matches[0])) as stream:
            frame=pd.read_excel(stream,sheet_name="Page 1 Generation and Fuel Data",header=5)
    cols=normalize_columns(frame.columns)
    required={"plant id","plant state","reported fuel type code","balancing authority code",
              "reported prime mover", "net generation (megawatthours)"}
    if required-set(cols):
        raise ValueError(f"Unexpected official EIA-923 Page 1 header; missing {sorted(required-set(cols))}")
    month_cols={}
    for month in MONTHS:
        key="netgen "+month.lower()
        if key not in cols:raise ValueError(f"Missing monthly net generation: {month}")
        month_cols[month]=cols[key]
    base=frame[[cols[x] for x in ("plant id","plant state","reported fuel type code",
              "balancing authority code","reported prime mover","net generation (megawatthours)")]
              +list(month_cols.values())].copy()
    base.columns=["plant_id","state","fuel","ba_code","prime_mover","annual_reported_mwh"]+list(MONTHS)
    base["source_row_id"]=range(len(base))
    base["plant_id"]=base.plant_id.astype("string").str.strip().str.replace(r"\.0$","",regex=True)
    for field in ("state","fuel","ba_code","prime_mover"):
        base[field]=base[field].astype("string").str.strip().str.upper()
    base["annual_reported_mwh"]=pd.to_numeric(base.annual_reported_mwh,errors="coerce")
    monthly=base.melt(id_vars=["source_row_id","plant_id","state","fuel","ba_code","prime_mover","annual_reported_mwh"],
                     value_vars=list(MONTHS),var_name="month_name",value_name="source_netgen")
    monthly["month"]=monthly.month_name.map({m:i+1 for i,m in enumerate(MONTHS)})
    monthly["netgen_mwh"]=pd.to_numeric(monthly.source_netgen,errors="coerce")
    monthly["numeric_qc"]="numeric"
    monthly.loc[monthly.netgen_mwh.isna(),"numeric_qc"]="missing_or_nonnumeric"
    monthly.loc[monthly.netgen_mwh.lt(0),"numeric_qc"]="negative_net_generation"
    return base,monthly

def summarize_monthly(monthly,bas):
    chosen=monthly[monthly.ba_code.isin(bas)].copy()
    if set(bas)-set(chosen.ba_code.dropna()):
        raise ValueError(f"Missing official EIA-923 BA codes: {set(bas)-set(chosen.ba_code.dropna())}")
    missing=chosen.netgen_mwh.isna()
    audit=chosen.groupby(["ba_code","fuel"],dropna=False).agg(
      rows=("netgen_mwh","size"),missing_or_nonnumeric=("netgen_mwh",lambda x:int(x.isna().sum())),
      negative=("netgen_mwh",lambda x:int(x.lt(0).sum())),
      observed_sum_mwh=("netgen_mwh","sum")).reset_index()
    totals=chosen.loc[~missing].groupby(["ba_code","fuel","month"],as_index=False).netgen_mwh.sum()
    return chosen,audit,totals

def annual_reconciliation(chosen):
    """Compare Page 1 annual reported totals to monthly cells by original row.

    A nonnumeric monthly entry is not silently interpreted as zero; rows with
    such entries cannot be certified as twelve-month-complete.
    """
    group_cols=["source_row_id","plant_id","state","fuel","ba_code","prime_mover","annual_reported_mwh"]
    report=chosen.groupby(group_cols,dropna=False).agg(
        months_observed=("netgen_mwh",lambda x:int(x.notna().sum())),
        monthly_numeric_sum_mwh=("netgen_mwh","sum"),
        missing_months=("netgen_mwh",lambda x:int(x.isna().sum()))
    ).reset_index()
    report["annual_delta_mwh"]=report.monthly_numeric_sum_mwh-report.annual_reported_mwh
    report["fully_numeric"]=report.months_observed.eq(12)
    report["reported_annual_available"]=report.annual_reported_mwh.notna()
    report["reconciles"]=(
       report.fully_numeric & report.reported_annual_available &
       report.annual_delta_mwh.abs().le(
           (report.annual_reported_mwh.abs()*1e-7).clip(lower=0.1)
       )
    )
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--year",type=int,default=2024)
    p.add_argument("--bas",nargs="+",default=["CISO","BPAT"])
    p.add_argument("--output",type=Path,default=Path("outputs/eia923_generation"))
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    url=URL.format(year=a.year)
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Energy-Transition-Analysis-PyPSA/0.6"}),timeout=120) as f:
        archive=f.read()
    original,monthly=extract_page1(archive)
    chosen,audit,totals=summarize_monthly(monthly,a.bas)
    chosen.to_csv(a.output/"page1_ba_fuel_monthly_record_audit.csv",index=False)
    reconciliation=annual_reconciliation(chosen)
    reconciliation.to_csv(a.output/"annual_monthly_reconciliation.csv",index=False)
    audit.to_csv(a.output/"ba_fuel_data_quality.csv",index=False)
    totals.to_csv(a.output/"ba_fuel_monthly_observed.csv",index=False)
    report={"year":a.year,"url":url,"source_sheet":"Page 1 Generation and Fuel Data",
      "source_grain":"plant x prime mover x reported fuel, month","requested_bas":a.bas,
      "source_rows":len(original),"selected_ba_monthly_rows":len(chosen),
      "missing_or_nonnumeric_cells":int(chosen.netgen_mwh.isna().sum()),
      "negative_generation_cells":int(chosen.netgen_mwh.lt(0).sum()),
      "annual_reconciliation_total_records":len(reconciliation),
      "annual_reconciliation_fully_numeric_records":int(reconciliation.fully_numeric.sum()),
      "annual_reconciliation_matching_records":int(reconciliation.reconciles.sum()),
      "warnings":["Missing/nonnumeric monthly cells omitted from numerical totals and retained in audit.",
                  "Negative values preserved; may represent storage or reporting corrections.",
                  "Page 4 generator data NOT added; avoid duplicate generation.",
                  "BA reporting is as given by EIA-923 and may differ from EIA-930 BA definition."]}
    (a.output/"provenance.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
