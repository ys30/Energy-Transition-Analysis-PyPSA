"""Paper S 3×3 renewable-penetration × wind-share siting-sensitivity matrix.

Fixed 2030 weather-2012-supported demand, 15 actual ReEDS weather years, 4 states,
two county siting weights, trapezoid source-hour approximation, 0/4/8h LP.
Full 3240 LPs = 9 design points × 360 cases. Exactly 360 ORIGINAL frozen
baseline point (R=1.5, wind share=0.5) are REUSED, yielding 2880 new solves.
This is a sensitivity study, not a weather/climate attribution experiment.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import h5py
import numpy as np
import pandas as pd
from energy_transition.reeds2022_all_weather_year_720lp import WEATHER_YEARS
from energy_transition.reeds2022_four_weather_year_siting_lp import (
    reaggregate_years, STATES, DESIGNS, DURATIONS, POWER, RTE, HOURS,
)
from energy_transition.reeds2022_county_full_state_lp import modeled_hourly_cf
from energy_transition.reeds2022_county_ac_normalized_2030 import normalized_pv_ac_cf
from energy_transition.reeds_2022_clocked_demand_branch import (
    verify_official_file, check_fixed_cst_native_labels,
)
from energy_transition.efs_cyclic_storage_lp import solve_zone

RATIOS=(1.0,1.5,2.0)
WIND_SHARES=(0.25,0.50,0.75)
BASE_RATIO=1.5
BASE_SHARE=0.50
HOUR="trapezoid_with_first_endpoint"
EXPECTED_ALL=15*4*2*3*3*3
EXPECTED_FROZEN=15*4*2*3
EXPECTED_NEW=EXPECTED_ALL-EXPECTED_FROZEN
KEYS=["weather_year","state","county_weight_scheme",
      "renewable_peak_ratio","wind_share_ac","battery_duration_h"]
PAIR_KEYS=KEYS[:-1]
SITING_KEYS=["weather_year","state","renewable_peak_ratio","wind_share_ac"]

def validate_baseline(frozen):
    required=set(["weather_year","state","county_weight_scheme","hour_approximation",
                  "battery_duration_h","storage_capacity_mwh",
                  "objective_illustrative_variable_usd","solver_status","max_equality_residual_mwh"])
    if not required.issubset(frozen.columns):
        raise ValueError("Frozen baseline data incomplete")
    z=frozen.loc[frozen.hour_approximation.eq(HOUR)].copy()
    if len(z)!=EXPECTED_FROZEN or z.solver_status.ne("optimal").any():
        raise ValueError("Expected 360 optimal frozen trapezoid cases")
    if z.max_equality_residual_mwh.max()>1e-5:raise ValueError("Frozen primal residual failure")
    k=["weather_year","state","county_weight_scheme","battery_duration_h"]
    if z.duplicated(k).any():raise ValueError("Duplicate frozen case")
    exp=pd.MultiIndex.from_product([WEATHER_YEARS,STATES,DESIGNS,DURATIONS],names=k)
    actual=pd.MultiIndex.from_frame(z[k])
    if len(exp.difference(actual)) or len(actual.difference(exp)):
        raise ValueError("Frozen case coverage drift")
    z["renewable_peak_ratio"]=BASE_RATIO
    z["wind_share_ac"]=BASE_SHARE
    return z

def validate_and_summarize(lp):
    if len(lp)!=EXPECTED_ALL or lp[KEYS].duplicated().any():
        raise ValueError("Complete 3240 unique design-sensitivity LPs required")
    exp=pd.MultiIndex.from_product(
        [WEATHER_YEARS,STATES,DESIGNS,RATIOS,WIND_SHARES,DURATIONS],names=KEYS)
    actual=pd.MultiIndex.from_frame(lp[KEYS])
    if len(exp.difference(actual)) or len(actual.difference(exp)):
        raise ValueError("Missing or extra design-sensitivity cases")
    if lp.solver_status.ne("optimal").any() or lp.max_equality_residual_mwh.max()>1e-5:
        raise ValueError("Design point LP solver feasibility failure")
    rows=[]
    for key,g in lp.groupby(PAIR_KEYS,sort=True):
        d=g.set_index("battery_duration_h")
        if set(d.index)!=set(DURATIONS):raise ValueError("Missing 0h/4h/8h duration")
        objective=d.objective_illustrative_variable_usd
        if objective.loc[0]+.1<objective.loc[4] or objective.loc[4]+.1<objective.loc[8]:
            raise ValueError("Marginal duration violates objective monotonicity")
        energy_delta=(d.loc[8,"storage_capacity_mwh"]-d.loc[4,"storage_capacity_mwh"])*1000.
        if energy_delta<=0:raise ValueError("Invalid energy denominator")
        row=dict(zip(PAIR_KEYS,key))
        row["marginal_4to8_usd_added_kwh_year"]=float((objective.loc[4]-objective.loc[8])/energy_delta)
        row["added_storage_kwh"]=float(energy_delta)
        row["curtailment_4h_mwh"]=float(d.loc[4,"unused_renewable_mwh"])
        row["curtailment_8h_mwh"]=float(d.loc[8,"unused_renewable_mwh"])
        row["firm_generation_4h_mwh"]=float(d.loc[4,"firm_generation_mwh"])
        row["firm_generation_8h_mwh"]=float(d.loc[8,"firm_generation_mwh"])
        rows.append(row)
    vals=pd.DataFrame(rows)
    if len(vals)!=1080:raise ValueError("Expected 1080 duration-triplet values")
    z=vals.pivot(index=SITING_KEYS,columns="county_weight_scheme",
                 values="marginal_4to8_usd_added_kwh_year")
    if len(z)!=540 or z.isna().any().any() or set(z.columns)!=set(DESIGNS):
        raise ValueError("Missing 540 paired siting design-point contrasts")
    paired=z.reset_index()
    paired["siting_effect_eia_minus_potential"]=(
        paired[DESIGNS[1]]-paired[DESIGNS[0]])
    summary=(paired.groupby(["state","renewable_peak_ratio","wind_share_ac"])
        .agg(weather_years=("weather_year","size"),
             median_siting_effect=("siting_effect_eia_minus_potential","median"),
             mean_siting_effect=("siting_effect_eia_minus_potential","mean"),
             min_siting_effect=("siting_effect_eia_minus_potential","min"),
             max_siting_effect=("siting_effect_eia_minus_potential","max"),
             positive_weather_years=("siting_effect_eia_minus_potential",lambda x:int((x>0).sum())),
             negative_weather_years=("siting_effect_eia_minus_potential",lambda x:int((x<0).sum())))
        .reset_index())
    if len(summary)!=36 or not summary.weather_years.eq(15).all():
        raise ValueError("Missing 36 state×design-point summary cells")
    return vals,paired,summary

def run(wind_h5,pv_h5,wind_sc,pv_sc,county_shares,wind_ref,pv_ref,
        demand_h5,frozen_csv,out):
    frozen=validate_baseline(pd.read_csv(frozen_csv))
    verify_official_file(Path(demand_h5))
    wind,_,tw=reaggregate_years(
        wind_h5,wind_sc,"wind",county_shares,wind_ref,years=WEATHER_YEARS)
    solar,_,tp=reaggregate_years(
        pv_h5,pv_sc,"pv",county_shares,pv_ref,years=WEATHER_YEARS)
    if not tw.equals(tp):raise ValueError("Wind/PV calendar misaligned")
    output=Path(out)
    output.mkdir(parents=True,exist_ok=True)
    new_cases=[]
    with h5py.File(demand_h5,"r") as f:
        g=f["2030"]
        check_fixed_cst_native_labels(g["datetime"][:])
        index=pd.DatetimeIndex(pd.to_datetime(
            [v.decode() if isinstance(v,bytes) else str(v) for v in g["datetime"][:]],utc=True))
        if not index.equals(tw):raise ValueError("Fixed demand vs CF clock mismatch")
        for state in STATES:
            demand=np.asarray(g[state][:],dtype=float)
            if demand.shape!=(HOURS,) or (demand<0).any() or not np.isfinite(demand).all():
                raise ValueError("Invalid state load")
            for year in WEATHER_YEARS:
                for scheme in DESIGNS:
                    w=modeled_hourly_cf(wind[(year,scheme,state)],HOUR)
                    p=normalized_pv_ac_cf(modeled_hourly_cf(solar[(year,scheme,state)],HOUR))
                    for ratio in RATIOS:
                        for wind_share in WIND_SHARES:
                            if ratio==BASE_RATIO and wind_share==BASE_SHARE:
                                continue
                            combined=wind_share*w+(1.-wind_share)*p
                            if not np.isfinite(combined).all() or (combined<0).any() or (combined>1).any():
                                raise ValueError("Invalid shared-AC combined CF")
                            for hours in DURATIONS:
                                sol=solve_zone(demand,combined,hours,
                                   renewable_peak_ratio=ratio,
                                   battery_power_peak_ratio=POWER if hours else 0.,
                                   roundtrip_efficiency=RTE,
                                   renewable_unit_cost=5.,firm_unit_cost=90.)
                                new_cases.append({
                                    "weather_year":year,"state":state,
                                    "county_weight_scheme":scheme,
                                    "renewable_peak_ratio":ratio,"wind_share_ac":wind_share,
                                    "battery_duration_h":hours,**sol})
            # Write safe state-level partial checkpoint to survive CI timeout.
            partial=pd.DataFrame(new_cases)
            partial.to_csv(output/"paper_s_design_grid_new_lp_partial.csv",
                           index=False,float_format="%.12g")
            print("PAPER_S_DESIGN_GRID_STATE_COMPLETED",state,len(partial),flush=True)
    new=pd.DataFrame(new_cases)
    if len(new)!=EXPECTED_NEW or new[KEYS].duplicated().any() or new.solver_status.ne("optimal").any():
        raise ValueError("Expected precisely 2880 new optimal LP cases")
    frozen_common=frozen.drop(columns=["hour_approximation"])
    full=pd.concat([new,frozen_common],ignore_index=True)
    vals,paired,summary=validate_and_summarize(full)
    # Frozen 15-year baseline must reproduce the previously published 60 state-year siting differences.
    base=paired[(paired.renewable_peak_ratio==BASE_RATIO)&
                (paired.wind_share_ac==BASE_SHARE)]
    if len(base)!=60:raise ValueError("Missing full frozen baseline")
    frozen_vals=vals[(vals.renewable_peak_ratio==BASE_RATIO)&
                     (vals.wind_share_ac==BASE_SHARE)]
    if len(frozen_vals)!=120:raise ValueError("Missing baseline duration value pairs")
    for filename,frame in (
        ("paper_s_design_grid_2880_NEW_lp.csv",new),
        ("paper_s_design_grid_1080_duration_values.csv",vals),
        ("paper_s_design_grid_540_paired_siting_effects.csv",paired),
        ("paper_s_design_grid_36_state_grid_summary.csv",summary)):
        frame.to_csv(output/filename,index=False,float_format="%.12g")
    (output/"paper_s_design_grid_new_lp_partial.csv").unlink(missing_ok=True)
    manifest={"status":"PAPER_S_DESIGN_GRID_3X3_COMPLETED_CANDIDATE",
       "new_lp":len(new),"frozen_original_lp_reused":len(frozen_common),
       "total_lp_cells":len(full),"duration_triplets":len(vals),
       "paired_siting_contrasts":len(paired),"state_grid_cells":len(summary),
       "weather_years":list(WEATHER_YEARS),"states":list(STATES),
       "renewable_peak_ratios":list(RATIOS),"wind_shares":list(WIND_SHARES),
       "fixed_reference_demand_model_year":2030,"fixed_reference_weather_year":2012,
       "hour_method":HOUR,"fixed_storage_power_share_of_load_peak":POWER,
       "frozen_original_results_modified":False,"paper_c2_modified":False,
       "observational_validation":False}
    (output/"paper_s_design_grid_manifest.json").write_text(
        json.dumps(manifest,indent=2)+"\n")
    print("PAPER_S_DESIGN_GRID_3X3_2880_NEW_LP_SUCCESS",json.dumps(manifest),flush=True)
    return summary

def main():
    a=argparse.ArgumentParser()
    for name in ("wind_h5","pv_h5","wind_sc","pv_sc","county_shares",
                 "wind_ref","pv_ref","demand_h5","frozen_csv"):
        a.add_argument("--"+name.replace("_","-"),type=Path,required=True)
    a.add_argument("--out",type=Path,required=True)
    p=a.parse_args()
    run(p.wind_h5,p.pv_h5,p.wind_sc,p.pv_sc,p.county_shares,
        p.wind_ref,p.pv_ref,p.demand_h5,p.frozen_csv,p.out)
if __name__=="__main__":
    main()
