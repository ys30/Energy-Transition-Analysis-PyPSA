"""Contemporaneous 2023 EIA-860M monthly BA-code generator roster vs EIA-930 BA MW.

Preliminary EIA-860M BA code is not verified to equal the population
measured in the EIA-930 BA net-generation fuel aggregates. This is
a population-completeness test, never certified observed capacity factors.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd

MONTHS=("january","february","march","april","may","june",
        "july","august","september","october","november","december")
BAS=("PNM","PSCO","IPCO","WACM")
TECH={"Solar Photovoltaic":"solar",
      "Onshore Wind Turbine":"wind","Offshore Wind Turbine":"wind"}
COLS=("Plant ID","Generator ID","Plant State","Balancing Authority Code",
      "Technology","Status","Nameplate Capacity (MW)","Operating Month","Operating Year")
JULY_SOURCE_SHA256="9a7b3f4051f1edb55f4d6508a1b963d2b344d687de6ea464ac538f2929122510"

def read_month(path,month):
    path=Path(path)
    if path.name!=f"{MONTHS[month-1]}_generator2023.xlsx":
        raise ValueError("EIA860M monthly filename does not match year/month")
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    if month==7 and digest!=JULY_SOURCE_SHA256:
        raise ValueError("Previously verified original July EIA860M SHA256 has changed")
    raw=pd.read_excel(path,sheet_name="Operating",header=2,dtype=str,
                      usecols=lambda name:name in COLS)
    if set(raw.columns)!=set(COLS):
        raise ValueError(f"Official monthly EIA860M schema drift: {set(COLS)-set(raw.columns)}")
    d=raw.loc[raw["Balancing Authority Code"].isin(BAS)&raw.Technology.isin(TECH)].copy()
    d["plant_key"]=d["Plant ID"].fillna("").str.replace(r"\.0$","",regex=True).str.strip()
    d["gen_key"]=d["Generator ID"].fillna("").str.strip()
    if d.plant_key.eq("").any() or d.gen_key.eq("").any():
        raise ValueError("BA generator with missing EIA plant/generator ID")
    if d[["plant_key","gen_key"]].duplicated().any():
        raise ValueError("Source monthly operating sheet contains duplicate physical generator IDs")
    d["nameplate_mw"]=pd.to_numeric(d["Nameplate Capacity (MW)"],errors="coerce")
    if not np.isfinite(d.nameplate_mw).all() or (d.nameplate_mw<0).any():
        raise ValueError("Bad official source nameplate MW")
    d["fuel"]=d.Technology.map(TECH)
    d["month"]=f"2023-{month:02d}"
    d["status_OP"]=d.Status.fillna("").str.startswith("(OP)")
    d["commission_month"]=pd.to_numeric(d["Operating Month"],errors="coerce")
    d["commission_year"]=pd.to_numeric(d["Operating Year"],errors="coerce")
    future=d.loc[d.status_OP&(
        (d.commission_year>2023)|
        ((d.commission_year==2023)&(d.commission_month>month)))]
    if len(future):raise ValueError("OP generator commissioning after source census month")
    d["source_sha256"]=digest
    return d,digest

def census(paths):
    frames=[];cohorts=[];geography=[];digests=[]
    for month,path in enumerate(paths,1):
        df,sha=read_month(path,month)
        digests.append({"month":f"2023-{month:02d}",
                        "file":Path(path).name,"source_sha256":sha})
        frames.append(df)
        for ba in BAS:
            for fuel in ("wind","solar"):
                c=df.loc[df["Balancing Authority Code"].eq(ba)&df.fuel.eq(fuel)]
                op=c.loc[c.status_OP]
                cohorts.append({
                  "month":f"2023-{month:02d}","ba_code":ba,"fuel":fuel,
                  "operating_worksheet_rows":len(c),"OP_generator_rows":len(op),
                  "OP_nameplate_mw":float(op.nameplate_mw.sum()),
                  "non_OP_generator_rows":len(c)-len(op),
                  "non_OP_nameplate_mw":float(c.loc[~c.status_OP,"nameplate_mw"].sum()),
                  "OP_unknown_commission_date_count":int(
                    (op.commission_year.isna()|op.commission_month.isna()).sum()),
                  "verified_mettered_BA_generation_footprint":False})
                for state,group in op.groupby("Plant State"):
                    geography.append({
                      "month":f"2023-{month:02d}","ba_code":ba,"fuel":fuel,
                      "plant_state":state,"OP_generators":len(group),
                      "OP_nameplate_mw":float(group.nameplate_mw.sum())})
    s=pd.DataFrame(cohorts);g=pd.DataFrame(geography)
    if len(s)!=96:raise ValueError("Missing 12-month BA-fuel cohorts")
    for r in s.itertuples(index=False):
        x=g[(g.month==r.month)&(g.ba_code==r.ba_code)&(g.fuel==r.fuel)]
        if abs(x.OP_nameplate_mw.sum()-r.OP_nameplate_mw)>1e-6:
            raise ValueError("BA-to-state candidate-nameplate arithmetic does not reconcile")
    return pd.concat(frames,ignore_index=True),s,g,pd.DataFrame(digests)

def comparison(census_summary,observed):
    required={"utc_hour_end","ba_code","fuel","reported_mw","adjusted_mw"}
    if not required.issubset(observed.columns):raise ValueError("Observed source fields missing")
    o=observed.copy()
    o["utc_hour_end"]=pd.to_datetime(o.utc_hour_end,utc=True,errors="raise")
    if o.duplicated(["utc_hour_end","ba_code","fuel"]).any():
        raise ValueError("Duplicate observed BA/fuel/UTC hour source")
    if not o.utc_hour_end.dt.year.eq(2023).all():
        raise ValueError("Observed source not 2023")
    o["month"]=o.utc_hour_end.dt.strftime("%Y-%m")
    rows=[]
    for r in census_summary.itertuples(index=False):
        x=o[(o.month==r.month)&(o.ba_code==r.ba_code)&(o.fuel==r.fuel)]
        for field in ("reported_mw","adjusted_mw"):
            vals=pd.to_numeric(x[field],errors="coerce")
            rows.append({
              "month":r.month,"ba_code":r.ba_code,"fuel":r.fuel,
              "source_MW_variant":field,
              "expected_UTC_hour_ends":pd.Period(r.month).days_in_month*24,
              "actual_timestamp_rows":len(x),"non_null_MW_rows":int(vals.notna().sum()),
              "month_OP_nameplate_candidate_mw":r.OP_nameplate_mw,
              "measured_BA_max_mw":float(vals.max()) if vals.notna().any() else np.nan,
              "hours_BA_MW_above_month_OP_candidate":int((vals>r.OP_nameplate_mw+1e-8).sum()),
              "max_positive_gap_mw":float(max(0.,vals.max()-r.OP_nameplate_mw)) if vals.notna().any() else np.nan,
              "status":"BA_CANDIDATE_GENERATOR_POPULATION_SCOPE_DIAGNOSTIC_NOT_VALIDATION",
              "BA_equals_state":False,"actual_measured_CF":False})
    ans=pd.DataFrame(rows)
    if len(ans)!=192:raise ValueError("Expected 192 two-version month-level comparisons")
    return ans

def run(folder,observations,out):
    folder=Path(folder);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    paths=[folder/f"{name}_generator2023.xlsx" for name in MONTHS]
    if not all(f.is_file() for f in paths):raise ValueError("Missing one or more actual monthly official workbooks")
    records,s,g,digests=census(paths)
    compare=comparison(s,pd.read_csv(observations))
    records.to_csv(out/"EIA860M_2023_original_12month_four_BA_generator_records.csv",index=False)
    s.to_csv(out/"EIA860M_2023_96_month_BA_fuel_candidate_rosters.csv",index=False)
    g.to_csv(out/"EIA860M_2023_BA_state_plant_geography_monthly.csv",index=False)
    digests.to_csv(out/"EIA860M_2023_12_source_workbook_SHA256.csv",index=False)
    compare.to_csv(out/"EIA930_2023_192_month_BA_capacity_scope_comparisons.csv",index=False)
    m={"status":"SOURCE_MONTHLY_BA_CODE_CANDIDATE_ONLY",
       "source_workbooks_authenticated":len(digests),
       "month_BA_fuel_cohorts":len(s),"source_comparison_rows":len(compare),
       "EIA860M_preliminary":True,"BA_equals_state":False,
       "EIA930_metered_fleet_coverage_certified":False,
       "observed_capacity_factor_validated":False,"paper_s_LP_changed":False}
    (out/"EIA860M_2023_monthly_scope_manifest.json").write_text(json.dumps(m,indent=2)+"\n")
    print("PAPER_S_MONTHLY_2023_BA_SOURCE_ROSTER_AUDIT",json.dumps(m))
    return s,compare

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--monthly-folder",type=Path,required=True)
    p.add_argument("--observations",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    run(a.monthly_folder,a.observations,a.out)

if __name__=="__main__":main()
