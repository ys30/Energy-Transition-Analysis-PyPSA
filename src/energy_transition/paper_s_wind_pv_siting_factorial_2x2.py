"""Paper S: exact wind-weight × PV-weight 2×2 mechanism ablation.

Standalone observational siting-weight intervention; NOT climate attribution.
Only 360 NEW HiGHS cases (wind-only, PV-only × 60 state-years × 3 durations).
Frozen original baseline and joint-weight 360 LP cases are read, not changed.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import h5py
import numpy as np
import pandas as pd
from energy_transition.reeds2022_all_weather_year_720lp import WEATHER_YEARS
from energy_transition.reeds2022_four_weather_year_siting_lp import (
    reaggregate_years,STATES,DESIGNS,DURATIONS,RATIO,WIND_SHARE,POWER,RTE,HOURS,
)
from energy_transition.reeds2022_county_full_state_lp import modeled_hourly_cf
from energy_transition.reeds2022_county_ac_normalized_2030 import normalized_pv_ac_cf
from energy_transition.reeds_2022_clocked_demand_branch import (
    verify_official_file,check_fixed_cst_native_labels,
)
from energy_transition.efs_cyclic_storage_lp import solve_zone

BASE="potential_potential"
WIND="eia_wind_only"
SOLAR="eia_pv_only"
JOINT="eia_wind_eia_pv"
HOUR="trapezoid_with_first_endpoint"
EXPECTED_NEW=15*4*2*3

def validate_frozen(frozen):
    keys=["weather_year","state","county_weight_scheme","hour_approximation","battery_duration_h"]
    assert_keys=set(keys+["objective_illustrative_variable_usd","storage_capacity_mwh",
                          "unused_renewable_mwh","solver_status"])
    if not assert_keys.issubset(frozen.columns):
        raise ValueError("Frozen original LP schema incomplete")
    z=frozen[frozen.hour_approximation.eq(HOUR)].copy()
    if len(z)!=360 or z[keys].duplicated().any() or not z.solver_status.eq("optimal").all():
        raise ValueError("Expected 360 original frozen trapezoid LP rows")
    expected=pd.MultiIndex.from_product([WEATHER_YEARS,STATES,DESIGNS,DURATIONS],names=[
        "weather_year","state","county_weight_scheme","battery_duration_h"])
    actual=pd.MultiIndex.from_frame(z[expected.names])
    if len(expected.difference(actual)) or len(actual.difference(expected)):
        raise ValueError("Frozen original LP case coverage drift")
    z["factorial_arm"]=np.where(z.county_weight_scheme.eq(DESIGNS[0]),BASE,JOINT)
    return z

def value_from_durations(lp):
    keys=["weather_year","state","factorial_arm"]
    if lp[keys+["battery_duration_h"]].duplicated().any():raise ValueError("Duplicate LP duration")
    out=[]
    for key,g in lp.groupby(keys,sort=True):
        d=g.set_index("battery_duration_h")
        if set(d.index)!=set(DURATIONS) or not d.solver_status.eq("optimal").all():
            raise ValueError("Missing/nonoptimal factorial duration")
        denom=(d.loc[8,"storage_capacity_mwh"]-d.loc[4,"storage_capacity_mwh"])*1000.
        if denom<=0:raise ValueError("Nonpositive added storage capacity")
        v=(d.loc[4,"objective_illustrative_variable_usd"]-
           d.loc[8,"objective_illustrative_variable_usd"])/denom
        out.append(dict(zip(keys,key),marginal_4to8_usd_kwh_year=float(v),
            delta_curtailment_8minus4_mwh=float(
                d.loc[8,"unused_renewable_mwh"]-d.loc[4,"unused_renewable_mwh"])))
    return pd.DataFrame(out)

def attribute(values):
    keys=["weather_year","state"]
    z=values.pivot(index=keys,columns="factorial_arm",values="marginal_4to8_usd_kwh_year")
    if len(z)!=60 or z.isna().any().any() or set(z.columns)!={BASE,WIND,SOLAR,JOINT}:
        raise ValueError("Incomplete 60 quartet factorial")
    a,b,c,d=(z[x] for x in (BASE,WIND,SOLAR,JOINT))
    result=pd.DataFrame({
        "weather_year":z.index.get_level_values(0),
        "state":z.index.get_level_values(1),
        "V_base":a.to_numpy(),"V_wind_only":b.to_numpy(),
        "V_pv_only":c.to_numpy(),"V_joint":d.to_numpy(),
        "total_eia_minus_potential":(d-a).to_numpy(),
        "wind_alone":(b-a).to_numpy(),"pv_alone":(c-a).to_numpy(),
        "wind_pv_interaction":(d-b-c+a).to_numpy(),
        "wind_shapley":(.5*((b-a)+(d-c))).to_numpy(),
        "pv_shapley":(.5*((c-a)+(d-b))).to_numpy()
    })
    if not np.allclose(result.wind_shapley+result.pv_shapley,
                       result.total_eia_minus_potential,atol=1e-9,rtol=0):
        raise ValueError("Shapley conservation failure")
    if not np.allclose(result.wind_alone+result.pv_alone+result.wind_pv_interaction,
                       result.total_eia_minus_potential,atol=1e-9,rtol=0):
        raise ValueError("Factorial interaction conservation failure")
    return result

def shape_stats(load,wind,pv):
    if any(np.shape(x)!=(HOURS,) for x in (load,wind,pv)):raise ValueError("Wrong common hour length")
    if np.max(load)<=0:raise ValueError("Invalid load peak")
    available=RATIO*np.max(load)*(WIND_SHARE*wind+(1-WIND_SHARE)*pv)
    net=load-available
    daily=net.reshape(-1,24)
    shift24=lambda x:float(np.corrcoef(x[:-24],x[24:])[0,1]) if np.std(x)>0 else float("nan")
    return {
        "wind_cf_mean":float(np.mean(wind)),
        "pv_cf_mean":float(np.mean(pv)),
        "combined_cf_variance":float(np.var(WIND_SHARE*wind+(1-WIND_SHARE)*pv)),
        "combined_cf_lag24_corr":shift24(WIND_SHARE*wind+(1-WIND_SHARE)*pv),
        "mean_daily_netload_peak_to_trough_mw":float(np.mean(np.ptp(daily,axis=1))),
        "netload_std_mw":float(np.std(net)),
        "netload_annual_max_mw":float(np.max(net)),
        "netload_lag24_corr":shift24(net),
        "pre_dispatch_surplus_mwh":float(np.maximum(-net,0).sum()),
        "pre_dispatch_deficit_mwh":float(np.maximum(net,0).sum()),
    }

def run(wind_h5,pv_h5,wind_sc,pv_sc,county_shares,wind_ref,pv_ref,demand_h5,frozen_csv,out):
    frozen=validate_frozen(pd.read_csv(frozen_csv))
    verify_official_file(Path(demand_h5))
    winds,_,tw=reaggregate_years(wind_h5,wind_sc,"wind",county_shares,wind_ref,years=WEATHER_YEARS)
    pvs,_,tp=reaggregate_years(pv_h5,pv_sc,"pv",county_shares,pv_ref,years=WEATHER_YEARS)
    if not tw.equals(tp):raise ValueError("Source wind and PV source-clock mismatch")
    rows=[];metrics=[]
    with h5py.File(demand_h5,"r") as f:
        obj=f["2030"]
        check_fixed_cst_native_labels(obj["datetime"][:])
        clock=pd.DatetimeIndex(pd.to_datetime(
            [x.decode() if isinstance(x,bytes) else str(x) for x in obj["datetime"][:]],utc=True))
        if not clock.equals(tw):raise ValueError("Demand versus wind/PV clock mismatch")
        for st in STATES:
            load=np.asarray(obj[st][:],dtype=float)
            if load.shape!=(HOURS,) or not np.isfinite(load).all():raise ValueError("Invalid 2030 load")
            for year in WEATHER_YEARS:
                for arm,w_scheme,p_scheme in (
                    (BASE,DESIGNS[0],DESIGNS[0]),
                    (WIND,DESIGNS[1],DESIGNS[0]),
                    (SOLAR,DESIGNS[0],DESIGNS[1]),
                    (JOINT,DESIGNS[1],DESIGNS[1]),
                ):
                    w=modeled_hourly_cf(winds[(year,w_scheme,st)],HOUR)
                    p=normalized_pv_ac_cf(modeled_hourly_cf(pvs[(year,p_scheme,st)],HOUR))
                    metrics.append(dict(weather_year=year,state=st,factorial_arm=arm,
                                        **shape_stats(load,w,p)))
                    if arm in (BASE,JOINT):continue
                    mixed=WIND_SHARE*w+(1-WIND_SHARE)*p
                    for duration in DURATIONS:
                        sol=solve_zone(load,mixed,duration,renewable_peak_ratio=RATIO,
                            battery_power_peak_ratio=POWER if duration else 0.,
                            roundtrip_efficiency=RTE,renewable_unit_cost=5.,firm_unit_cost=90.)
                        rows.append(dict(weather_year=year,state=st,factorial_arm=arm,
                                         battery_duration_h=duration,**sol))
    news=pd.DataFrame(rows)
    if len(news)!=EXPECTED_NEW or not news.solver_status.eq("optimal").all():
        raise ValueError("Expected exactly 360 optimal new LP cases")
    original=frozen.drop(columns=["county_weight_scheme","hour_approximation"])
    full=pd.concat([original,news],ignore_index=True)
    values=value_from_durations(full)
    decomposition=attribute(values)
    shapes=pd.DataFrame(metrics)
    if len(shapes)!=240:raise ValueError("Incomplete four-arm annual shape metrics")
    # Compare all 120 original baseline/joint 4→8h values before admitting new results.
    original_vals=value_from_durations(original)
    new_vals=values[values.factorial_arm.isin((BASE,JOINT))]
    m=original_vals.merge(new_vals,on=["weather_year","state","factorial_arm"],validate="one_to_one",
                          suffixes=("_original","_joined"))
    if len(m)!=120 or not np.allclose(m.marginal_4to8_usd_kwh_year_original,
                                     m.marginal_4to8_usd_kwh_year_joined,atol=1e-9,rtol=0):
        raise ValueError("Frozen LP values mutated")
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    for name,df in (
        ("paper_s_siting_factorial_360_NEW_lp.csv",news),
        ("paper_s_siting_factorial_240_four_arm_duration_values.csv",values),
        ("paper_s_siting_factorial_60_shapley_interaction.csv",decomposition),
        ("paper_s_siting_factorial_240_hourly_curve_descriptives.csv",shapes)):
        df.to_csv(out/name,index=False,float_format="%.12g")
    manifest=dict(status="NEW_SITING_FACTORIAL_2x2_CANDIDATE_ONLY",
        weather_years=list(WEATHER_YEARS),states=list(STATES),new_lp=int(len(news)),
        frozen_lp_reused=360,all_four_arm_duration_values=int(len(values)),
        paired_factorial_rows=int(len(decomposition)),descriptive_rows=len(shapes),
        fixed_2030_2012_weather_demand=True,actual_2025_siting_not_future_fleet=True,
        hour_mode=HOUR,design_point_R=RATIO,design_point_wind_share=WIND_SHARE,
        frozen_original_outputs_modified=False,climate_attribution=False,
        observed_EIA930_validation=False)
    (out/"paper_s_siting_factorial_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("PAPER_S_2X2_SITING_ATTRIBUTION_PASS",json.dumps(manifest))
    return decomposition

def main():
    p=argparse.ArgumentParser()
    for name in ("wind_h5","pv_h5","wind_sc","pv_sc","county_shares","wind_ref","pv_ref",
                 "demand_h5","frozen_csv"):
        p.add_argument("--"+name.replace("_","-"),required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    run(a.wind_h5,a.pv_h5,a.wind_sc,a.pv_sc,a.county_shares,a.wind_ref,a.pv_ref,
        a.demand_h5,a.frozen_csv,a.out)
if __name__=="__main__":main()
