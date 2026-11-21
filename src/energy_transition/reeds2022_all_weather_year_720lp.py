"""All 15 authenticated ReEDS source weather years × county siting × duration × hour mode.

Fixed ReEDS 2030 demand has 2012 weather support. This is a controlled,
non-contemporaneous numerical sensitivity, NOT matched-weather load,
observed 2030 dispatch, or authenticated hourly-integrated generation.
Frozen 2010–2013 original 192 LP objectives are required regression anchors.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import h5py
import numpy as np
import pandas as pd
from energy_transition.reeds2022_four_weather_year_siting_lp import (
    reaggregate_years, STATES, DESIGNS, DURATIONS, RATIO, WIND_SHARE, POWER, RTE, ILR, HOURS,
)
from energy_transition.reeds2022_96lp_hour_approximation_192lp import MODES
from energy_transition.reeds2022_county_full_state_lp import modeled_hourly_cf
from energy_transition.reeds2022_county_ac_normalized_2030 import normalized_pv_ac_cf
from energy_transition.reeds_2022_clocked_demand_branch import (
    verify_official_file, check_fixed_cst_native_labels,
)
from energy_transition.efs_cyclic_storage_lp import solve_zone

WEATHER_YEARS=tuple(list(range(2007,2014))+list(range(2016,2024)))
PILOT_YEARS=(2010,2011,2012,2013)
EXPECTED=15*4*2*3*2
CASE_KEYS=["weather_year","state","county_weight_scheme","hour_approximation","battery_duration_h"]


def summarize_all(lp):
    required={"weather_year","state","county_weight_scheme","hour_approximation",
              "battery_duration_h","objective_illustrative_variable_usd",
              "storage_capacity_mwh","solver_status","max_equality_residual_mwh"}
    if not required.issubset(lp.columns):
        raise ValueError("Incomplete LP output schema")
    if len(lp)!=EXPECTED or lp[CASE_KEYS].duplicated().any():
        raise ValueError("720 unique case identities required")
    expected=pd.MultiIndex.from_product(
        [WEATHER_YEARS,STATES,DESIGNS,MODES,DURATIONS],names=CASE_KEYS)
    actual=pd.MultiIndex.from_frame(lp[CASE_KEYS])
    if len(expected.difference(actual)) or len(actual.difference(expected)):
        raise ValueError("Missing or extra weather/state/scheme/mode/duration cases")
    if not lp.solver_status.eq("optimal").all() or (
        not np.isfinite(lp.objective_illustrative_variable_usd.to_numpy(dtype=float)).all()
    ) or lp.max_equality_residual_mwh.max()>1e-5:
        raise ValueError("Source LP optimality or numerical conservation failed")
    pairs=[]
    keys=CASE_KEYS[:-1]
    for key,group in lp.groupby(keys,sort=True):
        row=group.set_index("battery_duration_h")
        obj=row.objective_illustrative_variable_usd
        if not set(row.index)==set(DURATIONS) or obj.loc[0]+.1<obj.loc[4] or obj.loc[4]+.1<obj.loc[8]:
            raise ValueError("Duration completeness or monotonic objective failure")
        delta_energy=(row.loc[8,"storage_capacity_mwh"]-row.loc[4,"storage_capacity_mwh"])*1000.
        if delta_energy<=0:raise ValueError("Invalid energy extension denominator")
        pairs.append(dict(zip(keys,key),additional_storage_kwh=delta_energy,
            marginal_4_to_8_usd_kwh_year=(obj.loc[4]-obj.loc[8])/delta_energy,
            avoided_variable_cost_usd=obj.loc[4]-obj.loc[8]))
    duration=pd.DataFrame(pairs)
    if len(duration)!=240:raise ValueError("Expected 240 duration triplets")
    geo=[]
    for key,group in duration.groupby(["weather_year","state","hour_approximation"],sort=True):
        idx=group.set_index("county_weight_scheme")
        if set(idx.index)!=set(DESIGNS):raise ValueError("Unmatched source/EIA geography")
        a=float(idx.loc[DESIGNS[0],"marginal_4_to_8_usd_kwh_year"])
        b=float(idx.loc[DESIGNS[1],"marginal_4_to_8_usd_kwh_year"])
        geo.append(dict(zip(["weather_year","state","hour_approximation"],key),
            source_potential_usd_kwh_year=a,eia_county_usd_kwh_year=b,
            eia_minus_potential_usd_kwh_year=b-a))
    contrasts=pd.DataFrame(geo)
    if len(contrasts)!=120:raise ValueError("Expected 120 weather/state/mode contrasts")
    hold=contrasts[contrasts.hour_approximation==MODES[0]].set_index(["weather_year","state"]).sort_index()
    trap=contrasts[contrasts.hour_approximation==MODES[1]].set_index(["weather_year","state"]).sort_index()
    if len(hold)!=60 or not hold.index.equals(trap.index):
        raise ValueError("Expected 60 matched hour-convention contrasts")
    paired=hold[["eia_minus_potential_usd_kwh_year"]].rename(columns={
        "eia_minus_potential_usd_kwh_year":"effect_hold"})
    paired["effect_trapezoid"]=trap.eia_minus_potential_usd_kwh_year
    paired["same_sign"]=np.sign(paired.effect_hold)==np.sign(paired.effect_trapezoid)
    return duration,contrasts,paired.reset_index()


def check_frozen_192(current,original):
    frozen=pd.read_csv(original)
    key=CASE_KEYS
    old=frozen.set_index(key).objective_illustrative_variable_usd.sort_index()
    pilot=current[current.weather_year.isin(PILOT_YEARS)].set_index(key).objective_illustrative_variable_usd.sort_index()
    if len(old)!=192 or len(pilot)!=192 or not old.index.is_unique or not old.index.equals(pilot.index):
        raise ValueError("Frozen 192 LP case IDs not precisely reproduced")
    max_abs=float((old-pilot).abs().max())
    if not np.isfinite(max_abs) or max_abs>0.1:raise ValueError(f"192 LP anchor drift USD {max_abs}")
    return max_abs


def run(wind_h5,pv_h5,wind_sc,pv_sc,county_shares,wind_ref,pv_ref,demand_h5,
        frozen_192_lps,out):
    verify_official_file(Path(demand_h5))
    weather_w,wa,tw=reaggregate_years(
        wind_h5,wind_sc,"wind",county_shares,wind_ref,years=WEATHER_YEARS)
    weather_p,pa,tp=reaggregate_years(
        pv_h5,pv_sc,"pv",county_shares,pv_ref,years=WEATHER_YEARS)
    if not tw.equals(tp):raise ValueError("Original wind/PV reference index mismatch")
    rows=[]
    with h5py.File(demand_h5,"r") as f:
        original=f["2030"]
        check_fixed_cst_native_labels(original["datetime"][:])
        clock=pd.DatetimeIndex(pd.to_datetime(
            [v.decode() if isinstance(v,bytes) else str(v) for v in original["datetime"][:]],
            utc=True))
        if not clock.equals(tw):raise ValueError("2030 fixed 2012 reference clock differs")
        for st in STATES:
            load=np.asarray(original[st][:],dtype=float)
            if load.shape!=(HOURS,) or not np.isfinite(load).all() or (load<0).any():
                raise ValueError("Invalid original 2030 state demand")
            for year in WEATHER_YEARS:
                for scheme in DESIGNS:
                    for mode in MODES:
                        w=modeled_hourly_cf(weather_w[(year,scheme,st)],mode)
                        pv=normalized_pv_ac_cf(modeled_hourly_cf(weather_p[(year,scheme,st)],mode))
                        mixed=WIND_SHARE*w+(1-WIND_SHARE)*pv
                        for duration in DURATIONS:
                            sol=solve_zone(
                                load,mixed,duration,renewable_peak_ratio=RATIO,
                                battery_power_peak_ratio=POWER if duration else 0.,
                                roundtrip_efficiency=RTE,renewable_unit_cost=5.,
                                firm_unit_cost=90.)
                            rows.append({"weather_year":year,"state":st,
                                "county_weight_scheme":scheme,"hour_approximation":mode,
                                "battery_duration_h":duration,
                                "demand_projection_year":2030,"weather_reference_demand_year":2012,
                                "eia_siting_reference_year":2025,"weather_load_contemporaneous":year==2012,
                                "nonleap_Feb29_synthetic":year not in (2008,2012,2016,2020),
                                "source_hourly_integrated_generation_verified":False,
                                "real_fleet_2030_simulation":False,**sol})
    lp=pd.DataFrame(rows)
    durations,geography,method_pairs=summarize_all(lp)
    drift=check_frozen_192(lp,frozen_192_lps)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    lp.to_csv(out/"paper_s_all15_720_lp.csv",index=False,float_format="%.12g")
    durations.to_csv(out/"paper_s_all15_240_duration_triplets.csv",index=False,float_format="%.12g")
    geography.to_csv(out/"paper_s_all15_120_siting_comparisons.csv",index=False,float_format="%.12g")
    method_pairs.to_csv(out/"paper_s_all15_60_hour_method_pairs.csv",index=False,float_format="%.12g")
    pd.concat([wa,pa],ignore_index=True).to_csv(
        out/"paper_s_all15_calendar_audit.csv",index=False)
    manifest={
        "status":"ALL15_SOURCE_720_LP_ONLY_AFTER_SUCCESSFUL_COMPLETION",
        "weather_years":list(WEATHER_YEARS),"LPs":len(lp),
        "duration_triplets":len(durations),
        "siting_comparisons":len(geography),"hour_mode_comparisons":len(method_pairs),
        "frozen_192_max_objective_drift_usd":drift,
        "hour_mode_spatial_effect_sign_agreement":int(method_pairs.same_sign.sum()),
        "comparison_count":60,
        "source_CF_is_instantaneous_not_integrated":True,
        "2030_demand_weather_year_fixed_to_2012":True,
        "observed_2025_siting_not_future_fleet":True,
    }
    (out/"paper_s_all15_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("PAPER_S_ALL15_720_LP_FROZEN_192_REGRESSION_PASS",json.dumps(manifest))
    return lp,durations,geography,method_pairs


def main():
    parser=argparse.ArgumentParser()
    for name in ("wind_h5","pv_h5","wind_sc","pv_sc","county_shares",
                 "wind_ref","pv_ref","demand_h5","frozen_192_lps"):
        parser.add_argument("--"+name.replace("_","-"),type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    a=parser.parse_args()
    run(a.wind_h5,a.pv_h5,a.wind_sc,a.pv_sc,a.county_shares,a.wind_ref,a.pv_ref,
        a.demand_h5,a.frozen_192_lps,a.out)


if __name__=="__main__":
    main()
