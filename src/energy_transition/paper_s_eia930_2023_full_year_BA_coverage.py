"""Reconcile 2023 full-year authentic EIA-930 BA wind/solar UTC-hour coverage.

Two independently MD5-pinned PUDL-mirrored raw EIA-930 source half-year
archives. Does not impute missing hours, assign BA power to a state, or
normalize source MW by unverifiable BA-installed capacity. First verifies
half-year archive identity and balances; also detects June/July overlaps.
"""
from __future__ import annotations
import argparse,hashlib,json,zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from energy_transition.paper_s_eia930_2023h2_ba_observed_extract import (
    BAS,TECHS,TIME_COL,BA_COL
)

SOURCE_RECORD="https://zenodo.org/records/22856870"
SOURCE_HALF={
    "half1":("eia930-2023half1.zip","eia930-2023half1-balance.csv",
             "1b4acef4e1ec596cf92e7658f9be64c7"),
    "half2":("eia930-2023half2.zip","eia930-2023half2-balance.csv",
             "1de4e47693426671123bb08ec0d33995")
}
START=pd.Timestamp("2023-01-01T00:00:00Z")
HALF=pd.Timestamp("2023-07-01T00:00:00Z")
END=pd.Timestamp("2024-01-01T00:00:00Z")
EXPECTED_HOURS=8760

def read_half(path,half):
    if half not in SOURCE_HALF:raise ValueError("Unrecognized raw archive half")
    filename,rawname,expected_md5=SOURCE_HALF[half]
    path=Path(path)
    if path.name!=filename:raise ValueError(f"Wrong half-year archive basename: {path.name}")
    md5=hashlib.md5()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(2**20),b""):md5.update(block)
    if md5.hexdigest()!=expected_md5:raise ValueError("Raw EIA-930 archive MD5 does not match publisher mirror")
    start,stop=(START,HALF) if half=="half1" else (HALF,END)
    all_parts=[]
    usecols=[BA_COL,TIME_COL]
    for tech in TECHS.values():
        base=f"Net Generation (MW) from {tech}"
        usecols.extend([base,base+" (Imputed)",base+" (Adjusted)"])
    with zipfile.ZipFile(path) as z:
        if rawname not in z.namelist():
            raise ValueError(f"Expected raw balance file not present: {rawname}")
        with z.open(rawname) as stream:
            for chunk in pd.read_csv(stream,usecols=usecols,chunksize=50000,
                                     encoding="utf-8-sig",low_memory=False):
                d=chunk.loc[chunk[BA_COL].isin(BAS)].copy()
                if d.empty:continue
                d["utc_hour_end"]=pd.to_datetime(
                    d[TIME_COL],format="%m/%d/%Y %I:%M:%S %p",
                    utc=True,errors="raise")
                d=d.loc[(d.utc_hour_end>=start)&(d.utc_hour_end<stop)]
                if d.empty:continue
                for fuel,tech in TECHS.items():
                    base=f"Net Generation (MW) from {tech}"
                    f=d[[BA_COL,"utc_hour_end",base,
                         base+" (Imputed)",base+" (Adjusted)"]].copy()
                    f.columns=["ba_code","utc_hour_end","reported_mw",
                               "imputed_mw","adjusted_mw"]
                    f["fuel"]=fuel
                    for c in ("reported_mw","imputed_mw","adjusted_mw"):
                        f[c]=pd.to_numeric(f[c],errors="coerce")
                        if np.isinf(f[c].to_numpy(float)).any():
                            raise ValueError("Nonfinite source MW")
                    f["source_half"]=half
                    all_parts.append(f)
    if not all_parts:raise ValueError(f"No selected BAs in {half}")
    d=pd.concat(all_parts,ignore_index=True)
    if d.duplicated(["ba_code","fuel","utc_hour_end"]).any():
        raise ValueError(f"Duplicated raw {half} BA fuel hour-ending row")
    return d

def annual_coverage(panel):
    expect=pd.date_range(START,END,freq="h",inclusive="left")
    if len(expect)!=EXPECTED_HOURS:raise ValueError("2023 not 8760 hour")
    if panel.duplicated(["ba_code","fuel","utc_hour_end"]).any():
        raise ValueError("Raw half-year archive UTC overlap, duplicate BA/fuel/hour")
    if panel.utc_hour_end.isna().any() or not panel.utc_hour_end.isin(expect).all():
        raise ValueError("Invalid 2023 UTC observation source clock")
    summary=[];monthly=[];missing=[]
    for ba in BAS:
        for fuel in TECHS:
            source=panel[(panel.ba_code==ba)&(panel.fuel==fuel)].set_index("utc_hour_end")
            gaps=expect.difference(source.index)
            missing.extend({"ba_code":ba,"fuel":fuel,"utc_hour_end":t.isoformat()}
                           for t in gaps)
            summary.append({
                "ba_code":ba,"fuel":fuel,"expected_UTC_hour_count":len(expect),
                "source_timestamp_count":len(source),
                "missing_source_hour_ending_count":len(gaps),
                "non_null_reported_MW_count":int(source.reported_mw.notna().sum()),
                "null_reported_MW_on_present_hour":int(source.reported_mw.isna().sum()),
                "negative_reported_MW_count":int((source.reported_mw<0).sum()),
                "imputed_non_null_count":int(source.imputed_mw.notna().sum()),
                "adjusted_non_null_count":int(source.adjusted_mw.notna().sum()),
                "max_reported_MW":float(source.reported_mw.max()) if source.reported_mw.notna().any() else None,
                "source_halves_present":";".join(sorted(source.source_half.unique())),
                "BA_equals_state":False,"observed_capacity_factor_validated":False,
            })
            for m in range(1,13):
                idx=expect[expect.month==m]
                relevant=source.reindex(idx)
                present=idx.isin(source.index)
                monthly.append({
                    "ba_code":ba,"fuel":fuel,"month":f"2023-{m:02d}",
                    "expected_UTC_hour_count":len(idx),
                    "source_timestamp_count":int(present.sum()),
                    "missing_source_hour_ending_count":int((~present).sum()),
                    "non_null_reported_MW_count":int(relevant.reported_mw.notna().sum()),
                    "null_reported_MW_on_present_hour":int(
                        relevant.loc[present,"reported_mw"].isna().sum()),
                    "negative_reported_MW_count":int((relevant.reported_mw<0).sum()),
                })
    summary=pd.DataFrame(summary)
    monthly=pd.DataFrame(monthly)
    if len(summary)!=8 or len(monthly)!=96:raise ValueError("Missing year/BA/fuel cohorts")
    if not summary.source_timestamp_count.add(summary.missing_source_hour_ending_count).eq(EXPECTED_HOURS).all():
        raise ValueError("Nonconserving year-coverage accounting")
    if not summary.non_null_reported_MW_count.add(summary.null_reported_MW_on_present_hour).eq(summary.source_timestamp_count).all():
        raise ValueError("Nonconserving null-value accounting")
    return summary,monthly,pd.DataFrame(missing,columns=["ba_code","fuel","utc_hour_end"])

def run(h1,h2,out):
    a=read_half(h1,"half1");b=read_half(h2,"half2")
    full=pd.concat([a,b],ignore_index=True).sort_values(["ba_code","fuel","utc_hour_end"])
    s,m,g=annual_coverage(full)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    full.to_csv(out/"paper_s_eia930_2023_annual_BA_wind_solar_reported_MW.csv",index=False)
    s.to_csv(out/"paper_s_eia930_2023_annual_8_BA_fuel_coverage.csv",index=False)
    m.to_csv(out/"paper_s_eia930_2023_annual_96_month_BA_fuel_coverage.csv",index=False)
    g.to_csv(out/"paper_s_eia930_2023_annual_missing_UTC_hours.csv",index=False)
    manifest={
       "status":"SOURCE_VERIFIED_2023_FULL_YEAR_BA_COVERAGE_NOT_EXTERNAL_VALIDATION",
       "source_record":SOURCE_RECORD,
       "source_half1_md5":SOURCE_HALF["half1"][2],
       "source_half2_md5":SOURCE_HALF["half2"][2],
       "annual_UTC_half_open":[START.isoformat(),END.isoformat()],
       "expected_hours_per_BA_fuel":EXPECTED_HOURS,
       "source_row_count":len(full),
       "source_missing_hours":len(g),
       "source_null_reported_on_present_rows":int(s.null_reported_MW_on_present_hour.sum()),
       "source_negative_reported_MW":int(s.negative_reported_MW_count.sum()),
       "BA_equals_state":False,
       "hour_integrated_MWh_verified":False,
       "observed_capacity_factor_validated":False,
       "model_skill_validated":False,
       "source_roster_capacity_denominator_reconciled":False,
       "LPs_reoptimized":False,
    }
    (out/"paper_s_eia930_2023_annual_BA_coverage_manifest.json").write_text(
        json.dumps(manifest,indent=2)+"\n")
    print("PAPER_S_2023_FULL_YEAR_BA_HOURLY_COVERAGE_AUDITED",json.dumps(manifest))
    return s,m,g

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive-h1",required=True,type=Path)
    p.add_argument("--archive-h2",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    x=p.parse_args()
    run(x.archive_h1,x.archive_h2,x.out)

if __name__=="__main__":main()
