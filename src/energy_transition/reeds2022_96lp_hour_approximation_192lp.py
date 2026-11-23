"""Paired source 2010–2013 original HDF5 192-LP hourly-CF integration sensitivity.

Two same 96-design panels: end_instant_hold vs trapezoid_with_first_endpoint.
Not authentic hour-integrated output; these are two prespecified approximations.
The frozen 96 trapezoid cases MUST exactly replicate the prior source LPs.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import h5py
import numpy as np
import pandas as pd
from energy_transition.reeds2022_four_weather_year_siting_lp import (
    YEARS,STATES,DESIGNS,DURATIONS,RATIO,WIND_SHARE,POWER,RTE,ILR,
    reaggregate_years,summarize,HOURS
)
from energy_transition.reeds2022_county_full_state_lp import modeled_hourly_cf
from energy_transition.reeds2022_county_ac_normalized_2030 import normalized_pv_ac_cf
from energy_transition.reeds_2022_clocked_demand_branch import (
    verify_official_file,check_fixed_cst_native_labels
)
from energy_transition.efs_cyclic_storage_lp import solve_zone
MODES=("end_instant_hold","trapezoid_with_first_endpoint")
BASE_RUN=43281182390

def summarize_modes(lps):
    if len(lps)!=192 or set(lps.hour_approximation)!=set(MODES):
        raise ValueError("Exactly 2 original-source 96-LP modes required")
    grouped=[]
    maps=[]
    for mode in MODES:
        part=lps[lps.hour_approximation.eq(mode)].copy()
        if len(part)!=96:raise ValueError("Incomplete hour-mode panel")
        p,d=summarize(part)
        p.insert(0,"hour_approximation",mode)
        d.insert(0,"hour_approximation",mode)
        grouped.append(p);maps.append(d)
    pairs=pd.concat(grouped,ignore_index=True)
    geography=pd.concat(maps,ignore_index=True)
    idx=["weather_year","state","county_weight_scheme","battery_duration_h"]
    a=lps[lps.hour_approximation.eq(MODES[0])].set_index(idx).sort_index()
    b=lps[lps.hour_approximation.eq(MODES[1])].set_index(idx).sort_index()
    if not a.index.equals(b.index) or len(a)!=96:raise ValueError("Unpaired 96 cases")
    compare=a[["objective_illustrative_variable_usd"]].rename(
        columns={"objective_illustrative_variable_usd":"objective_hold_usd"})
    compare["objective_trapezoid_usd"]=b.objective_illustrative_variable_usd
    compare["objective_hold_minus_trapezoid_usd"]=compare.objective_hold_usd-compare.objective_trapezoid_usd
    ref=["weather_year","state","county_weight_scheme"]
    pa=pairs[pairs.hour_approximation.eq(MODES[0])].set_index(ref).sort_index()
    pb=pairs[pairs.hour_approximation.eq(MODES[1])].set_index(ref).sort_index()
    if len(pa)!=32 or not pa.index.equals(pb.index):raise ValueError("Incomplete hour-mode value pairing")
    annuity=pd.DataFrame(index=pa.index)
    annuity["energy_annuity_usd_kwh_year_hold"]=pa.energy_annuity_hurdle_usd_kwh_year
    annuity["energy_annuity_usd_kwh_year_trapezoid"]=pb.energy_annuity_hurdle_usd_kwh_year
    annuity["annuity_hold_minus_trapezoid"]=(
        annuity.energy_annuity_usd_kwh_year_hold-annuity.energy_annuity_usd_kwh_year_trapezoid)
    annuity["10usd_screen_hold"]=annuity.energy_annuity_usd_kwh_year_hold>=10
    annuity["10usd_screen_trapezoid"]=annuity.energy_annuity_usd_kwh_year_trapezoid>=10
    annuity["10usd_screen_hour_approximation_flip"]=annuity["10usd_screen_hold"]!=annuity["10usd_screen_trapezoid"]
    ga=geography[geography.hour_approximation.eq(MODES[0])].set_index(["weather_year","state"]).sort_index()
    gb=geography[geography.hour_approximation.eq(MODES[1])].set_index(["weather_year","state"]).sort_index()
    if len(ga)!=16 or not ga.index.equals(gb.index):raise ValueError("Unpaired geographic comparisons")
    compare_geo=pd.DataFrame(index=ga.index)
    for label,grp in (("hold",ga),("trapezoid",gb)):
        compare_geo[f"spatial_EIA_minus_potential_{label}_usd_kwh_year"]=grp[
            "energy_annuity_hurdle_usd_kwh_year_EIA_minus_potential"]
        compare_geo[f"spatial_10usd_screen_flip_{label}"]=grp[
            "spatial_weight_10usd_screen_flips"]
    compare_geo["siting_delta_sign_preserved"]=(
        np.sign(compare_geo.spatial_EIA_minus_potential_hold_usd_kwh_year)==
        np.sign(compare_geo.spatial_EIA_minus_potential_trapezoid_usd_kwh_year))
    compare_geo["siting_10usd_screen_status_agrees"]=(
        compare_geo.spatial_10usd_screen_flip_hold==
        compare_geo.spatial_10usd_screen_flip_trapezoid)
    return pairs,geography,compare.reset_index(),annuity.reset_index(),compare_geo.reset_index()

def run(wind_h5,pv_h5,wind_sc,pv_sc,county_shares,wind_ref,pv_ref,demand_h5,original_96_lps,out):
    verify_official_file(Path(demand_h5))
    w,wa,tw=reaggregate_years(wind_h5,wind_sc,"wind",county_shares,wind_ref)
    p,pa,tp=reaggregate_years(pv_h5,pv_sc,"pv",county_shares,pv_ref)
    if not tw.equals(tp):raise ValueError("Wind/PV original source clocks mismatch")
    rows=[]
    with h5py.File(demand_h5,"r") as source:
        d=source["2030"]
        check_fixed_cst_native_labels(d["datetime"][:])
        clock=pd.DatetimeIndex(pd.to_datetime(
            [x.decode() if isinstance(x,bytes) else str(x) for x in d["datetime"][:]],utc=True))
        if not clock.equals(tw):raise ValueError("Original demand and 2012 source clock mismatch")
        for st in STATES:
            load=np.asarray(d[st][:],dtype=float)
            if load.shape!=(HOURS,) or not np.isfinite(load).all() or (load<0).any():
                raise ValueError("Invalid source 2030 load")
            for year in YEARS:
                for scheme in DESIGNS:
                    for mode in MODES:
                        wind=modeled_hourly_cf(w[(year,scheme,st)],mode)
                        pv=normalized_pv_ac_cf(modeled_hourly_cf(p[(year,scheme,st)],mode))
                        mix=WIND_SHARE*wind+(1-WIND_SHARE)*pv
                        for duration in DURATIONS:
                            result=solve_zone(load,mix,duration,renewable_peak_ratio=RATIO,
                              battery_power_peak_ratio=POWER if duration else 0.,
                              roundtrip_efficiency=RTE,renewable_unit_cost=5.,firm_unit_cost=90.)
                            rows.append({
                              "weather_year":year,"state":st,"county_weight_scheme":scheme,
                              "hour_approximation":mode,"battery_duration_h":duration,
                              "reference_demand_year":2030,
                              "site_weight_source_year":2025,
                              "original_source_weather_year":year,
                              "source_weather_CF_is_instantaneous":True,
                              "true_hour_energy_integral_certified":False,
                              "physical_2030_generation_forecast":False,
                              "nonleap_Feb29_synthetic":year!=2012,
                              "renewable_AC_peak_ratio":RATIO,"wind_AC_fraction":WIND_SHARE,
                              "pv_DC_to_AC_ILR":ILR,
                              **result})
    all_lp=pd.DataFrame(rows)
    if len(all_lp)!=192 or not all_lp.solver_status.eq("optimal").all() or (
        all_lp.max_equality_residual_mwh.max()>1e-5):
        raise ValueError("192 paired source LPs failed feasibility")
    frozen=pd.read_csv(original_96_lps)
    idx=["weather_year","state","county_weight_scheme","battery_duration_h"]
    original=frozen.set_index(idx).objective_illustrative_variable_usd.sort_index()
    current=all_lp[all_lp.hour_approximation.eq(MODES[1])].set_index(
        idx).objective_illustrative_variable_usd.sort_index()
    if len(original)!=96 or len(current)!=96 or not original.index.equals(current.index):
        raise ValueError("Original 96-LP case identities are not replicated")
    maximum=float(np.max(np.abs(original-current)))
    if maximum>.1:raise ValueError(f"Frozen 96-LP trapezoid objective drift USD {maximum}")
    pairs,geo,obj,annuity,cross=summarize_modes(all_lp)
    o=Path(out);o.mkdir(parents=True,exist_ok=True)
    all_lp.to_csv(o/"paper_s_2010_2013_two_hour_approximations_192_LP.csv",index=False,float_format="%.12g")
    pairs.to_csv(o/"paper_s_2010_2013_two_hour_approximations_64_duration_triplets.csv",index=False,float_format="%.12g")
    geo.to_csv(o/"paper_s_2010_2013_two_hour_approximations_32_siting_comparisons.csv",index=False,float_format="%.12g")
    obj.to_csv(o/"paper_s_2010_2013_two_hour_approximations_96_paired_objectives.csv",index=False,float_format="%.12g")
    annuity.to_csv(o/"paper_s_2010_2013_two_hour_approximations_32_paired_annuity.csv",index=False,float_format="%.12g")
    cross.to_csv(o/"paper_s_2010_2013_two_hour_approximations_16_geo_direction_robustness.csv",index=False,float_format="%.12g")
    pd.concat([wa,pa],ignore_index=True).to_csv(
        o/"paper_s_2010_2013_two_hour_approximations_64_calendar_substitution_audit.csv",index=False)
    manifest={
      "status":"ORIGINAL_SOURCE_192_LP_WEATHER_GEO_HOUR_APPROXIMATION_ROBUSTNESS",
      "original_verified_96_LP_run":BASE_RUN,"source_weather_years":list(YEARS),
      "LPs":len(all_lp),"duration_triplets":len(pairs),
      "weather_state_geo_mode_comparisons":len(geo),
      "matched_96_objective_pairs":len(obj),
      "matched_32_annuity_pairs":len(annuity),
      "matched_16_spatial_effect_pairs":len(cross),
      "source_frozen_96_trapezoid_max_objective_delta_usd":maximum,
      "max_abs_annuity_hour_mode_difference_usd_kwh_year":float(
        annuity.annuity_hold_minus_trapezoid.abs().max()),
      "hour_approximation_10usd_screen_flip_count_across_32_geography_scenarios":int(
        annuity["10usd_screen_hour_approximation_flip"].sum()),
      "spatial_effect_direction_disagreements_across_16_year_state_pairs":int(
        (~cross.siting_delta_sign_preserved).sum()),
      "spatial_10usd_screen_status_disagreements_across_16_year_state_pairs":int(
        (~cross.siting_10usd_screen_status_agrees).sum()),
      "2012_AZ_siting_screen_flip_hold":bool(cross.set_index(["weather_year","state"]).loc[
        (2012,"AZ"),"spatial_10usd_screen_flip_hold"]),
      "2012_AZ_siting_screen_flip_trapezoid":bool(cross.set_index(["weather_year","state"]).loc[
        (2012,"AZ"),"spatial_10usd_screen_flip_trapezoid"]),
      "native_instantaneous_source_not_integrated_hourly_energy":True,
      "neither_hour_mode_publisher_certified_physical_hour_integral":True,
      "no_future_climate_prediction_or_2030_actual_fleet_calibration":True}
    (o/"paper_s_2010_2013_two_hour_approximations_192LP_manifest.json").write_text(
        json.dumps(manifest,indent=2)+"\n")
    print(cross.to_string(index=False))
    print(annuity.loc[annuity.state.eq("AZ")].to_string(index=False))
    print(json.dumps(manifest,indent=2))
    print("PAPER_S_ORIGINAL_192LP_WEATHER_GEO_HOUR_APPROXIMATION_PASS")
    return manifest

def main():
    p=argparse.ArgumentParser()
    for arg in ("wind_h5","pv_h5","wind_sc","pv_sc","county_shares",
                "wind_ref","pv_ref","demand_h5","original_96_lps"):
        p.add_argument("--"+arg.replace("_","-"),required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    run(a.wind_h5,a.pv_h5,a.wind_sc,a.pv_sc,a.county_shares,
        a.wind_ref,a.pv_ref,a.demand_h5,a.original_96_lps,a.out)

if __name__=="__main__":main()
