"""Audit observed EIA-930 BA wind/solar hourly shapes without treating them as potential.

Signed values and negative hourly net generation are preserved. The four
selected complete weeks are descriptive only; not weather-year or forward
renewable capacity-factor forecasts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

SEASONS=("winter","spring","summer","autumn")
BAS=("CISO","BPAT")
FUELS=("SUN","WND")
HOURS=168

def audit(raw:pd.DataFrame):
    keys=("season","period","respondent","fueltype","reported_signed_net_mwh")
    if not set(keys).issubset(raw.columns):
        raise ValueError("Missing required EIA-930 observed renewable columns")
    d=raw.copy()
    if d[list(keys)].isna().any().any():
        raise ValueError("Missing EIA-930 observed values")
    d["period"]=pd.to_datetime(d["period"],utc=True,errors="raise")
    d["reported_signed_net_mwh"]=pd.to_numeric(d["reported_signed_net_mwh"],errors="raise")
    if d.duplicated(["season","period","respondent","fueltype"]).any():
        raise ValueError("Duplicate observed BA-fuel-season UTC hour")
    if not np.isfinite(d.reported_signed_net_mwh.to_numpy()).all():
        raise ValueError("Nonfinite observed signed net generation")
    expected={(s,b,f) for s in SEASONS for b in BAS for f in FUELS}
    if set(zip(d.season,d.respondent,d.fueltype))!=expected:
        raise ValueError("Unexpected observed BA fuel seasonal coverage")
    rows=[]
    for (season,ba,fuel),g in d.groupby(["season","respondent","fueltype"]):
        g=g.sort_values("period")
        times=pd.DatetimeIndex(g.period)
        if len(g)!=HOURS or not (times[1:]-times[:-1]==pd.Timedelta(hours=1)).all():
            raise ValueError(f"Incomplete or non-hourly EIA-930 observations: {season}/{ba}/{fuel}")
        vals=g.reported_signed_net_mwh.to_numpy(dtype=float)
        ramps=np.diff(vals)
        positives=np.maximum(vals,0.)
        max_pos=float(positives.max())
        rows.append({
            "season":str(season),"ba_code":str(ba),"fueltype":str(fuel),
            "n_observed_hours":len(vals),
            "signed_reported_generation_mwh":float(vals.sum()),
            "positive_component_mwh":float(positives.sum()),
            "negative_component_mwh":float(np.minimum(vals,0.).sum()),
            "negative_hours":int((vals<0).sum()),
            "positive_net_hours":int((vals>0).sum()),
            "zero_net_hours":int((vals==0).sum()),
            "signed_hourly_mean_mwh":float(vals.mean()),
            "signed_hourly_std_mwh":float(vals.std()),
            "signed_net_peak_positive_hour_mwh":max_pos,
            "max_abs_one_hour_reported_net_ramp_mwh":float(np.abs(ramps).max()),
            "mean_abs_one_hour_reported_net_ramp_mwh":float(np.abs(ramps).mean()),
            "observed_signed_net_shape_not_capacity_factor":True,
        })
    summary=pd.DataFrame(rows).sort_values(["season","ba_code","fueltype"]).reset_index(drop=True)
    if len(summary)!=16:
        raise ValueError("Incomplete independent BA/fuel seasonal panels")
    if not np.allclose(summary.signed_reported_generation_mwh,
                       summary.positive_component_mwh+summary.negative_component_mwh,
                       rtol=1e-12,atol=1e-7):
        raise ValueError("Negative signed generation energy conservation failed")
    metadata={
        "status":"OBSERVED_EIA930_2024_FOUR_WEEK_SIGNED_NET_SHAPE_ACCEPTED",
        "source_family":"EIA-930 historical BA-level net generation by fuel",
        "original_source_year":2024,"seasons":list(SEASONS),
        "balancing_authorities":list(BAS),"fueltypes":list(FUELS),
        "expected_hourly_records":4*2*2*168,
        "expected_independent_panels":16,
        "datetime_index":"Parsed source EIA-930 period UTC; per-hour integrated generation (MWh)",
        "hours_are_2024_observed_seasonal_windows_only":True,
        "all_hours_of_2024_complete":False,
        "reported_negative_net_generation_retained":True,
        "actual_meteorological_resource_availability_measured":False,
        "matching_generation_nameplate_verified":False,
        "renewable_capacity_factor_valid":False,
        "efs_2030_2050_hour_alignment_admitted":False,
        "future_renewable_resource_forecast_admitted":False,
        "physical_Western_OPF_admitted":False,
        "note":"Observed generation is dispatched signed BA net production, not unconstrained generation potential or a capacity factor. Historical UTC observations cannot be joined to EFS LocalHourID by ordinal."
    }
    return summary,metadata


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--seasonal",type=Path,required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    a=p.parse_args()
    summary,meta=audit(pd.read_csv(a.seasonal))
    meta["source_csv_sha256"]=hashlib.sha256(a.seasonal.read_bytes()).hexdigest()
    a.out_dir.mkdir(parents=True,exist_ok=True)
    summary.to_csv(a.out_dir/"observed_2024_eia930_four_week_ba_fuel_shapes.csv",index=False)
    (a.out_dir/"observed_2024_eia930_shape_provenance.json").write_text(json.dumps(meta,indent=2)+"\n")
    print(summary.to_string(index=False))
    print(json.dumps(meta,indent=2))


if __name__=="__main__":
    main()
