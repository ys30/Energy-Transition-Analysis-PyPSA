"""Paper S independent ReEDS2022 authentic 2012 wind/PV demand matching pilot.

Source 2022 ReEDS EFS_REFERENCE HDF5 state demand has an explicitly
documented 2012 fixed CST hour-ending clock. Original wind/PV v1 HDF5
contains instantaneous CF on exactly corresponding source CST timestamps.
We explicitly *approximate* hourly average generation by trapezoidal
integration of consecutive actual instants, comparing it with instantaneous
sampling as sensitivity. This numerical interval assumption is not
publisher-certified actual hourly generation.

For state source representativeness, include only ReEDS BA zones for which
ALL listed counties in the official county2zone crosswalk share one state.
This yields a within-state resource-potential subset, not a complete
state renewable fleet. Existing ReEDS BA multi-state zones are excluded
rather than assigned by an invented weight. Potential MW class weights are
illustrative supply weights, NOT measured installed capacity.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import numpy as np
import pandas as pd
from .reeds2022_real_resource_intake import SOURCES,CROSSWALK_MD5,inspect_weather_index,require_md5,decode
from .reeds_2022_clocked_demand_branch import check_fixed_cst_native_labels,verify_official_file
from .efs_cyclic_storage_lp import solve_zone

STATES=("AZ","CO","ID","WY")
PROFILE_YEAR=2012
MODEL_YEAR=2030
ILR_PV=1.34
WIND_SHARE=.5
SUPPORTED_DURATIONS=(0,4)
SAMPLE_MODES=("trapezoidal_previous_instant","instantaneous_end_label")

def strict_pure_ba_crosswalk(crosswalk):
    required={"FIPS","ba","state"}
    if not required.issubset(crosswalk.columns):raise ValueError("Original county2zone schema changed")
    x=crosswalk.loc[:,["FIPS","ba","state"]].copy()
    if x.isna().any().any() or x.duplicated(["FIPS"]).any():
        raise ValueError("Invalid source counties: duplicate FIPS or missing source keys")
    x["ba"]=x.ba.astype(str)
    groups=x.groupby("ba").state.agg(lambda s: sorted(set(s.astype(str))))
    chosen={state:set(groups.loc[groups.map(lambda states:states==[state])].index) for state in STATES}
    counts=x.groupby("state").size().to_dict()
    table=[]
    for state in STATES:
        rows=x[x.state.eq(state)]
        pure=rows[rows.ba.isin(chosen[state])]
        table.append({"state":state,"source_counties_all":int(len(rows)),
                      "source_counties_in_pure_state_BAs":int(len(pure)),
                      "pure_state_BA_count":int(len(chosen[state])),
                      "county_coverage_pct":100*len(pure)/len(rows) if len(rows) else 0.,
                      "BAs_included_pipe_delimited":"|".join(sorted(chosen[state])),
                      "source_BAs_cross_state_count":int(rows.loc[~rows.ba.isin(chosen[state]),"ba"].nunique())})
    return chosen,pd.DataFrame(table)

def read_weighted_source_cf(h5_path,sc_path,tech,pure_by_state):
    import h5py
    spec=SOURCES[tech]
    require_md5(h5_path,spec["md5"]);require_md5(sc_path,spec["capacity_md5"])
    sc=pd.read_csv(sc_path)
    if list(sc.columns)!=["class|region","MW"] or sc["class|region"].duplicated().any():
        raise ValueError("Unexpected original ReEDS resource potential schema")
    mw=pd.to_numeric(sc.MW,errors="raise")
    if (mw<0).any() or not np.isfinite(mw).all():raise ValueError("Invalid original potential MW")
    weights=dict(zip(sc["class|region"].astype(str),mw.astype(float)))
    with h5py.File(h5_path,"r") as f:
        columns=decode(f["columns"][:])
        if len(set(columns))!=len(columns):raise ValueError("Duplicate original resource columns")
        raw=f["index_0"][:]
        idx,clock=inspect_weather_index(raw)
        if idx[0]<=0:raise ValueError("2012 first hourly resource lacks real previous-hour value")
        # Original preceding source timestamp is 2011-12-31 23:00 CST.
        labels=decode(raw)
        preceding=pd.Timestamp(labels[int(idx[0]-1)]).tz_convert("UTC")
        start=pd.Timestamp(labels[int(idx[0])]).tz_convert("UTC")
        if start-preceding!=pd.Timedelta(hours=1):raise ValueError("Missing true previous calendar-year hour")
        selection=np.r_[idx[0]-1,idx]
        data=np.asarray(f["data"][int(selection[0]):int(selection[-1]+1),:],dtype=float)
        if data.shape!=(8761,len(columns)) or not np.isfinite(data).all():
            raise ValueError("Incomplete actual source 2011/2012 hourly data")
        if data.min()<-1e-8 or data.max()>1.+1e-8:
            raise ValueError("Actual source CF values are outside [0,1]")
        cnum={c:i for i,c in enumerate(columns)}
        annual=[]; profiles={}
        for state in STATES:
            keys=[k for k in columns if k.split("|")[-1] in pure_by_state[state] and weights.get(k,0.)>0.]
            if not keys:raise ValueError("No source-backed pure-state BA resource potential for "+tech+"/"+state)
            missing=[k for k in keys if k not in weights]
            if missing:raise ValueError("Original resource class capacity key missing")
            cols=[cnum[k] for k in keys]
            cap=np.array([weights[k] for k in keys],dtype=float)
            total=float(cap.sum())
            if total<=0:raise ValueError("Zero source potential "+state)
            instantaneous=np.average(data[:,cols],axis=1,weights=cap)
            if tech=="pv":instantaneous*=ILR_PV
            if instantaneous.min()<-1e-8 or instantaneous.max()>1.+2e-4:
                raise ValueError("AC-normalized capacity factors outside [0,1]")
            # The 8761 source instants span preceding 2011 hour through
            # the final 2012 hour; estimated hourly mean is trapezoidal.
            trap=.5*(instantaneous[:-1]+instantaneous[1:])
            end=instantaneous[1:]
            profiles[state]={"trapezoidal_previous_instant":np.clip(trap,0,1),
                 "instantaneous_end_label":np.clip(end,0,1)}
            annual.append({"technology":tech,"state":state,
                 "pure_state_resource_BA_count":int(len({k.split("|")[-1] for k in keys})),
                 "resource_classes":len(keys),"potential_capacity_mw":total,
                 "calendar_year":2012,"trapezoidal_annual_mean_cf":float(trap.mean()),
                 "end_instant_annual_mean_cf":float(end.mean()),
                 "trapezoid_minus_end_total_cf_hours":float((trap-end).sum()),
                 "first_matched_UTC_instant":start.isoformat(),
                 "last_matched_UTC_instant":pd.Timestamp(labels[int(idx[-1])]).tz_convert("UTC").isoformat(),
                 "2011_preceding_instant_checked":True,
                 "source_profiler_md5":spec["md5"],
                 "source_cf_IS_hourly_energy_verified":False})
        return profiles,pd.DataFrame(annual),clock

def solve(h5_demand,wind_h5,pv_h5,wind_sc,pv_sc,crosswalk,output):
    import h5py
    verify_official_file(h5_demand)
    require_md5(crosswalk,CROSSWALK_MD5)
    county=pd.read_csv(crosswalk,dtype={"FIPS":str})
    pure,coverage=strict_pure_ba_crosswalk(county)
    wind,w_info,w_clock=read_weighted_source_cf(wind_h5,wind_sc,"wind",pure)
    solar,p_info,p_clock=read_weighted_source_cf(pv_h5,pv_sc,"pv",pure)
    if w_clock["2012_first"]!=p_clock["2012_first"] or w_clock["2012_last"]!=p_clock["2012_last"]:
        raise ValueError("Actual publisher wind/PV resource clocks do not match")
    rows=[]
    with h5py.File(h5_demand,"r") as f:
        group=f[str(MODEL_YEAR)]
        clock=check_fixed_cst_native_labels(group["datetime"][:])
        native=pd.to_datetime(decode(group["datetime"][:]),utc=True)
        source_utc_first=pd.Timestamp(w_clock["2012_first"]).tz_convert("UTC")
        source_utc_last=pd.Timestamp(w_clock["2012_last"]).tz_convert("UTC")
        if native[0]!=source_utc_first or native[-1]!=source_utc_last:
            raise ValueError("The explicitly timestamped original demand/weather source keys mismatch")
        for state in STATES:
            demand=np.asarray(group[state][:],dtype=float)
            if demand.shape!=(8760,) or not np.isfinite(demand).all() or (demand<0).any():
                raise ValueError("Original ReEDS demand invalid "+state)
            for mode in SAMPLE_MODES:
                cf=WIND_SHARE*wind[state][mode]+(1-WIND_SHARE)*solar[state][mode]
                if cf.shape!=(8760,) or (cf<0).any() or (cf>1.+1e-6).any():
                    raise ValueError("Authentic weather-derived source availability invalid")
                for duration in SUPPORTED_DURATIONS:
                    m=solve_zone(demand,np.clip(cf,0,1),duration,renewable_peak_ratio=.9)
                    rows.append({"experiment":"Independent ReEDS2022 original-state demand + actual ReEDS2012 BA resource subset",
                       "state":state,"model_year":MODEL_YEAR,"weather_year":PROFILE_YEAR,
                       "source_clock":"2012 CST UTC-06:00",
                       "hour_approximation":mode,"battery_duration_h":duration,
                       "wind_share_illustrative_installed_MW":WIND_SHARE,
                       "pv_share_illustrative_installed_MW":1-WIND_SHARE,
                       "source_demand_h5_md5":"7b2055d43200744a16a8c4fed68b1a17",
                       "real_source_weather_available":True,
                       "physical_hour_energy_exact":False,
                       "within_state_BA_subset_only":True,
                       "state_complete_resource_allocation":False,
                       "real_Western_network_OPF":False,**m})
    summary=pd.DataFrame(rows)
    output.mkdir(parents=True,exist_ok=True)
    summary.to_csv(output/"paper_s_reeds2022_real_resource_2030_lp_16_scenarios.csv",index=False,float_format="%.12g")
    coverage.to_csv(output/"paper_s_reeds2022_pure_state_BA_coverage.csv",index=False)
    pd.concat([w_info,p_info]).to_csv(output/"paper_s_reeds2022_wind_pv_original_capacity_source_summary.csv",index=False)
    manifest={"status":"REEDS2022_ACTUAL_WIND_AND_PV_SOURCE_RESTRICTED_RESOURCE_SUBSET_LP_PASS",
      "source_2012_real_weather_profile":True,"hour_boundary_approximated_not_verified":True,
      "four_states":STATES,"model_year":MODEL_YEAR,"weather_year":PROFILE_YEAR,
      "publisher_source_MD5_checked":True,
      "source_wind_pv_native_clock_matched_to_demand_source":True,
      "source_CST_hour_ending_load_vs_instant_CF":"Trapezoid numerical approximation + direct end-instant sensitivity; no assertion that point-value equals hourly mean",
      "BA_county_crosswalk_restricted_to_wholly_within_state":True,
      "whole_state_resource_fleet_calibrated":False,"capacity_share_assumed_not_observed":True,
      "physical_network_or_reliability_estimate":False,
      "LPs":len(rows),"old_EFS2020_results_modified":False}
    (output/"paper_s_reeds2022_real_source_model_boundary.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(summary[["state","hour_approximation","battery_duration_h","demand_mwh",
                   "storage_discharge_to_load_mwh","firm_generation_mwh","unused_renewable_mwh",
                   "objective_illustrative_variable_usd"]].to_string(index=False))
    print(coverage[["state","source_counties_all","source_counties_in_pure_state_BAs","county_coverage_pct","pure_state_BA_count"]].to_string(index=False))
    print("REAL_WIND_PV_2012_SOURCE_LP_PILOT_PASSED_ASSUMPTION_BOUNDED_NOT_REAL_NETWORK")
    return summary

def main():
 a=argparse.ArgumentParser()
 for name in ("demand_h5","wind_h5","pv_h5","wind_sc","pv_sc","county2zone"):
  a.add_argument("--"+name.replace("_","-"),type=Path,required=True)
 a.add_argument("--out",type=Path,required=True)
 p=a.parse_args()
 solve(p.demand_h5,p.wind_h5,p.pv_h5,p.wind_sc,p.pv_sc,p.county2zone,p.out)
if __name__=="__main__":main()
