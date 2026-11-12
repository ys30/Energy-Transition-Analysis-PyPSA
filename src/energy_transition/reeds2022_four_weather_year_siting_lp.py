"""Prespecified 2011–2014 ReEDS source-weather interannual sensitivity, 96 LPs.

Source-native county × resource-class wind/PV HDF5, EIA860 2025
operating plant COUNTY weight, frozen 2030 demand and common AC.
Nonleap weather years are mapped by month-day-hour to native 2012
demand support, Feb29 artificially averaged and Dec31 excluded.
This is an illustrative interannual WEATHER sensitivity, NOT a climate
change prediction, valid source hourly energy integral, or future fleet.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import h5py
import numpy as np
import pandas as pd
from energy_transition.reeds2022_county_state_resources import (
    STATES,validate_capacity_key_match,WIND_COUNTY_MD5,PV_COUNTY_MD5,
    WIND_COUNTY_CAPACITY_MD5,PV_COUNTY_CAPACITY_MD5,
)
from energy_transition.reeds2022_real_resource_intake import require_md5,decode
from energy_transition.reeds2022_eia2025_spatial_reweighted_lp import (
    county_tech_weights,DESIGNS,DURATIONS,RATIO,WIND_SHARE,POWER,RTE,paired_summary,
)
from energy_transition.reeds2022_explicit_weather_year_alignment import (
    align_weather_year_to_reeds_2012_support
)
from energy_transition.reeds2022_joint_resource_shape import read_native
from energy_transition.reeds2022_county_full_state_lp import modeled_hourly_cf,HOURS
from energy_transition.reeds2022_county_ac_normalized_2030 import normalized_pv_ac_cf,ILR
from energy_transition.reeds_2022_clocked_demand_branch import verify_official_file,check_fixed_cst_native_labels
from energy_transition.efs_cyclic_storage_lp import solve_zone

YEARS=(2011,2012,2013,2014)
SOURCES={"wind":(WIND_COUNTY_MD5,WIND_COUNTY_CAPACITY_MD5),
         "pv":(PV_COUNTY_MD5,PV_COUNTY_CAPACITY_MD5)}
BASE_RUN=43159121663

def reaggregate_years(h5,sc,tech,county_shares,original_2012_csv):
    original,clock=read_native(original_2012_csv,tech)
    h_md5,c_md5=SOURCES[tech]
    require_md5(h5,h_md5)
    require_md5(sc,c_md5)
    source=pd.read_csv(sc,dtype=str)
    if list(source.columns)!=["class|region","MW"]:raise ValueError("Original ReEDS supply-curve CSV schema drift")
    shares=pd.read_csv(county_shares,dtype={"county_fips":"string"})
    output={}
    audits=[]
    with h5py.File(h5,"r") as f:
        names=decode(f["columns"][:])
        native=pd.DatetimeIndex(pd.to_datetime(decode(f["index_0"][:]),errors="raise"))
        table=validate_capacity_key_match(names,source["class|region"].tolist(),
            pd.to_numeric(source["MW"],errors="raise"),capacity_basis="ac" if tech=="wind" else "dc",tech=tech)
        if names!=table.column.tolist() or not np.issubdtype(f["data"].dtype,np.floating):
            raise ValueError("Original HDF5 resource key ordering/float dtype mismatch")
        weights={st:county_tech_weights(table,shares,tech,st) for st in STATES}
        for year in YEARS:
            idx=np.flatnonzero(native.year==year)
            if len(idx)!=HOURS or not np.array_equal(idx,np.arange(idx[0],idx[0]+HOURS)):
                raise ValueError(f"Source year {year} not original contiguous 8760")
            source_labels=native[idx]
            raw={(scheme,st):np.empty(HOURS,dtype=float) for scheme in DESIGNS for st in STATES}
            for pos in range(0,HOURS,168):
                block=np.asarray(f["data"][idx[pos:pos+168],:],dtype=float)
                if not np.isfinite(block).all() or np.min(block)<-1e-12 or np.max(block)>1+1e-8:
                    raise ValueError(f"Original {tech} {year} CF values invalid")
                for st,(potential,eia) in weights.items():
                    for scheme,w in zip(DESIGNS,(potential,eia)):
                        raw[(scheme,st)][pos:pos+len(block)]=block@w
            for scheme in DESIGNS:
                for st in STATES:
                    original_cf=raw[(scheme,st)]
                    if year==2012 and scheme==DESIGNS[0]:
                        err=float(np.max(np.abs(original_cf-original[st].to_numpy(float))))
                        if err>5e-8:raise ValueError(f"2012 source potential CF anchor drift {tech} {st}: {err}")
                    mapped,calendar=align_weather_year_to_reeds_2012_support(source_labels,original_cf)
                    output[(year,scheme,st)]=mapped
                    audits.append({"technology":tech,"source_weather_year":year,
                        "county_weight_scheme":scheme,"state":st,
                        "original_instantaneous_mean_CF":float(original_cf.mean()),
                        "aligned_instantaneous_mean_CF":float(mapped.mean()),
                        **calendar})
    if len(output)!=len(YEARS)*len(DESIGNS)*len(STATES):
        raise ValueError("Incomplete original source multi-year profiles")
    return output,pd.DataFrame(audits),clock

def summarize(lp):
    pairs=[]
    for (year,st,scheme),g in lp.groupby(["weather_year","state","county_weight_scheme"],sort=True):
        if len(g)!=3 or set(g.battery_duration_h)!=set(DURATIONS):
            raise ValueError("Missing year/state/siting matched durations")
        d=g.set_index("battery_duration_h")
        obj=d.objective_illustrative_variable_usd
        if obj.loc[0]+.1<obj.loc[4] or obj.loc[4]+.1<obj.loc[8]:
            raise ValueError("Battery duration inexplicably increases minimum operating cost")
        additional_kwh=(d.loc[8,"storage_capacity_mwh"]-d.loc[4,"storage_capacity_mwh"])*1000
        if additional_kwh<=0:raise ValueError("Invalid additional storage kWh")
        pairs.append({"weather_year":year,"state":st,"county_weight_scheme":scheme,
            "four_hour_savings_usd":obj.loc[0]-obj.loc[4],
            "eight_hour_savings_usd":obj.loc[0]-obj.loc[8],
            "incremental_4_to_8_hour_savings_usd":obj.loc[4]-obj.loc[8],
            "additional_storage_kwh":additional_kwh,
            "energy_annuity_hurdle_usd_kwh_year":(obj.loc[4]-obj.loc[8])/additional_kwh})
    pair=pd.DataFrame(pairs)
    if len(pair)!=32:raise ValueError("Expected exactly 32 within-weather-year 0/4/8h triplets")
    index=["weather_year","state"]
    resource=pair[pair.county_weight_scheme.eq(DESIGNS[0])].set_index(index).sort_index()
    siting=pair[pair.county_weight_scheme.eq(DESIGNS[1])].set_index(index).sort_index()
    if len(resource)!=16 or not resource.index.equals(siting.index):
        raise ValueError("Missing 16 matched weather year × state geography pairs")
    delta=pd.DataFrame(index=resource.index)
    for metric in ("four_hour_savings_usd","eight_hour_savings_usd",
                   "incremental_4_to_8_hour_savings_usd","energy_annuity_hurdle_usd_kwh_year"):
        delta[metric+"_potential"]=resource[metric]
        delta[metric+"_EIA2025_county"]=siting[metric]
        delta[metric+"_EIA_minus_potential"]=siting[metric]-resource[metric]
    delta["potential_meets_illustrative_10usd_screen"]=resource.energy_annuity_hurdle_usd_kwh_year>=10
    delta["eia2025_meets_illustrative_10usd_screen"]=siting.energy_annuity_hurdle_usd_kwh_year>=10
    delta["spatial_weight_10usd_screen_flips"]=(
        delta.potential_meets_illustrative_10usd_screen !=
        delta.eia2025_meets_illustrative_10usd_screen)
    return pair,delta.reset_index()

def run(wind_h5,pv_h5,wind_sc,pv_sc,county_shares,wind_ref,pv_ref,demand_h5,reference_2012_24lp,out):
    verify_official_file(Path(demand_h5))
    wind,wa,tw=reaggregate_years(wind_h5,wind_sc,"wind",county_shares,wind_ref)
    pv,pa,tp=reaggregate_years(pv_h5,pv_sc,"pv",county_shares,pv_ref)
    if not tw.equals(tp):raise ValueError("Frozen original reference wind/PV source clocks disagree")
    rows=[]
    with h5py.File(demand_h5,"r") as f:
        d=f["2030"]
        check_fixed_cst_native_labels(d["datetime"][:])
        native=pd.DatetimeIndex(pd.to_datetime([x.decode() if isinstance(x,bytes) else str(x)
            for x in d["datetime"][:]],utc=True))
        if not native.equals(tw):raise ValueError("Original demand/reference-year source UTC times differ")
        for st in STATES:
            load=np.asarray(d[st][:],dtype=float)
            if load.shape!=(HOURS,) or not np.isfinite(load).all() or (load<0).any():
                raise ValueError("Invalid ReEDS 2030 demand")
            for year in YEARS:
                for scheme in DESIGNS:
                    w=modeled_hourly_cf(wind[(year,scheme,st)],"trapezoid_with_first_endpoint")
                    p=normalized_pv_ac_cf(modeled_hourly_cf(pv[(year,scheme,st)],"trapezoid_with_first_endpoint"))
                    mixed=WIND_SHARE*w+(1-WIND_SHARE)*p
                    for duration in DURATIONS:
                        sol=solve_zone(load,mixed,duration,renewable_peak_ratio=RATIO,
                            battery_power_peak_ratio=POWER if duration else 0.,
                            roundtrip_efficiency=RTE,renewable_unit_cost=5.,firm_unit_cost=90.)
                        rows.append({"weather_year":year,"state":st,"county_weight_scheme":scheme,
                            "demand_projection_year":2030,"eia_operating_siting_year":2025 if scheme==DESIGNS[1] else None,
                            "reference_calendar":"2012 native source 8760 support",
                            "nonleap_feb29_synthesized":year!=2012,
                            "weather_year_is_climate_change_projection":False,
                            "source_hourly_energy_integral_certified":False,
                            "actual_installed_2030_fleet":False,
                            "battery_duration_h":duration,"battery_power_peak_ratio":POWER if duration else 0.,
                            "total_renewable_AC_nameplate_per_peak":RATIO,
                            "wind_share_common_AC":WIND_SHARE,"PV_original_ILR":ILR,
                            **sol})
    frame=pd.DataFrame(rows)
    if len(frame)!=96 or not frame.solver_status.eq("optimal").all() or frame.max_equality_residual_mwh.max()>1e-5:
        raise ValueError("96 weather year LPs not all optimum or conserved")
    orig=pd.read_csv(reference_2012_24lp)
    old=orig.set_index(["state","county_weight_scheme","battery_duration_h"]).objective_illustrative_variable_usd.sort_index()
    new=frame[frame.weather_year.eq(2012)].set_index(
        ["state","county_weight_scheme","battery_duration_h"]).objective_illustrative_variable_usd.sort_index()
    if len(old)!=24 or len(new)!=24 or not old.index.equals(new.index):
        raise ValueError("Original 24 LP 2012 geo-siting anchor not covered")
    maxdiff=float(np.abs(old-new).max())
    if maxdiff>.1:raise ValueError(f"Frozen 2012 24-LP objective drift {maxdiff}")
    pairs,delta=summarize(frame)
    o=Path(out);o.mkdir(parents=True,exist_ok=True)
    frame.to_csv(o/"paper_s_2011_2014_weather_year_96_geography_duration_LPs.csv",index=False,float_format="%.12g")
    pairs.to_csv(o/"paper_s_2011_2014_weather_year_32_storage_triplets.csv",index=False,float_format="%.12g")
    delta.to_csv(o/"paper_s_2011_2014_weather_year_16_siting_comparisons.csv",index=False,float_format="%.12g")
    audit=pd.concat([wa,pa],ignore_index=True)
    audit.to_csv(o/"paper_s_2011_2014_weather_year_64_calendar_mapping_diagnostics.csv",index=False)
    summary={"status":"REEDS_SOURCE_2011_2014_FOUR_WEATHER_YEAR_96_LP_WITH_EIA2025_SITING",
      "original_source_HDF5_MD5":{k:SOURCES[k][0] for k in SOURCES},
      "weather_years":list(YEARS),"complete_LPs":len(frame),"duration_triplets":len(pairs),
      "matched_geographical_comparisons":len(delta),
      "calendar_mapping_diagnostics":len(audit),
      "frozen_2012_24_LP_max_objective_delta_usd":maxdiff,
      "spatial_siting_10usd_screen_flips_across_four_weather_years":int(delta.spatial_weight_10usd_screen_flips.sum()),
      "nonleap_synthetic_feb29_hours_each_curve":24,
      "2025_fleet_siting_is_a_2030_installed_forecast":False,
      "interannual_weather_is_a_future_climate_change_projection":False,
      "hourly_integrated_source_generation_certified":False,
      "calendar_feb29_imputation_is_observed_weather":False,
      "battery_capex_or_real_market_profits_modeled":False}
    (o/"paper_s_2011_2014_weather_96LP_manifest.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(delta[["weather_year","state","energy_annuity_hurdle_usd_kwh_year_potential",
      "energy_annuity_hurdle_usd_kwh_year_EIA2025_county","spatial_weight_10usd_screen_flips"]].to_string(index=False))
    print(json.dumps(summary,indent=2))
    print("PAPER_S_4_WEATHER_YEAR_96_SOURCE_HDF5_LP_AND_2012_FROZEN_ANCHOR_PASS")
    return frame,pairs,delta

def main():
    p=argparse.ArgumentParser()
    for arg in ("wind_h5","pv_h5","wind_sc","pv_sc","county_shares",
        "wind_ref","pv_ref","demand_h5","reference_2012_24lp"):
        p.add_argument("--"+arg.replace("_","-"),type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    run(a.wind_h5,a.pv_h5,a.wind_sc,a.pv_sc,a.county_shares,a.wind_ref,a.pv_ref,
        a.demand_h5,a.reference_2012_24lp,a.out)

if __name__=="__main__":main()
