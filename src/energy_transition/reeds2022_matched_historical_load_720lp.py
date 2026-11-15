"""Same-weather historical demand LP sensitivity: 720 ORIGINAL-source LPs.

15 authentic weather years x 4 states x 2 county schemes x 3 durations x
2 distinct demand treatments. Solar/wind source time mapping uses the existing
published CF 2012-support alignment. Historical load hours are mapped by
month/day/hour to the SAME 2012 support, with explicit Feb29 imputation and
Dec31 omission for nonleap years. Neither source point CF integration nor
real 2030 historical-weather-conditioned demand is certified. No 2030 fleet.
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
    reaggregate_years,STATES,DESIGNS,DURATIONS,RATIO,WIND_SHARE,POWER,RTE,HOURS,
)
from energy_transition.reeds2022_historical_weather_demand_audit import (
    verify_historical_md5,parse_native_fixed_cst,HIST_KEYS,
)
from energy_transition.reeds2022_explicit_weather_year_alignment import TARGET_KEYS
from energy_transition.reeds2022_county_full_state_lp import modeled_hourly_cf
from energy_transition.reeds2022_county_ac_normalized_2030 import normalized_pv_ac_cf
from energy_transition.reeds_2022_clocked_demand_branch import (
    verify_official_file,check_fixed_cst_native_labels,
)
from energy_transition.efs_cyclic_storage_lp import solve_zone

LOAD_MODES=("actual_historical_level","historical_weather_shape_scaled_to_2030_annual_energy")
EXPECTED=15*4*2*3*2


def align_original_historical_load(native_index,raw):
    """Replicate original wind/PV calendar map for MWh/h without assuming CF bounds."""
    dates=pd.DatetimeIndex(native_index)
    values=np.asarray(raw,dtype=float)
    if dates.tz is not None or len(dates)!=HOURS or values.shape!=(HOURS,):
        raise ValueError("Expected 8760 single native CST historical load records")
    if dates.has_duplicates or not np.isfinite(values).all() or (values<0).any():
        raise ValueError("Historical load values or clock invalid")
    keys=[(x.month,x.day,x.hour) for x in dates]
    if len(set(keys))!=HOURS:raise ValueError("Duplicate historical load civil hours")
    source=dict(zip(keys,values))
    aligned=[]
    missing=[]
    for mm,dd,hh in TARGET_KEYS:
        key=(mm,dd,hh)
        if key in source:
            aligned.append(float(source[key]))
        elif (mm,dd)==(2,29) and (2,28,hh) in source and (3,1,hh) in source:
            aligned.append(float((source[(2,28,hh)]+source[(3,1,hh)])/2))
            missing.append(key)
        else:
            raise ValueError(f"Unsupported historical demand calendar gap: {key}")
    excluded=set(source)-set(TARGET_KEYS)
    if excluded and excluded!={(12,31,h) for h in range(24)}:
        raise ValueError("Unexpected excluded calendar hours")
    if len(missing) not in (0,24) or len(excluded) not in (0,24):
        raise ValueError("Unaccounted historical demand calendar substitution")
    result=np.asarray(aligned,dtype=float)
    return result,{"interpolated_feb29_hours":len(missing),
        "omitted_dec31_hours":len(excluded),
        "native_mwh_sum":float(values.sum()),
        "aligned_mwh_sum":float(result.sum()),
        "calendar_substitution_mwh":float(result.sum()-values.sum())}


def load_historical_by_weather_year(h5):
    """Require the exactly publisher-authenticated 15-year × 4-state history."""
    verify_historical_md5(h5)
    curves={}
    audit=[]
    with h5py.File(h5,"r") as f:
        if not all(k in f for k in HIST_KEYS):raise ValueError("Historical HDF5 schema drift")
        names=[v.decode("utf-8") if isinstance(v,bytes) else str(v) for v in f["columns"][:]]
        if len(set(names))!=len(names) or any(s not in names for s in STATES):
            raise ValueError("Historical state keys missing/duplicate")
        raw=f["data"]
        idx=f["index_0"][:]
        if raw.shape!=(len(WEATHER_YEARS)*HOURS,len(names)) or len(idx)!=len(WEATHER_YEARS)*HOURS:
            raise ValueError("Historical source matrix inconsistent with 15 years")
        columns=[names.index(s) for s in STATES]
        for i,year in enumerate(WEATHER_YEARS):
            lo=i*HOURS;hi=lo+HOURS
            t=parse_native_fixed_cst(idx[lo:hi])
            expected=pd.date_range(f"{year}-01-01",periods=HOURS,freq="h")
            if not t.equals(expected):raise ValueError(f"Historic native year {year} clock drift")
            block=np.asarray(raw[lo:hi,columns],dtype=float)
            for j,st in enumerate(STATES):
                curve,diag=align_original_historical_load(t,block[:,j])
                if curve.max()<=0:raise ValueError("Zero peak load")
                curves[(year,st)]=curve
                audit.append({"weather_year":year,"state":st,**diag})
    if len(curves)!=60:raise ValueError("60 historical weather year-state curves required")
    return curves,pd.DataFrame(audit)


def analyze(lp):
    case=["weather_year","state","county_weight_scheme","load_mode","battery_duration_h"]
    if len(lp)!=EXPECTED or lp[case].duplicated().any():
        raise ValueError("Exactly 720 unique matched historical load LP cases required")
    expected=pd.MultiIndex.from_product(
        [WEATHER_YEARS,STATES,DESIGNS,LOAD_MODES,DURATIONS],names=case)
    if len(expected.difference(pd.MultiIndex.from_frame(lp[case]))) or len(
        pd.MultiIndex.from_frame(lp[case]).difference(expected)):
        raise ValueError("Incomplete historical demand factorial")
    if not lp.solver_status.eq("optimal").all() or lp.max_equality_residual_mwh.max()>1e-5:
        raise ValueError("Historical LP infeasibility or material balance error")
    triplets=[]
    for key,g in lp.groupby(case[:-1],sort=True):
        part=g.set_index("battery_duration_h")
        obj=part.objective_illustrative_variable_usd
        if set(part.index)!=set(DURATIONS) or obj.loc[0]+.1<obj.loc[4] or obj.loc[4]+.1<obj.loc[8]:
            raise ValueError("Incomplete or nonmonotonic storage duration")
        capacity=(part.loc[8,"storage_capacity_mwh"]-part.loc[4,"storage_capacity_mwh"])*1000.
        if capacity<=0:raise ValueError("Bad storage energy denominator")
        triplets.append(dict(zip(case[:-1],key),
            annualized_marginal_4_to_8_usd_kwh_year=(obj.loc[4]-obj.loc[8])/capacity,
            incremental_operating_cost_avoided_usd=obj.loc[4]-obj.loc[8]))
    pairs=pd.DataFrame(triplets)
    if len(pairs)!=240:raise ValueError("240 matched historical demand triplets required")
    contrast=[]
    for key,g in pairs.groupby(["weather_year","state","load_mode"],sort=True):
        z=g.set_index("county_weight_scheme")
        if set(z.index)!=set(DESIGNS):raise ValueError("Siting scheme incomplete")
        a=float(z.loc[DESIGNS[0],"annualized_marginal_4_to_8_usd_kwh_year"])
        b=float(z.loc[DESIGNS[1],"annualized_marginal_4_to_8_usd_kwh_year"])
        contrast.append(dict(zip(["weather_year","state","load_mode"],key),
            source_potential_usd_kwh_year=a,eia_county_usd_kwh_year=b,
            eia_minus_potential_usd_kwh_year=b-a))
    geo=pd.DataFrame(contrast)
    if len(geo)!=120:raise ValueError("120 historic demand geographic comparisons required")
    return pairs,geo


def run(wind_h5,pv_h5,wind_sc,pv_sc,county_shares,wind_ref,pv_ref,
        historic_load_h5,projected_load_h5,out):
    verify_official_file(Path(projected_load_h5))
    historical,audit=load_historical_by_weather_year(historic_load_h5)
    wind,wa,tw=reaggregate_years(
        wind_h5,wind_sc,"wind",county_shares,wind_ref,years=WEATHER_YEARS)
    solar,sa,tp=reaggregate_years(
        pv_h5,pv_sc,"pv",county_shares,pv_ref,years=WEATHER_YEARS)
    if not tw.equals(tp):raise ValueError("Wind/PV original reference clock drift")
    fixed={}
    with h5py.File(projected_load_h5,"r") as f:
        obj=f["2030"]
        check_fixed_cst_native_labels(obj["datetime"][:])
        clock=pd.DatetimeIndex(pd.to_datetime(
            [x.decode() if isinstance(x,bytes) else str(x) for x in obj["datetime"][:]],
            utc=True))
        if not clock.equals(tw):raise ValueError("Projected 2030 load clock mismatch")
        for st in STATES:
            v=np.asarray(obj[st][:],dtype=float)
            if v.shape!=(HOURS,) or not np.isfinite(v).all() or v.sum()<=0:
                raise ValueError("Projected reference load invalid")
            fixed[st]=v
    rows=[]
    for year in WEATHER_YEARS:
        for st in STATES:
            base=historical[(year,st)]
            scaled=base*(fixed[st].sum()/base.sum())
            for mode,load in zip(LOAD_MODES,(base,scaled)):
                for scheme in DESIGNS:
                    w=modeled_hourly_cf(wind[(year,scheme,st)],"trapezoid_with_first_endpoint")
                    p=normalized_pv_ac_cf(
                        modeled_hourly_cf(solar[(year,scheme,st)],"trapezoid_with_first_endpoint"))
                    mixed=WIND_SHARE*w+(1-WIND_SHARE)*p
                    for hours in DURATIONS:
                        sol=solve_zone(load,mixed,hours,renewable_peak_ratio=RATIO,
                            battery_power_peak_ratio=POWER if hours else 0.,
                            roundtrip_efficiency=RTE,renewable_unit_cost=5.,firm_unit_cost=90.)
                        rows.append({"weather_year":year,"state":st,"county_weight_scheme":scheme,
                            "load_mode":mode,"battery_duration_h":hours,
                            "source_weather_matches_demand":True,
                            "load_is_2030_weather_conditioned_forecast":False,
                            "load_annual_target_is_2030_projection":mode==LOAD_MODES[1],
                            "hour_approximation":"trapezoid_with_first_endpoint",
                            "native_historical_demand_mwh":float(base.sum()),
                            "used_demand_mwh":float(load.sum()),
                            "projected_2030_energy_mwh":float(fixed[st].sum()),
                            "source_hour_integrated_generation_certified":False,
                            **sol})
    lp=pd.DataFrame(rows)
    durations,geography=analyze(lp)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    lp.to_csv(out/"paper_s_same_weather_720_lp.csv",index=False,float_format="%.12g")
    durations.to_csv(out/"paper_s_same_weather_240_duration_triplets.csv",index=False,float_format="%.12g")
    geography.to_csv(out/"paper_s_same_weather_120_spatial_comparisons.csv",index=False,float_format="%.12g")
    audit.to_csv(out/"paper_s_same_weather_60_load_calendar_audit.csv",index=False)
    pd.concat([wa,sa],ignore_index=True).to_csv(
        out/"paper_s_same_weather_240_cf_calendar_audit.csv",index=False)
    manifest={"status":"HISTORICAL_SAME_WEATHER_AND_ENERGY_SCALED_720_LP",
        "cases":len(lp),"weather_years":list(WEATHER_YEARS),
        "duration_triplets":len(durations),"geography_comparisons":len(geography),
        "historical_load_levels_and_shape_distinguished":True,
        "load_year_and_wind_solar_weather_year_matched":True,
        "2030_weather_conditioned_demand_forecast_produced":False,
        "physical_hourly_generation_integral_validated":False,
        "frozen_720_fixed2030_demand_source_results_modified":False}
    (out/"paper_s_same_weather_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("PAPER_S_SAME_WEATHER_HISTORICAL_LOAD_720_LP_PASS")
    print(json.dumps(manifest))
    return lp,durations,geography


def main():
    p=argparse.ArgumentParser()
    for name in ("wind_h5","pv_h5","wind_sc","pv_sc","county_shares",
                 "wind_ref","pv_ref","historic_load_h5","projected_load_h5"):
        p.add_argument("--"+name.replace("_","-"),type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    run(a.wind_h5,a.pv_h5,a.wind_sc,a.pv_sc,a.county_shares,a.wind_ref,a.pv_ref,
        a.historic_load_h5,a.projected_load_h5,a.out)


if __name__=="__main__":main()
