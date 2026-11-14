"""Prespecified ReEDS2022 county-native renewable deployment sensitivity.

Three *hypothetical* renewable nameplate ratios (0.9,1.5,2.0 times state
peak load) × four states × three demand years × two source-hour numerical
approximations × 0/4h battery = 144 HiGHS solves. No grid buildout forecast,
hourly-generation certification, network power flow, battery CAPEX, or policy
welfare claim is made.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd

from energy_transition.efs_cyclic_storage_lp import solve_zone
from energy_transition.reeds_2022_clocked_demand_branch import (
    check_fixed_cst_native_labels, verify_official_file,
)
from energy_transition.reeds2022_joint_resource_shape import STATES,read_native
from energy_transition.reeds2022_county_full_state_lp import (
    YEARS,MODES,DURATIONS,WIND_FRACTION,HOURS,modeled_hourly_cf,
)

RATIOS=(0.9,1.5,2.0)
POWER_PEAK_RATIO=0.25
RT_EFFICIENCY=0.9
SOURCE_RUN=42962740548
BASELINE_RUN=42965036275


def paired_summary(results:pd.DataFrame)->pd.DataFrame:
    ids=["state","demand_model_year","hour_approximation","renewable_peak_ratio"]
    no=results.loc[results.battery_duration_h.eq(0)].set_index(ids)
    yes=results.loc[results.battery_duration_h.eq(4)].set_index(ids)
    if len(no)!=72 or len(yes)!=72 or no.index.has_duplicates or yes.index.has_duplicates:
        raise ValueError("Missing or duplicate 0h / 4h cases")
    if set(no.index)!=set(yes.index):raise ValueError("Mismatched pair keys")
    cols=["objective_illustrative_variable_usd","firm_generation_mwh",
          "unused_renewable_mwh","storage_discharge_to_load_mwh",
          "renewable_available_mwh"]
    t=no[cols].add_suffix("_0h").join(yes[cols].add_suffix("_4h"),how="inner")
    t["savings_variable_usd"]=t.objective_illustrative_variable_usd_0h-t.objective_illustrative_variable_usd_4h
    t["savings_pct_0h_cost"]=100*t.savings_variable_usd/t.objective_illustrative_variable_usd_0h
    t["firm_displacement_mwh"]=t.firm_generation_mwh_0h-t.firm_generation_mwh_4h
    t["curtailment_reduction_mwh"]=t.unused_renewable_mwh_0h-t.unused_renewable_mwh_4h
    t["curtailment_rate_without_storage_pct"]=100*t.unused_renewable_mwh_0h/t.renewable_available_mwh_0h
    if (t.savings_variable_usd < -.1).any() or (t.firm_displacement_mwh < -.1).any():
        raise ValueError("LP pair fails storage-feasible monotonicity")
    return t.reset_index().sort_values(ids,kind="stable")


def evaluate(demand_h5,wind_csv,pv_csv,out,*,years=YEARS,states=STATES,
             ratios=RATIOS):
    import h5py
    verify_official_file(Path(demand_h5))
    w,wts=read_native(wind_csv,"wind")
    p,pts=read_native(pv_csv,"pv")
    if not wts.equals(pts):raise ValueError("Publisher wind and PV source instants differ")
    if tuple(ratios)!=RATIOS:raise ValueError("Prespecified three-ratio experiment changed")
    rows=[]
    with h5py.File(demand_h5,"r") as f:
        for year in years:
            g=f[str(year)]
            check_fixed_cst_native_labels(g["datetime"][:])
            native=pd.DatetimeIndex(pd.to_datetime([
                a.decode() if isinstance(a,bytes) else str(a) for a in g["datetime"][:]
            ],utc=True))
            if not native.equals(wts):raise ValueError("Authenticated native timestamps mismatch")
            for state in states:
                load=np.asarray(g[state][:],dtype=np.float64)
                if load.shape!=(HOURS,) or not np.isfinite(load).all() or (load<0).any():
                    raise ValueError("Invalid original demand")
                for mode in MODES:
                    wf=modeled_hourly_cf(w[state],mode)
                    pf=modeled_hourly_cf(p[state],mode)
                    cf=WIND_FRACTION*wf+(1-WIND_FRACTION)*pf
                    for ratio in ratios:
                        if not np.isfinite(ratio) or ratio<=0:raise ValueError("Invalid scenario ratio")
                        for duration in DURATIONS:
                            opt=solve_zone(load,cf,duration,
                                 renewable_peak_ratio=ratio,
                                 battery_power_peak_ratio=POWER_PEAK_RATIO,
                                 roundtrip_efficiency=RT_EFFICIENCY)
                            rows.append({
                               "experiment":"county-native-real-weather-hypothetical-capacity-ratio-sweep",
                               "state":state,"demand_model_year":year,
                               "reference_weather_year":2012,
                               "hour_approximation":mode,
                               "first_hour_trapezoid_endpoint_fallback":mode==MODES[1],
                               "renewable_peak_ratio":float(ratio),
                               "hypothetical_wind_fraction":WIND_FRACTION,
                               "battery_duration_h":duration,
                               "storage_power_peak_ratio":POWER_PEAK_RATIO,
                               "source_cf_weather_authenticated":True,
                               "hourly_generation_energy_publisher_certified":False,
                               "built_capacity_calibrated":False,
                               "resource_potential_is_not_installed_MW":True,
                               "network_or_reliability_certified":False,
                               **opt})
    df=pd.DataFrame(rows)
    if len(df)!=len(states)*len(years)*len(MODES)*len(RATIOS)*len(DURATIONS):
        raise ValueError("Expected 144 LP cases")
    if not df.solver_status.eq("optimal").all() or df.max_equality_residual_mwh.max()>1e-5:
        raise ValueError("One or more storage LP solves failed")
    pairs=paired_summary(df)
    out=Path(out)
    out.mkdir(parents=True,exist_ok=True)
    df.to_csv(out/"paper_s_reeds2022_county_native_144_ratio_LP.csv",
              index=False,float_format="%.12g")
    pairs.to_csv(out/"paper_s_reeds2022_county_native_72_ratio_paired.csv",
                 index=False,float_format="%.12g")
    manifest={"status":"ORIGINAL_SOURCE_2012_REFERENCE_METEOROLOGY_144_RATIO_LP_PASS",
      "original_source_cf_workflow":SOURCE_RUN,
      "original_source_demand_md5":"7b2055d43200744a16a8c4fed68b1a17",
      "baseline_0p9_ratio_lp_run":BASELINE_RUN,
      "LP_count":len(df),"paired_0h_4h_count":len(pairs),
      "scenario_renewable_to_peak_nameplate_ratios":list(RATIOS),
      "states":list(states),"model_years":list(years),
      "weather_year":2012,
      "wind_pv_capacity_mix":"hypothetical 50/50 MW",
      "battery_power_to_peak":POWER_PEAK_RATIO,
      "battery_duration_options_h":list(DURATIONS),
      "hourly_CF_to_energy_is_assumed_not_publisher_certified":True,
      "first_hour_trapezoid_uses_endpoint_no_cyclic_wrap":True,
      "storage_capex_included":False,"real_network_or_reliability_estimate":False,
      "old_EFS2020_results_modified":False}
    (out/"paper_s_reeds2022_county_native_ratio_sweep_manifest.json").write_text(
         json.dumps(manifest,indent=2)+"\n")
    print(pairs.loc[(pairs.demand_model_year==2030)&
                    pairs.hour_approximation.eq(MODES[1]),
                    ["state","renewable_peak_ratio","savings_variable_usd",
                     "savings_pct_0h_cost","curtailment_rate_without_storage_pct"]]
          .to_string(index=False,float_format=lambda x:f"{x:.6f}"))
    print("SOURCE_AUTHENTICATED_144_RATIO_SWEEP_SOLVES_AND_72_PAIRS_PASS")
    return df,pairs


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--demand-h5",type=Path,required=True)
    parser.add_argument("--wind-csv",type=Path,required=True)
    parser.add_argument("--pv-csv",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    evaluate(args.demand_h5,args.wind_csv,args.pv_csv,args.out)


if __name__=="__main__":
    main()
