"""Reweight ReEDS 2012 county-class source CF by observed EIA-860 2025 county siting.

Original 2012 publisher instantaneous reference weather; 2025 EIA county
installed generator AC nameplate *shares*; within each county source class
mix remains developer-available ReEDS supply potential MW proportions.
2030 projected demand and 0/4/8h HiGHS copperplate dispatch are an
explicitly cross-year numerical scenario, not observed generation or
a forecast of actual installed 2030 plants. Source-HDF5 model must
numerically reproduce the frozen resource-potential 2012 four-state CF
for both wind (AC) and utility PV (AC grid/DC array) before using any
counterfactual EIA geographic weighting.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd
import h5py
from energy_transition.reeds2022_county_state_resources import (
    STATES as STATE_FIPS,validate_capacity_key_match,
    WIND_COUNTY_MD5,PV_COUNTY_MD5,WIND_COUNTY_CAPACITY_MD5,PV_COUNTY_CAPACITY_MD5,
)
from energy_transition.reeds2022_real_resource_intake import require_md5,inspect_weather_index,decode
from energy_transition.reeds2022_joint_resource_shape import read_native
from energy_transition.reeds2022_county_full_state_lp import modeled_hourly_cf,HOURS
from energy_transition.reeds2022_county_ac_normalized_2030 import normalized_pv_ac_cf,ILR
from energy_transition.efs_cyclic_storage_lp import solve_zone
from energy_transition.reeds_2022_clocked_demand_branch import verify_official_file,check_fixed_cst_native_labels

SOURCES={"wind":(WIND_COUNTY_MD5,WIND_COUNTY_CAPACITY_MD5),
         "pv":(PV_COUNTY_MD5,PV_COUNTY_CAPACITY_MD5)}
DESIGNS=("source_potential_2012","eia_2025_operating_county_weight")
DURATIONS=(0,4,8)
RATIO=1.5
WIND_SHARE=.5
POWER=.25
RTE=.9
SOURCE_BASELINE=43058074434
EIA_SOURCE=43124063185

def county_tech_weights(table,site_shares,tech,st):
    """Exact county geographic reallocation; resource class mix conditional on county."""
    t=table.copy()
    fips=STATE_FIPS[st]
    state_mask=t.state_fips.eq(fips).to_numpy()
    cap=t.capacity_mw.to_numpy(dtype=float)
    supply=np.where(state_mask,cap,0.)
    if supply.sum()<=0:raise ValueError("No original developer resource potential")
    potential=supply/supply.sum()
    county_total=t.groupby("county_fips").capacity_mw.transform("sum").to_numpy(dtype=float)
    slice_eia=site_shares.loc[(site_shares.state.eq(st))&
                             (site_shares.technology.eq(tech)),["county_fips","eia2025_share_among_geocoded"]]
    if slice_eia.empty or slice_eia.county_fips.duplicated().any():
        raise ValueError("Missing/duplicate site weights for study state and technology")
    shares=pd.Series(slice_eia.eia2025_share_among_geocoded.to_numpy(float),
                     index=slice_eia.county_fips.astype(str))
    if not np.isfinite(shares.to_numpy()).all() or (shares<0).any() or abs(shares.sum()-1)>1e-10:
        raise ValueError("EIA county weights must sum exactly to one")
    missing=shares[(shares>0)&(~shares.index.isin(t.loc[state_mask,"county_fips"]))]
    if len(missing):raise ValueError(f"Observed EIA county missing ReEDS source CF classes: {list(missing.index)}")
    per_class=t.county_fips.map(shares).fillna(0).to_numpy(float)
    eia=np.where(state_mask & (county_total>0),per_class*cap/np.maximum(county_total,1e-30),0.)
    if abs(eia.sum()-1)>1e-9 or abs(potential.sum()-1)>1e-9 or (eia<0).any():
        raise ValueError("Geographic and conditional source-class weights do not conserve unity")
    return potential,eia

def original_class_profiles(h5_path,sc_path,tech,county_share_csv,reference_csv):
    md5,capacity_md5=SOURCES[tech]
    require_md5(Path(h5_path),md5)
    require_md5(Path(sc_path),capacity_md5)
    supply=pd.read_csv(sc_path,dtype=str)
    if list(supply.columns)!=["class|region","MW"]:
        raise ValueError("ReEDS source capacity schema changed")
    cf_ref,tref=read_native(reference_csv,tech)
    sites=pd.read_csv(county_share_csv,dtype={"county_fips":"string"})
    needed={"technology","state","county_fips","eia2025_share_among_geocoded"}
    if not needed.issubset(sites.columns):raise ValueError("Missing independently checked EIA county weights")
    all_weights={}
    all_outputs={design:{} for design in DESIGNS}
    with h5py.File(h5_path,"r") as f:
        names=decode(f["columns"][:])
        rows,clock=inspect_weather_index(f["index_0"][:])
        if len(rows)!=HOURS or f["data"].shape[1]!=len(names):
            raise ValueError("ReEDS HDF5 source indices wrong")
        table=validate_capacity_key_match(names,supply["class|region"].tolist(),
              pd.to_numeric(supply["MW"],errors="raise"),capacity_basis="dc" if tech=="pv" else "ac",tech=tech)
        if names!=table.column.tolist() or not np.issubdtype(f["data"].dtype,np.floating):
            raise ValueError("Unexpected original native class column order or encoding")
        for state in STATE_FIPS:
            all_weights[state]=county_tech_weights(table,sites,tech,state)
        # Store only four time-series per design; read source rows in bounded chunks.
        for state in STATE_FIPS:
            for design in DESIGNS:all_outputs[design][state]=np.empty(HOURS,dtype=float)
        for off in range(0,HOURS,168):
            indices=rows[off:off+168]
            block=np.asarray(f["data"][indices,:],dtype=float)
            if not np.isfinite(block).all() or np.min(block)<-1e-12 or np.max(block)>1+1e-8:
                raise ValueError("Invalid original source CF data")
            for state,(w_p,w_e) in all_weights.items():
                all_outputs[DESIGNS[0]][state][off:off+len(indices)]=block@w_p
                all_outputs[DESIGNS[1]][state][off:off+len(indices)]=block@w_e
    errors={}
    for state in STATE_FIPS:
        original=cf_ref[state].to_numpy(float)
        rebuilt=all_outputs[DESIGNS[0]][state]
        err=float(np.max(np.abs(rebuilt-original)))
        errors[state]=err
        if err>5e-8:
            raise ValueError(f"Original potential-weighted {tech} county/HDF5 baseline mismatch in {state}: {err}")
        if not all(np.isfinite(all_outputs[d][state]).all() for d in DESIGNS):
            raise ValueError("Nonfinite county reaggregated time series")
    print("SOURCE_CLASS_HDF5_REWEIGHT_BASELINE_VALIDATED",tech,errors)
    return all_outputs,errors,tref

def paired_summary(lp):
    key=["state","county_weight_scheme"]
    r=[]
    for (st,scheme),g in lp.groupby(key):
        if len(g)!=3 or set(g.battery_duration_h)!=set(DURATIONS):
            raise ValueError("Missing battery duration source comparison")
        d=g.set_index("battery_duration_h")
        obj=d.objective_illustrative_variable_usd
        if obj.loc[0]+.1<obj.loc[4] or obj.loc[4]+.1<obj.loc[8]:
            raise ValueError("8-hour battery should not worsen optimum objective")
        delta_energy=1000*(d.loc[8,"storage_capacity_mwh"]-d.loc[4,"storage_capacity_mwh"])
        if delta_energy<=0:raise ValueError("Invalid battery duration capacity")
        r.append({"state":st,"county_weight_scheme":scheme,
           "four_hour_operating_savings_usd":obj.loc[0]-obj.loc[4],
           "eight_hour_operating_savings_usd":obj.loc[0]-obj.loc[8],
           "incremental_4_to_8h_savings_usd":obj.loc[4]-obj.loc[8],
           "incremental_energy_kwh":delta_energy,
           "incremental_4_to_8h_energy_annuity_usd_per_kwh_year":(obj.loc[4]-obj.loc[8])/delta_energy})
    pairs=pd.DataFrame(r)
    if len(pairs)!=8:raise ValueError("Expected 8 0/4/8 duration groups")
    base=pairs[pairs.county_weight_scheme.eq(DESIGNS[0])].set_index("state").sort_index()
    alt=pairs[pairs.county_weight_scheme.eq(DESIGNS[1])].set_index("state").sort_index()
    if not base.index.equals(alt.index) or len(base)!=4:
        raise ValueError("Missing state source geographic counterfactual")
    delta=pd.DataFrame(index=base.index)
    fields=("four_hour_operating_savings_usd","eight_hour_operating_savings_usd",
            "incremental_4_to_8h_savings_usd",
            "incremental_4_to_8h_energy_annuity_usd_per_kwh_year")
    for field in fields:
        delta[field+"_potential"]=base[field]
        delta[field+"_EIA2025_county"]=alt[field]
        delta[field+"_EIA_minus_potential"]=alt[field]-base[field]
    delta["10usd_energy_annuity_screen_flips"]=(
        base[fields[-1]].ge(10)!=alt[fields[-1]].ge(10))
    return pairs,delta.reset_index()

def run(wind_h5,pv_h5,wind_sc,pv_sc,county_shares,wind_ref,pv_ref,
        demand_h5,base_180,out):
    import h5py
    verify_official_file(Path(demand_h5))
    wind,wind_errors,wt=original_class_profiles(wind_h5,wind_sc,"wind",county_shares,wind_ref)
    pv,pv_errors,pt=original_class_profiles(pv_h5,pv_sc,"pv",county_shares,pv_ref)
    if not wt.equals(pt):raise ValueError("Wind and PV source clock differs")
    base=pd.read_csv(base_180)
    rec=[]
    with h5py.File(demand_h5,"r") as f:
        g=f["2030"]
        check_fixed_cst_native_labels(g["datetime"][:])
        dt=pd.DatetimeIndex(pd.to_datetime([v.decode() if isinstance(v,bytes) else str(v)
            for v in g["datetime"][:]],utc=True))
        if not dt.equals(wt):raise ValueError("Demand and raw CF publisher native time index differs")
        for st in STATE_FIPS:
            load=np.asarray(g[st][:],dtype=float)
            if len(load)!=HOURS or not np.isfinite(load).all() or (load<0).any():
                raise ValueError("Invalid source load")
            for scheme in DESIGNS:
                w=modeled_hourly_cf(wind[scheme][st],"trapezoid_with_first_endpoint")
                s=normalized_pv_ac_cf(modeled_hourly_cf(pv[scheme][st],"trapezoid_with_first_endpoint"))
                combined=WIND_SHARE*w+(1-WIND_SHARE)*s
                if (combined>1).any() or (combined<0).any():
                    raise ValueError("Invalid common AC renewable CF")
                for duration in DURATIONS:
                    opt=solve_zone(load,combined,duration,renewable_peak_ratio=RATIO,
                         battery_power_peak_ratio=POWER if duration else 0.,
                         roundtrip_efficiency=RTE,renewable_unit_cost=5.,firm_unit_cost=90.)
                    rec.append({"state":st,"demand_model_year":2030,
                        "weather_reference_year":2012,"county_siting_source_year":2025 if scheme==DESIGNS[1] else None,
                        "county_weight_scheme":scheme,"source_wind_share_AC":WIND_SHARE,
                        "renewable_AC_nameplate_ratio_to_peak":RATIO,
                        "pv_inverter_loading_ratio":ILR,"battery_power_peak_ratio":POWER if duration else 0.,
                        "battery_duration_h":duration,"weather_hour_approximation":"trapezoid_with_first_endpoint",
                        "generator_technology_class_assigned_within_EIA_county_from_ReEDS_potential":True,
                        "measured_2025_generation":False,
                        "observed_2030_buildout_or_net_investment":False,
                        **opt})
    frame=pd.DataFrame(rec)
    if len(frame)!=24 or not frame.solver_status.eq("optimal").all() or frame.max_equality_residual_mwh.max()>1e-5:
        raise ValueError("24 LP original weather state counterfactuals not feasible")
    # Match frozen 180-AC source case: 4 states x 0/4/8h, power 25% peak, r 1.5, wind .5.
    base=base[(base.renewable_peak_ratio.eq(RATIO))&
              (base.wind_share_installed_mw.eq(WIND_SHARE))&
              ((base.battery_power_peak_ratio.eq(POWER))|base.battery_duration_h.eq(0))]
    old=base.set_index(["state","battery_duration_h"]).objective_illustrative_variable_usd.sort_index()
    new=frame[frame.county_weight_scheme.eq(DESIGNS[0])].set_index(
        ["state","battery_duration_h"]).objective_illustrative_variable_usd.sort_index()
    if len(old)!=12 or len(new)!=12 or not old.index.equals(new.index):
        raise ValueError("Original common-AC source LP anchor incomplete")
    maxdiff=float(np.max(np.abs(old-new)))
    if maxdiff>.1:raise ValueError(f"Frozen potential basis LP objective drift {maxdiff}")
    pairs,delta=paired_summary(frame)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    frame.to_csv(out/"paper_s_2030_EIA2025_county_weight_vs_source_potential_24_LP.csv",index=False,float_format="%.12g")
    pairs.to_csv(out/"paper_s_2030_EIA2025_vs_potential_8_battery_pairs.csv",index=False,float_format="%.12g")
    delta.to_csv(out/"paper_s_2030_EIA2025_vs_potential_4_state_storage_value_effects.csv",index=False,float_format="%.12g")
    profiles=pd.DataFrame({"source_instantaneous_CST":pd.date_range("2012-01-01",periods=HOURS,freq="h",tz="Etc/GMT+6").astype(str)})
    for tech,series in (("wind",wind),("pv",pv)):
        for scheme in DESIGNS:
            for st in STATE_FIPS:
                profiles[f"{st}_{tech}_{scheme}"]=series[scheme][st]
    profiles.to_csv(out/"paper_s_2012_4state_EIA2025_vs_resource_weighted_original_instantaneous_CF.csv",index=False,float_format="%.12g")
    manifest={"status":"REEDS_ORIGINAL_2012_FOUR_STATE_EIA2025_SITING_WEIGHTED_24_LP_VERIFIED",
        "source_HDF5_original_MD5_wind":WIND_COUNTY_MD5,"source_HDF5_original_MD5_pv":PV_COUNTY_MD5,
        "source_EIA2025_site_workflow":EIA_SOURCE,"source_2012_original_CFs_workflow":42962740548,
        "frozen_common_AC_LP_workflow":SOURCE_BASELINE,
        "wind_max_abs_reconstructed_potential_CF_error":wind_errors,
        "pv_max_abs_reconstructed_potential_CF_error":pv_errors,
        "frozen_12_original_AC_source_objectives_max_abs_error_usd":maxdiff,
        "original_LPs":len(frame),"matched_storage_triplets":len(pairs),
        "states_compared":len(delta),"10usd_battery_threshold_decision_flips":int(delta["10usd_energy_annuity_screen_flips"].sum()),
        "2025_plant_county_only_no_technology_class_or_vintage_calibration":True,
        "reference_weather_2012_year_end_truncated":True,
        "2030_demand_projected_not_observed":True,
        "publisher_hourly_integrated_generation_certified":False,
        "2025_actual_generator_output_measured":False,
        "battery_capex_or_plant_market_value_modeled":False}
    (out/"paper_s_EIA2025_siting_2012_weather_2030_demand_24_LP_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(delta.to_string(index=False))
    print(json.dumps(manifest,indent=2))
    print("EIA2025_COUNTY_SITING_2012_SOURCE_WEATHER_2030_DEMAND_24_LP_PASS")
    return frame,pairs,delta

def main():
    p=argparse.ArgumentParser()
    for arg in ("wind_h5","pv_h5","wind_sc","pv_sc","county_shares",
                "wind_ref","pv_ref","demand_h5","base_180"):
        p.add_argument("--"+arg.replace("_","-"),required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    run(a.wind_h5,a.pv_h5,a.wind_sc,a.pv_sc,a.county_shares,a.wind_ref,a.pv_ref,
        a.demand_h5,a.base_180,a.out)

if __name__=="__main__":main()
