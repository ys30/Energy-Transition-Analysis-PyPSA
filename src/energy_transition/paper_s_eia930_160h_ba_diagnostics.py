"""Descriptive BA-level diagnostics for checksum-pinned observed EIA-930 MW.

Do not call correlation between balancing authorities model validation.
No state crosswalk, measured installed-capacity denominator, or ReEDS
co-timed comparison is supplied here.
"""
from __future__ import annotations
import argparse, hashlib, json
from itertools import combinations
from pathlib import Path
import pandas as pd
import numpy as np

SOURCE_SHA256="0e72513a99c920391c0fc51a1691e84780ca5da81ba0c34b2fe218ed3fbc2f5a"
SOURCE_ARTIFACT_ID=14150700990
COMMON_START="2023-07-01T08:00:00Z"
COMMON_END="2023-07-07T23:00:00Z"
BAS=("PNM","PSCO","IPCO","WACM")
FUELS=("wind","solar")
VALIDATION_STATUS="DESCRIPTIVE_OBSERVED_BA_ONLY"

def source_panel(path,verify_hash=True):
    path=Path(path)
    if verify_hash and hashlib.sha256(path.read_bytes()).hexdigest()!=SOURCE_SHA256:
        raise ValueError("Pinned actual EIA930 source CSV SHA256 mismatch")
    d=pd.read_csv(path)
    required={"ba_code","fuel","utc_hour_end","reported_mw","adjusted_mw","imputed_mw"}
    if not required.issubset(d.columns):raise ValueError("Missing source columns")
    d["utc_hour_end"]=pd.to_datetime(d.utc_hour_end,utc=True,errors="raise")
    start=pd.Timestamp(COMMON_START)
    end=pd.Timestamp(COMMON_END)
    d=d.loc[(d.utc_hour_end>=start)&(d.utc_hour_end<=end)].copy()
    if d.duplicated(["ba_code","fuel","utc_hour_end"]).any():
        raise ValueError("Duplicate BA fuel hour")
    if set(d.ba_code)!=set(BAS) or set(d.fuel)!=set(FUELS):
        raise ValueError("Unverified BA or missing technology series")
    expected=pd.date_range(start,end,freq="h",tz="UTC")
    for ba in BAS:
        for fuel in FUELS:
            group=d[(d.ba_code==ba)&(d.fuel==fuel)]
            if len(group)!=len(expected) or not pd.DatetimeIndex(group.utc_hour_end).equals(expected):
                # Input order-independent comparison of actual time labels
                if set(group.utc_hour_end)!=set(expected):
                    raise ValueError("Incomplete common UTC hour-end panel")
    for field in ("reported_mw","adjusted_mw","imputed_mw"):
        d[field]=pd.to_numeric(d[field],errors="coerce")
    if d.reported_mw.isna().any():raise ValueError("Reported MW missing")
    if not np.isfinite(d.reported_mw).all():raise ValueError("Nonfinite reported MW")
    return d

def diagnostics(d):
    summary=[]
    for (ba,fuel),g in sorted(d.groupby(["ba_code","fuel"])):
        vals=g.reported_mw
        neg=vals[vals<0]
        summary.append({
            "ba_code":ba,"fuel":fuel,"sample_hours":len(g),
            "negative_hours":int(len(neg)),
            "negative_hour_fraction":float((vals<0).mean()),
            "min_reported_mw":float(vals.min()),
            "max_reported_mw":float(vals.max()),
            "mean_reported_mw":float(vals.mean()),
            "mean_zero_clipped_mw_diagnostic_only":float(vals.clip(lower=0).mean()),
            "clipping_raises_mean_mw":float(vals.clip(lower=0).mean()-vals.mean()),
            "imputed_nonmissing_hours":int(g.imputed_mw.notna().sum()),
            "reported_adjusted_different_hours":int(((g.reported_mw!=g.adjusted_mw)&g.adjusted_mw.notna()).sum()),
        })
    corr=[]
    for fuel in FUELS:
        pivot=d.loc[d.fuel==fuel].pivot(
            index="utc_hour_end",columns="ba_code",values="reported_mw")
        for a,b in combinations(BAS,2):
            rho=pivot[a].corr(pivot[b],method="spearman")
            if not np.isfinite(rho):raise ValueError("Cannot calculate pairwise rank correlation")
            corr.append({
                "fuel":fuel,"ba_a":a,"ba_b":b,"paired_hour_count":len(pivot),
                "spearman_rho":float(rho),
                "interpretation":"BA-to-BA descriptive similarity only; not ReEDS validation",
            })
    return pd.DataFrame(summary),pd.DataFrame(corr)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    d=source_panel(args.source)
    summary,corr=diagnostics(d)
    args.out.mkdir(parents=True,exist_ok=True)
    summary.to_csv(args.out/"eia930_2023_july_160h_ba_mw_negative_sensitivity.csv",index=False)
    corr.to_csv(args.out/"eia930_2023_july_160h_cross_ba_rank_correlations.csv",index=False)
    manifest={
        "status":VALIDATION_STATUS,"pinned_observation_artifact_id":SOURCE_ARTIFACT_ID,
        "observation_csv_sha256":SOURCE_SHA256,
        "common_UTC_hour_end_start":COMMON_START,
        "common_UTC_hour_end_end":COMMON_END,
        "rows":len(d),"unique_hours":int(d.utc_hour_end.nunique()),
        "ba_fuel_series":len(summary),"negative_source_MW_hours":int(summary.negative_hours.sum()),
        "BA_is_state":False,"observed_vs_ReEDS_validation":False,
        "installed_capacity_denominator_source_verified":False,
        "reported_negative_values_preserved":True,
        "zero_clipped_statistics_are_sensitivity_only":True,
        "spearman_cross_ba_not_forecast_skill":True,
    }
    (args.out/"eia930_2023_july_160h_ba_mw_diagnostics_manifest.json").write_text(
        json.dumps(manifest,indent=2)+"\n")
    print("EIA930_160H_BA_DESCRIPTIVE_DIAGNOSTICS_PASS",json.dumps(manifest))
if __name__=="__main__":main()
