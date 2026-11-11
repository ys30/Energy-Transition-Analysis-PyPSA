"""Common AC ReEDS2022 same-source hour approximation sensitivity.

4 states × 3 hypothetical renewable AC-to-peak ratios × 3 AC wind shares ×
2 noncertified hourly approximations × (0,4,8)-h storage = 216 original LPs.
No assumptions about installed fleet, physical intervals, battery CAPEX,
network, or true annual future dispatch. Source 2012 fixed-CST instants.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from energy_transition.efs_cyclic_storage_lp import solve_zone
from energy_transition.reeds2022_joint_resource_shape import STATES,read_native
from energy_transition.reeds2022_county_full_state_lp import HOURS,modeled_hourly_cf,MODES
from energy_transition.reeds2022_county_ac_normalized_2030 import ILR,normalized_pv_ac_cf
from energy_transition.reeds2022_county_storage_mix_duration_2030 import (
    MODEL_YEAR,RATIOS,WIND_MIX,EFFICIENCY,
)
from energy_transition.reeds_2022_clocked_demand_branch import (
    verify_official_file,check_fixed_cst_native_labels
)

DURATIONS=(0,4,8)
BATTERY_POWER_PEAK=.25
FIRM_COST=90.
RENEW_COST=5.
OLD_AC_RUN=43058074434
KEYS=("state","renewable_peak_ratio","wind_share_installed_mw")

def summarize(frame):
    full=[*KEYS,"hour_approximation","battery_duration_h"]
    if len(frame)!=216 or frame.duplicated(full).any():
        raise ValueError("Expected 216 unique source LP rows")
    idx=frame.set_index(full)
    if (frame.solver_status!="optimal").any() or (frame.max_equality_residual_mwh>1e-5).any():
        raise ValueError("Invalid LP convergence or conservation")
    groups=frame.pivot(index=[*KEYS,"hour_approximation"],
        columns="battery_duration_h",
        values=["objective_illustrative_variable_usd","storage_capacity_mwh"])
    if len(groups)!=72 or groups.isna().any().any():
        raise ValueError("Must have 72 complete 0/4/8h triplets")
    pair=groups.reset_index()[[(*[KEYS,"hour_approximation"],)] ] if False else None
    rec=[]
    for key,sub in frame.groupby([*KEYS,"hour_approximation"],sort=True):
        if len(sub)!=3 or set(sub.battery_duration_h)!=set(DURATIONS):
            raise ValueError("Storage durations missing")
        z=sub.set_index("battery_duration_h")
        obj=z.objective_illustrative_variable_usd
        if obj.loc[0]+.10 <obj.loc[4] or obj.loc[4]+.10<obj.loc[8]:
            raise ValueError("Larger battery should not worsen cost optimum")
        delta_kwh=1000*(z.loc[8,"storage_capacity_mwh"]-
                        z.loc[4,"storage_capacity_mwh"])
        if delta_kwh<=0:raise ValueError("Invalid 4→8h incremental energy")
        rec.append(dict(zip([*KEYS,"hour_approximation"],key))|{
            "four_hour_savings_usd":obj.loc[0]-obj.loc[4],
            "eight_hour_savings_usd":obj.loc[0]-obj.loc[8],
            "incremental_4_to_8h_operating_savings_usd":obj.loc[4]-obj.loc[8],
            "incremental_energy_kwh":delta_kwh,
            "incremental_energy_annuity_hurdle_usd_per_kwh_year":(
                obj.loc[4]-obj.loc[8])/delta_kwh})
    paired=pd.DataFrame(rec)
    a=paired.set_index([*KEYS,"hour_approximation"])
    x=a.xs(MODES[0],level="hour_approximation").sort_index()
    y=a.xs(MODES[1],level="hour_approximation").sort_index()
    if len(x)!=36 or len(y)!=36 or not x.index.equals(y.index):
        raise ValueError("Missing 36 exact weather-hour approximation comparisons")
    diff=pd.DataFrame(index=x.index)
    for field in ("four_hour_savings_usd","eight_hour_savings_usd",
                  "incremental_4_to_8h_operating_savings_usd",
                  "incremental_energy_annuity_hurdle_usd_per_kwh_year"):
        diff[field+"_end_instant_hold"]=x[field]
        diff[field+"_trapezoid_first_endpoint"]=y[field]
        diff[field+"_trapezoid_minus_hold"]=y[field]-x[field]
    diff["conditional_10_hurdle_decision_changed"]=(
        (x.incremental_energy_annuity_hurdle_usd_per_kwh_year>=10) !=
        (y.incremental_energy_annuity_hurdle_usd_per_kwh_year>=10))
    return paired,diff.reset_index()

def run(demand_h5,wind_csv,pv_csv,reference_ac_180,out):
    import h5py
    verify_official_file(Path(demand_h5))
    wind,tw=read_native(wind_csv,"wind")
    pv,tp=read_native(pv_csv,"pv")
    if not tw.equals(tp):raise ValueError("Source weather clocks differ")
    rows=[]
    with h5py.File(demand_h5,"r") as f:
        g=f[str(MODEL_YEAR)]
        check_fixed_cst_native_labels(g["datetime"][:])
        labels=pd.DatetimeIndex(pd.to_datetime([
            v.decode() if isinstance(v,bytes) else str(v) for v in g["datetime"][:]],utc=True))
        if not labels.equals(tw):raise ValueError("Demand and weather source time labels differ")
        for state in STATES:
            load=np.asarray(g[state][:],dtype=float)
            if load.shape!=(HOURS,) or not np.isfinite(load).all() or (load<0).any():
                raise ValueError("Invalid source load")
            for mode in MODES:
                w=modeled_hourly_cf(wind[state],mode)
                p=normalized_pv_ac_cf(modeled_hourly_cf(pv[state],mode))
                for ratio in RATIOS:
                    for wind_share in WIND_MIX:
                        cf=wind_share*w+(1-wind_share)*p
                        for duration in DURATIONS:
                            sol=solve_zone(load,cf,duration,
                                renewable_peak_ratio=ratio,
                                battery_power_peak_ratio=BATTERY_POWER_PEAK if duration else 0.,
                                roundtrip_efficiency=EFFICIENCY,
                                renewable_unit_cost=RENEW_COST,firm_unit_cost=FIRM_COST)
                            rows.append({
                                "state":state,"demand_model_year":MODEL_YEAR,
                                "weather_reference_year":2012,
                                "hour_approximation":mode,
                                "first_hour_endpoint_fallback":mode==MODES[1],
                                "renewable_peak_ratio":ratio,
                                "wind_share_installed_mw":wind_share,
                                "battery_duration_h":duration,
                                "battery_power_peak_ratio":BATTERY_POWER_PEAK if duration else 0.,
                                "PV_DC_per_AC_nameplate_ILR":ILR,
                                "common_AC_nameplate":True,
                                "original_source_available_resource_not_installed_fleet":True,
                                "original_hourly_integral_publisher_certified":False,
                                **sol})
    df=pd.DataFrame(rows)
    paired,difference=summarize(df)
    base=pd.read_csv(reference_ac_180)
    target=base[base.battery_power_peak_ratio.eq(BATTERY_POWER_PEAK)]
    ref=target.set_index(["state","renewable_peak_ratio","wind_share_installed_mw","battery_duration_h"])
    now=df[df.hour_approximation.eq(MODES[1])].set_index(
        ["state","renewable_peak_ratio","wind_share_installed_mw","battery_duration_h"])
    ref=ref["objective_illustrative_variable_usd"].sort_index()
    now=now["objective_illustrative_variable_usd"].sort_index()
    if len(ref)!=len(now) or len(ref)!=108 or not ref.index.equals(now.index):
        raise ValueError("Frozen AC original 108-case .25-peak subset does not match")
    maxdiff=float((ref-now).abs().max())
    if maxdiff>.10:raise ValueError(f"Original AC LP benchmark objective drift {maxdiff}")
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    df.to_csv(out/"paper_s_reeds2022_2030_common_ac_216_hour_assumption_LPs.csv",index=False,float_format="%.12g")
    paired.to_csv(out/"paper_s_reeds2022_2030_common_ac_72_hour_storage_pairs.csv",index=False,float_format="%.12g")
    difference.to_csv(out/"paper_s_reeds2022_2030_common_ac_36_hour_assumption_comparisons.csv",index=False,float_format="%.12g")
    m={"status":"PAPER_S_COMMON_AC_216_HOUR_CONVENTION_LP_PASS",
       "source_2012_original_weather_workflow":42962740548,
       "original_180_common_ac_workflow":OLD_AC_RUN,
       "LPs":len(df),"storage_mode_pairs":len(paired),
       "paired_hour_approximation_cases":len(difference),
       "frozen_trapezoid_108_scenario_max_objective_delta_usd":maxdiff,
       "cross_mode_10_usd_annuity_decision_changed_count":int(difference.conditional_10_hurdle_decision_changed.sum()),
       "max_absolute_time_mode_4_to_8_annuity_difference_usd_per_kwh_year":float(
           difference.incremental_energy_annuity_hurdle_usd_per_kwh_year_trapezoid_minus_hold.abs().max()),
       "not_true_hour_integrated_generation":True,
       "source_year_2012_last_day_omitted":True,
       "built_fleet_or_network_validated":False,
       "battery_capital_costs_modeled":False}
    (out/"paper_s_reeds2022_2030_common_ac_216_hour_assumption_manifest.json").write_text(
        json.dumps(m,indent=2)+"\n")
    sel=difference[(difference.renewable_peak_ratio==1.5)&
                   (difference.wind_share_installed_mw==.5)]
    print(sel[["state","incremental_energy_annuity_hurdle_usd_per_kwh_year_end_instant_hold",
               "incremental_energy_annuity_hurdle_usd_per_kwh_year_trapezoid_first_endpoint",
               "conditional_10_hurdle_decision_changed"]].to_string(index=False))
    print(json.dumps(m,indent=2))
    print("PAPER_S_COMMON_AC_216_HOUR_CONVENTION_SOURCE_LP_PASS")
    return df,paired,difference

def main():
    p=argparse.ArgumentParser()
    for x in ("demand_h5","wind_csv","pv_csv","reference_ac_180"):
        p.add_argument("--"+x.replace("_","-"),type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    run(a.demand_h5,a.wind_csv,a.pv_csv,a.reference_ac_180,a.out)

if __name__=="__main__":
    main()
