"""Compare prespecified frozen 720 fixed-load LPs with same-weather 720 LPs.

Do not interpret annual-energy scaling alone as shape-only causal treatment:
the underlying solve_zone sizes renewable and storage POWER from each load PEAK.
Demand-peak differences thus also change installed hypothetical capacities.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

REF_MODE="trapezoid_with_first_endpoint"
SCHEMES=("source_potential_2012","eia_2025_operating_county_weight")
LOAD_MODES=("actual_historical_level","historical_weather_shape_scaled_to_2030_annual_energy")
KEY=("weather_year","state","county_weight_scheme","battery_duration_h")


def compare(fixed,matched):
    required_fixed=set(KEY)|{"hour_approximation","objective_illustrative_variable_usd",
        "demand_mwh","storage_power_mw","storage_capacity_mwh"}
    required_matched=set(KEY)|{"load_mode","objective_illustrative_variable_usd",
        "demand_mwh","storage_power_mw","storage_capacity_mwh"}
    if not required_fixed.issubset(fixed.columns) or not required_matched.issubset(matched.columns):
        raise ValueError("Missing source LP fields needed for paired comparison")
    fixed=fixed[fixed.hour_approximation.eq(REF_MODE)].copy()
    if len(fixed)!=360 or len(matched)!=720:
        raise ValueError("Expected 360 fixed-reference and 720 weather-matched LPs")
    if fixed[list(KEY)].duplicated().any() or matched[list(KEY)+["load_mode"]].duplicated().any():
        raise ValueError("LP scenario key duplication")
    baseline=fixed.set_index(list(KEY))
    out=[]
    for mode in LOAD_MODES:
        group=matched[matched.load_mode.eq(mode)].set_index(list(KEY))
        if len(group)!=360 or not baseline.index.equals(group.index.sort_values()):
            if len(group)!=360 or set(group.index)!=set(baseline.index):
                raise ValueError("Missing matched LP case identities")
        group=group.loc[baseline.index]
        for key,src in baseline.iterrows():
            x=group.loc[key]
            if not np.isfinite(x.objective_illustrative_variable_usd):
                raise ValueError("Non-finite actual historical LP objective")
            out.append({
                **dict(zip(KEY,key)),"load_mode":mode,
                "fixed2030_objective_usd":src.objective_illustrative_variable_usd,
                "historical_mode_objective_usd":x.objective_illustrative_variable_usd,
                "historical_minus_fixed_objective_usd":
                    x.objective_illustrative_variable_usd-src.objective_illustrative_variable_usd,
                "fixed2030_demand_mwh":src.demand_mwh,
                "historical_mode_demand_mwh":x.demand_mwh,
                "fixed2030_storage_power_mw":src.storage_power_mw,
                "historical_mode_storage_power_mw":x.storage_power_mw,
                "fixed2030_storage_energy_mwh":src.storage_capacity_mwh,
                "historical_mode_storage_energy_mwh":x.storage_capacity_mwh,
                "battery_power_retained":np.isclose(
                    src.storage_power_mw,x.storage_power_mw,rtol=1e-9,atol=1e-7),
            })
    scenario=pd.DataFrame(out)
    duration=[]
    for keys,g in scenario.groupby(["weather_year","state","county_weight_scheme","load_mode"],sort=True):
        z=g.set_index("battery_duration_h")
        if set(z.index)!={0,4,8}:raise ValueError("Incomplete 0/4/8 duration triplet")
        a=z.loc[4];b=z.loc[8]
        delta_fixed=(b.fixed2030_storage_energy_mwh-a.fixed2030_storage_energy_mwh)*1000
        delta_other=(b.historical_mode_storage_energy_mwh-a.historical_mode_storage_energy_mwh)*1000
        if delta_fixed<=0 or delta_other<=0:
            raise ValueError("Non-positive duration expansion energy")
        ref_value=(a.fixed2030_objective_usd-b.fixed2030_objective_usd)/delta_fixed
        other_value=(a.historical_mode_objective_usd-b.historical_mode_objective_usd)/delta_other
        duration.append(dict(zip(["weather_year","state","county_weight_scheme","load_mode"],keys),
            fixed2030_marginal_usd_kwh_year=ref_value,
            matched_marginal_usd_kwh_year=other_value,
            matched_minus_fixed_marginal_usd_kwh_year=other_value-ref_value,
            relative_energy_demand=float(a.historical_mode_demand_mwh/a.fixed2030_demand_mwh),
            relative_battery_power=float(a.historical_mode_storage_power_mw/a.fixed2030_storage_power_mw),
            same_total_demand=np.isclose(
                a.historical_mode_demand_mwh,a.fixed2030_demand_mwh,rtol=1e-9)))
    dur=pd.DataFrame(duration)
    if len(scenario)!=720 or len(dur)!=240:
        raise ValueError("Expected 720 LP and 240 duration-pair comparisons")
    geo=[]
    for keys,g in dur.groupby(["weather_year","state","load_mode"],sort=True):
        q=g.set_index("county_weight_scheme")
        if set(q.index)!=set(SCHEMES):raise ValueError("Missing site-weight pair")
        delta_fixed=(q.loc[SCHEMES[1],"fixed2030_marginal_usd_kwh_year"]-
                     q.loc[SCHEMES[0],"fixed2030_marginal_usd_kwh_year"])
        delta_matched=(q.loc[SCHEMES[1],"matched_marginal_usd_kwh_year"]-
                       q.loc[SCHEMES[0],"matched_marginal_usd_kwh_year"])
        geo.append(dict(zip(["weather_year","state","load_mode"],keys),
            fixed2030_siting_effect_usd_kwh_year=delta_fixed,
            matched_siting_effect_usd_kwh_year=delta_matched,
            change_in_siting_effect_usd_kwh_year=delta_matched-delta_fixed,
            same_spatial_effect_direction=bool(np.sign(delta_fixed)==np.sign(delta_matched))))
    spatial=pd.DataFrame(geo)
    if len(spatial)!=120:raise ValueError("Expected 120 matched spatial comparisons")
    return scenario,dur,spatial


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--fixed-720",required=True,type=Path)
    ap.add_argument("--matched-720",required=True,type=Path)
    ap.add_argument("--out",required=True,type=Path)
    args=ap.parse_args()
    full=pd.read_csv(args.fixed_720)
    matched=pd.read_csv(args.matched_720)
    scenarios,triplets,spatial=compare(full,matched)
    args.out.mkdir(parents=True,exist_ok=True)
    for name,data in (("paper_s_load_match_720_objective_comparison.csv",scenarios),
                      ("paper_s_load_match_240_value_comparison.csv",triplets),
                      ("paper_s_load_match_120_geography_comparison.csv",spatial)):
        data.to_csv(args.out/name,index=False,float_format="%.12g")
    m={"status":"PAIRED_LOAD_WEATHER_SOURCE_RESULTS",
       "LP_pairs":len(scenarios),"duration_triplets":len(triplets),
       "geography_comparisons":len(spatial),
       "load_annual_energy_scaling_also_changes_peak_based_installed_power":True,
       "shape_only_causal_effect_established":False,
       "source_same_weather_2030_fleet_projection":False}
    (args.out/"paper_s_load_match_comparison_manifest.json").write_text(json.dumps(m,indent=2)+"\n")
    print("PAPER_S_MATCHED_WEATHER_CROSS_PANEL_COMPARISON_PASS",json.dumps(m))


if __name__=="__main__":
    main()
