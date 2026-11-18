"""Paper S 2023 EIA-930 BA vs source ReEDS county-CF descriptive shape pilot.

2023 source weather and 2023 EIA observations ONLY. Compare designated BA
IPCO↔Idaho and PSCO↔Colorado as UNVALIDATED geographic proxies, never assume
BA equals state, installed 2023 capacity, hourly-integrated ReEDS source CF,
or a model-skill/observational superiority claim. 160 shared UTC-ended hours.
Three PRESPECIFIED clock sensitivities -1/0/+1 source hours, not clock fitting.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import h5py
import numpy as np
import pandas as pd
from energy_transition.paper_s_eia930_160h_ba_diagnostics import source_panel
from energy_transition.reeds2022_four_weather_year_siting_lp import (
    reaggregate_years,DESIGNS,STATES,HOURS
)
from energy_transition.reeds2022_county_full_state_lp import modeled_hourly_cf
from energy_transition.reeds2022_county_ac_normalized_2030 import normalized_pv_ac_cf
from energy_transition.reeds2022_explicit_weather_year_alignment import TARGET

YEAR=2023
PAIRINGS=(("IPCO","ID"),("PSCO","CO"))
FUELS=("wind","solar")
CLOCK_SHIFTS=(-1,0,1)
SCHEMES=DESIGNS
EXPECTED=2*2*2*3
OBS_WINDOW_HOURS=160
COMMON_START=pd.Timestamp("2023-07-01T08:00:00Z")
COMMON_END=pd.Timestamp("2023-07-07T23:00:00Z")

def source_to_utc_clock(target=TARGET):
    """Map 2012 source calendar labels to 2023 for July only, fixed UTC−06 clock."""
    t=pd.DatetimeIndex(target)
    if len(t)!=HOURS or t[0]!=pd.Timestamp("2012-01-01") or t.tz is not None:
        raise ValueError("Expected authenticated 2012 ReEDS reference index")
    july=(t.month==7)
    dates=t[july]
    # 2023 calendar has July 1-31; leap-day changes do not affect month/day join.
    target_2023=pd.DatetimeIndex([pd.Timestamp(year=YEAR,month=d.month,day=d.day,
                                              hour=d.hour) for d in dates])
    utc=target_2023.tz_localize("Etc/GMT+6").tz_convert("UTC")
    if len(utc)!=31*24 or utc.has_duplicates:
        raise ValueError("Bad source July 2023 clock")
    return july,utc

def metric(x,y):
    x=np.asarray(x,float);y=np.asarray(y,float)
    if x.shape!=(OBS_WINDOW_HOURS,) or y.shape!=x.shape or not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError("Incomplete/nonfinite 160h paired shapes")
    if np.ptp(x)<1e-12 or np.ptp(y)<1e-12:raise ValueError("Constant trace")
    # Both scales normalized on the SAME 160 observed/model-hour matched window,
    # not independently to physical installed nameplate MW.
    # Using positive 95th percentile preserves negative reported BA net generation.
    xscale=float(np.percentile(x[x>0],95))
    yscale=float(np.percentile(y[y>0],95))
    if xscale<=0 or yscale<=0:raise ValueError("Nonpositive normalization scale")
    xn=x/xscale;yn=y/yscale
    return {"pearson_r":float(np.corrcoef(xn,yn)[0,1]),
            "spearman_rho":float(pd.Series(xn).corr(pd.Series(yn),method="spearman")),
            "normalized_mae":float(np.abs(xn-yn).mean()),
            "normalized_rmse":float(np.sqrt(np.mean((xn-yn)**2))),
            "observed_positive_p95_mw":xscale,
            "source_positive_p95_cf":yscale,
            "negative_reported_mw_hours":int((x<0).sum())}

def compare(observed, profiles):
    z=observed.loc[
        observed.ba_code.isin([a for a,_ in PAIRINGS])&
        observed.fuel.isin(FUELS)].copy()
    z["utc_hour_end"]=pd.to_datetime(z.utc_hour_end,utc=True)
    if z.duplicated(["ba_code","fuel","utc_hour_end"]).any():raise ValueError("Duplicate EIA BA hours")
    expected=pd.date_range(COMMON_START,COMMON_END,freq="h",tz="UTC")
    july,source_utc=source_to_utc_clock()
    rows=[]; hourly=[]
    for ba,state in PAIRINGS:
        for fuel in FUELS:
            source=z[(z.ba_code==ba)&(z.fuel==fuel)].set_index("utc_hour_end")
            if len(source)!=OBS_WINDOW_HOURS or not source.index.isin(expected).all() or set(source.index)!=set(expected):
                raise ValueError("Missing common BA hourly 2023 source")
            source=source.reindex(expected)
            obs=source.reported_mw.to_numpy(float)
            for scheme in SCHEMES:
                values=np.asarray(profiles[(fuel,state,scheme)],float)
                if values.shape!=(HOURS,) or not np.isfinite(values).all():
                    raise ValueError("Invalid source ReEDS profile")
                native=pd.Series(values[july],index=source_utc)
                for shift in CLOCK_SHIFTS:
                    # Compare source instant at observed hour-ending + shift.
                    requested=expected+pd.Timedelta(hours=shift)
                    candidate=native.reindex(requested)
                    if candidate.isna().any():raise ValueError("2023 ReEDS source time coverage gap")
                    cf=candidate.to_numpy(float)
                    m=metric(obs,cf)
                    rows.append({"ba_code":ba,"proxy_state":state,"fuel":fuel,
                                 "siting_scheme":scheme,"source_clock_shift_hours":shift,
                                 "sample_hours":OBS_WINDOW_HOURS,
                                 "geographic_mapping_verified":False,
                                 "source_hour_integrated_verified":False,
                                 "observational_validation":False,**m})
                    # Hour-level pairs used for reproducible plotted profiles, with
                    # source values labeled explicitly as proxy, not measured CF.
                    for time,o,v in zip(expected,obs,cf):
                        hourly.append({"ba_code":ba,"proxy_state":state,"fuel":fuel,
                                       "siting_scheme":scheme,"source_clock_shift_hours":shift,
                                       "utc_hour_end":time.isoformat(),
                                       "eia930_reported_mw":float(o),
                                       "reeds_source_CF_proxy":float(v)})
    result=pd.DataFrame(rows)
    if len(result)!=EXPECTED or len(hourly)!=EXPECTED*OBS_WINDOW_HOURS:
        raise ValueError("Incomplete BA/fuel/siting/clock matrix")
    return result,pd.DataFrame(hourly)

def run(wind_h5,pv_h5,wind_sc,pv_sc,county_shares,wind_ref,pv_ref,observed_csv,out):
    observed=source_panel(observed_csv,verify_hash=True)
    winds,_,wt=reaggregate_years(wind_h5,wind_sc,"wind",county_shares,wind_ref,years=(2012,YEAR))
    solar,_,pt=reaggregate_years(pv_h5,pv_sc,"pv",county_shares,pv_ref,years=(2012,YEAR))
    if not wt.equals(pt):raise ValueError("Wind PV time labels disagree")
    profiles={}
    for scheme in SCHEMES:
        for _,state in PAIRINGS:
            profiles[("wind",state,scheme)]=modeled_hourly_cf(
                winds[(YEAR,scheme,state)],"trapezoid_with_first_endpoint")
            profiles[("solar",state,scheme)]=normalized_pv_ac_cf(
                modeled_hourly_cf(solar[(YEAR,scheme,state)],"trapezoid_with_first_endpoint"))
    scores,hourly=compare(observed,profiles)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    scores.to_csv(out/"paper_s_2023_july_eia930_160h_BA_state_PROXY_shape_metrics.csv",
                  index=False,float_format="%.12g")
    hourly.to_csv(out/"paper_s_2023_july_eia930_160h_BA_state_PROXY_hour_pairs.csv",
                  index=False,float_format="%.12g")
    manifest={"status":"DESCRIPTIVE_BA_TO_STATE_PROXY_COMPARISON_ONLY",
              "source_weather_year":YEAR,"eia930_observation_year":YEAR,
              "source_calendar":"fixed CST UTC-06:00",
              "observation_hour_ending_utc":True,
              "hour_mapping_shifts":list(CLOCK_SHIFTS),
              "common_hours":OBS_WINDOW_HOURS,
              "tested_proxy_pairs":[list(x) for x in PAIRINGS],
              "total_shape_metric_rows":len(scores),"hour_pairs":len(hourly),
              "BA_equals_state_assumed":False,
              "observational_validation_admitted":False,
              "hour_energy_integration_certified":False,
              "source_CF_instantaneous_sample":True,
              "observed_capacity_normalization_verified":False,
              "actual_2023_operating_weight_calibrated":False,
              "source_reported_negative_MW_preserved":True,
              "paper_s_frozen_LPs_modified":False,"paper_c2_modified":False}
    (out/"paper_s_2023_july_proxy_comparison_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("PAPER_S_2023_COMMON_WEATHER_BA_PROXY_DIAGNOSTIC_COMPLETE",json.dumps(manifest))
    return scores,hourly

def main():
    p=argparse.ArgumentParser()
    for name in ("wind_h5","pv_h5","wind_sc","pv_sc","county_shares",
                 "wind_ref","pv_ref","observed_csv"):
        p.add_argument("--"+name.replace("_","-"),type=Path,required=True)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    run(a.wind_h5,a.pv_h5,a.wind_sc,a.pv_sc,a.county_shares,
        a.wind_ref,a.pv_ref,a.observed_csv,a.out)
if __name__=="__main__":main()
