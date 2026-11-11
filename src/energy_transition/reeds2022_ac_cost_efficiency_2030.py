"""Paper S ReEDS2022 common-AC reference-year operating cost and efficiency sweep.

Independent source-backed HiGHS LP solves, not a financial valuation.
2026 manuscript admission experiment: four states, reference 2030 demand,
2012 original resource weather, common AC nameplate, r=1.5, wind share .5,
battery power .25 peak, durations 0/4/8 h, 3 roundtrip efficiencies,
3 illustrative firm marginal generation costs. 108 total LP solves.
No storage capital, degradation, network or certified interval energy.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from energy_transition.efs_cyclic_storage_lp import solve_zone
from energy_transition.reeds2022_county_ac_normalized_2030 import (
    normalized_pv_ac_cf,ILR,
)
from energy_transition.reeds2022_county_full_state_lp import modeled_hourly_cf,HOURS
from energy_transition.reeds2022_joint_resource_shape import STATES,read_native
from energy_transition.reeds_2022_clocked_demand_branch import (
    verify_official_file,check_fixed_cst_native_labels,
)

YEAR=2030
WEATHER_YEAR=2012
RENEWABLE_PEAK_RATIO=1.5
WIND_SHARE_AC=.5
STORAGE_POWER_PEAK_RATIO=.25
DURATIONS=(0,4,8)
ROUNDTRIP_EFFICIENCIES=(.80,.90,.95)
FIRM_COST_USD_PER_MWH=(60.,90.,120.)
RENEWABLE_COST_USD_PER_MWH=5.
SOURCE_REFERENCE_AC_LP_RUN=43058074434

def pairs(solutions):
    scope=["state","demand_model_year","roundtrip_efficiency",
           "firm_cost_usd_per_mwh"]
    if len(solutions)!=len(STATES)*len(ROUNDTRIP_EFFICIENCIES)*len(FIRM_COST_USD_PER_MWH)*len(DURATIONS):
        raise ValueError("Missing prespecified 108-case solver experiment")
    if solutions.duplicated(scope+["battery_duration_h"]).any():
        raise ValueError("Duplicate source LP design cells")
    frames={d:solutions[solutions.battery_duration_h.eq(d)].set_index(scope).sort_index()
            for d in DURATIONS}
    if any(len(v)!=36 for v in frames.values()) or any(
            not frames[0].index.equals(frames[d].index) for d in (4,8)):
        raise ValueError("Not exactly 36 0/4/8 storage matches")
    a,b,c=frames[0],frames[4],frames[8]
    out=pd.DataFrame(index=a.index)
    out["no_storage_operating_objective_usd"]=a.objective_illustrative_variable_usd
    out["four_hour_operating_objective_usd"]=b.objective_illustrative_variable_usd
    out["eight_hour_operating_objective_usd"]=c.objective_illustrative_variable_usd
    out["four_hour_storage_savings_usd"]=(
        a.objective_illustrative_variable_usd-b.objective_illustrative_variable_usd)
    out["eight_hour_storage_savings_usd"]=(
        a.objective_illustrative_variable_usd-c.objective_illustrative_variable_usd)
    out["incremental_4_to_8_hour_savings_usd"]=(
        b.objective_illustrative_variable_usd-c.objective_illustrative_variable_usd)
    out["battery_power_mw"]=b.storage_power_mw
    out["extra_4_to_8_hour_energy_kwh"]=(
        c.storage_capacity_mwh-b.storage_capacity_mwh)*1000.
    out["incremental_energy_annuity_hurdle_usd_per_kwh_year"]=(
        out.incremental_4_to_8_hour_savings_usd/out.extra_4_to_8_hour_energy_kwh)
    out["above_hypothetical_10usd_per_kwh_year_energy_cost_only"]=(
        out.incremental_energy_annuity_hurdle_usd_per_kwh_year>=10.)
    if (out.incremental_4_to_8_hour_savings_usd<-.10).any() or (
            out.extra_4_to_8_hour_energy_kwh<=0).any():
        raise ValueError("8h LP must weakly dominate 4h and add energy capacity")
    if not np.allclose(b.storage_power_mw,c.storage_power_mw,rtol=0,atol=1e-8):
        raise ValueError("4h and 8h comparisons must hold power fixed")
    # 0h dispatch cannot depend on eta because it contains no storage.
    for (state,cost),group in out.reset_index().groupby(["state","firm_cost_usd_per_mwh"]):
        if np.ptp(group.no_storage_operating_objective_usd.to_numpy())>.05:
            raise ValueError("Zero-storage optimum depends on round-trip efficiency")
    return out.reset_index().sort_values(scope)

def run(demand_h5,wind_csv,pv_csv,out):
    import h5py
    verify_official_file(Path(demand_h5))
    wind,t_w=read_native(wind_csv,"wind")
    pv,t_p=read_native(pv_csv,"pv")
    if not t_w.equals(t_p):raise ValueError("Weather source clocks differ")
    rows=[]
    with h5py.File(demand_h5,"r") as f:
        group=f[str(YEAR)]
        check_fixed_cst_native_labels(group["datetime"][:])
        times=pd.DatetimeIndex(pd.to_datetime(
            [v.decode() if isinstance(v,bytes) else str(v) for v in group["datetime"][:]],utc=True))
        if not times.equals(t_w):raise ValueError("ReEDS weather and demand native timestamps differ")
        for state in STATES:
            load=np.asarray(group[state][:],dtype=np.float64)
            if load.shape!=(HOURS,) or not np.isfinite(load).all() or (load<0).any():
                raise ValueError("Original source demand invalid")
            peak=float(load.max())
            wc=modeled_hourly_cf(wind[state],"trapezoid_with_first_endpoint")
            pc=normalized_pv_ac_cf(
                modeled_hourly_cf(pv[state],"trapezoid_with_first_endpoint"))
            cf=WIND_SHARE_AC*wc+(1-WIND_SHARE_AC)*pc
            for eta in ROUNDTRIP_EFFICIENCIES:
                for cost in FIRM_COST_USD_PER_MWH:
                    for duration in DURATIONS:
                        result=solve_zone(load,cf,duration,
                            renewable_peak_ratio=RENEWABLE_PEAK_RATIO,
                            battery_power_peak_ratio=STORAGE_POWER_PEAK_RATIO if duration else 0.,
                            roundtrip_efficiency=eta,
                            renewable_unit_cost=RENEWABLE_COST_USD_PER_MWH,
                            firm_unit_cost=cost)
                        rows.append({
                            "state":state,"demand_model_year":YEAR,
                            "source_reference_weather_year":WEATHER_YEAR,
                            "scenario_nameplate_basis":"common_AC_nameplate",
                            "hypothetical_renewable_ac_to_load_peak":RENEWABLE_PEAK_RATIO,
                            "hypothetical_wind_share_ac":WIND_SHARE_AC,
                            "pv_source_ILR":ILR,
                            "roundtrip_efficiency":eta,
                            "renewable_cost_usd_per_mwh":RENEWABLE_COST_USD_PER_MWH,
                            "firm_cost_usd_per_mwh":cost,
                            "battery_duration_h":duration,
                            "battery_power_to_load_peak":STORAGE_POWER_PEAK_RATIO if duration else 0.,
                            "actual_installed_fleet_known":False,
                            "hourly_energy_certified_by_publisher":False,
                            "battery_capex_in_objective":False,
                            **result,
                        })
    df=pd.DataFrame(rows)
    if not df.solver_status.eq("optimal").all() or df.max_equality_residual_mwh.max()>1e-5:
        raise ValueError("Unaccepted optimization solution or mass balance")
    paired=pairs(df)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    df.to_csv(out/"paper_s_reeds2022_2030_common_ac_108_efficiency_firm_cost_lp.csv",
              index=False,float_format="%.12g")
    paired.to_csv(out/"paper_s_reeds2022_2030_common_ac_36_efficiency_firm_cost_4_to_8h.csv",
                  index=False,float_format="%.12g")
    anchor=paired[(paired.state.eq("AZ"))&(paired.roundtrip_efficiency.eq(.9))&
                  (paired.firm_cost_usd_per_mwh.eq(90))]
    if len(anchor)!=1 or abs(float(anchor.incremental_energy_annuity_hurdle_usd_per_kwh_year.iloc[0])-10.955400)>.001:
        raise ValueError("Original source common-AC Arizona marginal 4→8h result not reproduced")
    manifest={
        "status":"REEDS2022_AC_108_LP_EFFICIENCY_FIRM_COST_SENSITIVITY_PASSED",
        "source_original_weather_artifact_run":42962740548,
        "common_AC_original_180_lp_run":SOURCE_REFERENCE_AC_LP_RUN,
        "demand_year":YEAR,"weather_year":WEATHER_YEAR,
        "LP_count":len(df),"paired_0_4_8_comparisons":len(paired),
        "roundtrip_efficiency_grid":ROUNDTRIP_EFFICIENCIES,
        "firm_unit_cost_grid_usd_mwh":FIRM_COST_USD_PER_MWH,
        "PV_ILR":ILR,
        "common_AC_capacity_bases":True,
        "battery_capex_in_optimization":False,
        "illustrative_annualized_energy_cost_test_usd_kwh_year":10,
        "actual_fleet_and_market_cost_calibration":False,
        "hourly_source_interval_generation_certified":False,
        "network_and_reliability_certified":False}
    (out/"paper_s_reeds2022_2030_common_ac_108_cost_eta_manifest.json").write_text(
        json.dumps(manifest,indent=2)+"\n")
    print(paired[["state","roundtrip_efficiency","firm_cost_usd_per_mwh",
                  "incremental_energy_annuity_hurdle_usd_per_kwh_year",
                  "above_hypothetical_10usd_per_kwh_year_energy_cost_only"]].to_string(index=False))
    print("REEDS2022_AC_108_LP_36_PAIRED_COST_EFFICIENCY_SENSITIVITY_PASS")
    return df,paired

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--demand-h5",type=Path,required=True)
    p.add_argument("--wind-csv",type=Path,required=True)
    p.add_argument("--pv-csv",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    run(a.demand_h5,a.wind_csv,a.pv_csv,a.out)

if __name__=="__main__":
    main()
