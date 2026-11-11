"""Cross-technology ReEDS2022 2012 county-derived instantaneous CF diagnostics.

INPUTS: publisher-authenticated wind/pv state CF artifacts from Actions run
42962740548; no demand-hour-ending/energy join or LP claimed.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

STATES=("AZ","CO","ID","WY")
N=8760
FIRST="2012-01-01 00:00:00-06:00"
LAST="2012-12-30 23:00:00-06:00"

def read_native(path,tech):
    x=pd.read_csv(path)
    required=["source_instantaneous_CST",*STATES]
    if list(x.columns)!=required or len(x)!=N:
        raise ValueError(f"{tech} source state CF requires 8760 rows and exact columns")
    idx=pd.to_datetime(x["source_instantaneous_CST"],utc=True)
    expected=pd.date_range(FIRST,periods=N,freq="h").tz_convert("UTC")
    if not pd.DatetimeIndex(idx).equals(expected):
        raise ValueError(f"{tech} CST timestamp validation failed")
    for st in STATES:
        if not np.isfinite(x[st]).all() or not x[st].between(0,1).all():
            raise ValueError(f"{tech}/{st} normalized CF outside [0,1]")
    return x,idx

def analyze(wind_file,pv_file):
    w,t=read_native(wind_file,"wind")
    s,t2=read_native(pv_file,"pv")
    if not t.equals(t2):
        raise ValueError("Wind and PV native instantaneous time labels disagree")
    local=t.tz_convert("Etc/GMT+6")
    by_hour=[]
    states={}
    for st in STATES:
        wf=w[st].to_numpy(dtype=float)
        sf=s[st].to_numpy(dtype=float)
        # An exploratory, instantaneous-only shape diagnosis; no MWh or load join.
        corr=float(np.corrcoef(wf,sf)[0,1])
        states[st]={
            "wind_mean_instantaneous_cf":float(wf.mean()),
            "pv_mean_instantaneous_cf":float(sf.mean()),
            "wind_pv_instantaneous_correlation":corr,
            "wind_pv_both_below_0p1_hours":int(np.sum((wf<.1)&(sf<.1))),
            "wind_pv_both_above_0p3_hours":int(np.sum((wf>.3)&(sf>.3))),
        }
        for hour in range(24):
            m=local.hour==hour
            by_hour.append({"state":st,"CST_hour":hour,
                "wind_instantaneous_cf_mean":float(wf[m].mean()),
                "pv_instantaneous_cf_mean":float(sf[m].mean())})
    report={
        "status":"AUTHENTICATED_RESOURCE_INSTANTANEOUS_SHAPE_DIAGNOSTIC",
        "source_workflow_run":42962740548,
        "native_time_standard":"2012 fixed CST UTC-06:00",
        "reference_weather_year":2012,
        "hour_count":N,
        "weather_hourly_energy_integral_certified":False,
        "demand_hour_ending_join_admitted":False,
        "installed_capacity_scenario_defined":False,
        "LP_solved":False,
        "states":states,
    }
    return report,pd.DataFrame(by_hour)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--wind",type=Path,required=True)
    p.add_argument("--pv",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    summary,hourly=analyze(a.wind,a.pv)
    a.out.mkdir(parents=True,exist_ok=True)
    (a.out/"reeds2022_2012_wind_pv_instantaneous_state_shape_diagnostic.json").write_text(json.dumps(summary,indent=2)+"\n")
    hourly.to_csv(a.out/"reeds2022_2012_wind_pv_state_hour_of_day.csv",index=False)
    print(json.dumps(summary,indent=2))
if __name__=="__main__":
    main()
