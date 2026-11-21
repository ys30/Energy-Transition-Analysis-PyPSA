"""Paper S Colorado R=2, wind 40/50/60 hourly SOC/curtailment active-set audit.

Independent, source-pinned re-solves. LP optimal dispatch can be degenerate:
individual SOC trajectories and shadow prices are basis-specific and therefore
descriptive, not uniquely identified economic mechanisms or causal effects.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import numpy as np,pandas as pd,h5py
from energy_transition.reeds2022_all_weather_year_720lp import WEATHER_YEARS
from energy_transition.reeds2022_four_weather_year_siting_lp import (
    reaggregate_years,DESIGNS,POWER,RTE,HOURS)
from energy_transition.reeds2022_county_full_state_lp import modeled_hourly_cf
from energy_transition.reeds2022_county_ac_normalized_2030 import normalized_pv_ac_cf
from energy_transition.reeds_2022_clocked_demand_branch import (
    verify_official_file,check_fixed_cst_native_labels)
from energy_transition.efs_cyclic_storage_lp import solve_zone

STATE="CO"; RATIO=2.0; SHARES=(.40,.50,.60); DURATIONS=(4,8)
HOUR="trapezoid_with_first_endpoint"
KEYS=["weather_year","state","county_weight_scheme","wind_share_ac","battery_duration_h"]

def sha(a):
    return hashlib.sha256(np.asarray(a,dtype="<f8").tobytes()).hexdigest()

def audit_summary(trace,dual,sol):
    p=float(sol["storage_power_mw"]);e=float(sol["storage_capacity_mwh"])
    x={
      "source_hour_count":len(trace),
      "soc_at_upper_hours":int(trace.soc_at_energy_limit.sum()),
      "charge_at_power_hours":int(trace.charge_at_power_limit.sum()),
      "discharge_at_power_hours":int(trace.discharge_at_power_limit.sum()),
      "curtailment_positive_hours":int((trace.unused_renewable_mwh>1e-6).sum()),
      "charge_positive_hours":int((trace.storage_charge_input_mwh>1e-6).sum()),
      "discharge_positive_hours":int((trace.storage_discharge_to_load_mwh>1e-6).sum()),
      "soc_positive_hours":int((trace.soc_end_mwh>1e-6).sum()),
      "soc_over_95pct_hours":int((trace.soc_end_mwh>.95*e).sum()),
      "soc_over_95pct_and_curtail_hours":int(((trace.soc_end_mwh>.95*e)&(trace.unused_renewable_mwh>1e-6)).sum()),
      "charge_at_power_and_curtail_hours":int((trace.charge_at_power_limit&(trace.unused_renewable_mwh>1e-6)).sum()),
      "curtailment_mwh":float(trace.unused_renewable_mwh.sum()),
      "charge_input_mwh":float(trace.storage_charge_input_mwh.sum()),
      "discharge_to_load_mwh":float(trace.storage_discharge_to_load_mwh.sum()),
      "firm_generation_mwh":float(trace.firm_generation_mwh.sum()),
      "mean_soc_fraction":float((trace.soc_end_mwh/e).mean()),
      "negative_energy_upper_dual_count":int((dual.soc_energy_upper_marginal_usd_per_mwh<-1e-5).sum()),
      "sum_energy_upper_dual_usd_per_mwh":float(dual.soc_energy_upper_marginal_usd_per_mwh.sum()),
      "negative_charge_power_dual_count":int((dual.charge_power_upper_marginal_usd_per_mw<-1e-5).sum()),
      "negative_discharge_power_dual_count":int((dual.discharge_power_upper_marginal_usd_per_mw<-1e-5).sum()),
    }
    if not (len(trace)==len(dual)==HOURS):
        raise ValueError("Missing complete hourly original-clock traces/duals")
    if any(x[key]>HOURS for key in x if key.endswith("_hours") or key.endswith("_count")):
        raise ValueError("Invalid hourly active-set count")
    return x

def check_frozen(current,original,additional):
    old=pd.concat([pd.read_csv(original),pd.read_csv(additional)],ignore_index=True)
    old=old[old.state.eq(STATE)&old.renewable_peak_ratio.eq(RATIO)&
             old.wind_share_ac.isin(SHARES)&old.battery_duration_h.isin(DURATIONS)]
    if len(old)!=len(current)!=180:
        # explicit comparison below also catches a missing case
        pass
    if len(old)!=180 or old.duplicated(KEYS).any():
        raise ValueError("Original frozen comparison missing or duplicated 180 CO cases")
    j=current.merge(old[KEYS+["objective_illustrative_variable_usd",
                   "storage_capacity_mwh"]],on=KEYS,validate="one_to_one",
              suffixes=("","_frozen"))
    if len(j)!=180:raise ValueError("Frozen objective matched case count is incomplete")
    diff=(j.objective_illustrative_variable_usd-
          j.objective_illustrative_variable_usd_frozen).abs()
    energy_diff=(j.storage_capacity_mwh-j.storage_capacity_mwh_frozen).abs()
    if diff.max()>0.1 or energy_diff.max()>1e-6:
        raise ValueError("Mechanism-run objective/energy drift versus frozen prior model")
    return {"matched_cases":len(j),"max_objective_abs_diff_usd":float(diff.max()),
            "max_storage_capacity_diff_mwh":float(energy_diff.max())}

def run(wind_h5,pv_h5,wind_sc,pv_sc,county_shares,wind_ref,pv_ref,
        demand_h5,frozen3x3_csv,continuity_csv,out):
    output=Path(out);output.mkdir(parents=True,exist_ok=True)
    verify_official_file(Path(demand_h5))
    wind,_,tw=reaggregate_years(wind_h5,wind_sc,"wind",county_shares,wind_ref,years=WEATHER_YEARS)
    pv,_,tp=reaggregate_years(pv_h5,pv_sc,"pv",county_shares,pv_ref,years=WEATHER_YEARS)
    if not tw.equals(tp):raise ValueError("Renewable source-hour clock mismatch")
    with h5py.File(demand_h5,"r") as h:
        d=h["2030"];check_fixed_cst_native_labels(d["datetime"][:])
        times=pd.DatetimeIndex(pd.to_datetime([
            x.decode() if isinstance(x,bytes) else str(x) for x in d["datetime"][:]],utc=True))
        if not times.equals(tw):raise ValueError("Frozen demand/CF clock mismatch")
        load=np.asarray(d[STATE][:],dtype=float)
    if len(load)!=HOURS or not np.isfinite(load).all():raise ValueError("Invalid fixed demand")
    rows=[];input_rows=[];trace_files=[]
    for year in WEATHER_YEARS:
        for scheme in DESIGNS:
            w=modeled_hourly_cf(wind[(year,scheme,STATE)],HOUR)
            p=normalized_pv_ac_cf(modeled_hourly_cf(pv[(year,scheme,STATE)],HOUR))
            for share in SHARES:
                combined=share*w+(1-share)*p
                if not np.isfinite(combined).all() or (combined<0).any() or (combined>1).any():
                    raise ValueError("Bad AC combined CF")
                input_rows.append(dict(weather_year=year,state=STATE,
                    county_weight_scheme=scheme,wind_share_ac=share,
                    demand_sha256=sha(load),wind_cf_sha256=sha(w),
                    pv_cf_sha256=sha(p),mix_sha256=sha(combined)))
                for duration in DURATIONS:
                    sol,trace,duals=solve_zone(load,combined,duration,
                        renewable_peak_ratio=RATIO,battery_power_peak_ratio=POWER,
                        roundtrip_efficiency=RTE,renewable_unit_cost=5.,
                        firm_unit_cost=90.,return_trace=True,return_duals=True)
                    if sol["solver_status"]!="optimal" or sol["max_equality_residual_mwh"]>1e-5:
                        raise ValueError("Hourly LP result infeasible")
                    result=dict(weather_year=year,state=STATE,
                        county_weight_scheme=scheme,renewable_peak_ratio=RATIO,
                        wind_share_ac=share,battery_duration_h=duration,
                        objective_illustrative_variable_usd=sol["objective_illustrative_variable_usd"],
                        storage_capacity_mwh=sol["storage_capacity_mwh"],
                        max_equality_residual_mwh=sol["max_equality_residual_mwh"],
                        **audit_summary(trace,duals,sol))
                    rows.append(result)
                    if year in (2012,2023):
                        t=trace.copy()
                        for col in duals.columns:
                            if col!="local_hour_id":t[col]=duals[col].values
                        t.insert(0,"battery_duration_h",duration)
                        t.insert(0,"wind_share_ac",share)
                        t.insert(0,"county_weight_scheme",scheme)
                        t.insert(0,"state",STATE)
                        t.insert(0,"weather_year",year)
                        fname=f"CO_R2_hourly_{year}_{scheme}_wind{int(share*100)}_dur{duration}.csv.gz"
                        t.to_csv(output/fname,index=False,compression="gzip")
                        trace_files.append(fname)
        print("PAPER_S_CO_R2_HOURLY_YEAR_COMPLETED",year,len(rows),flush=True)
        pd.DataFrame(rows).to_csv(output/"partial_hourly_mechanism_summary.csv",index=False)
    frame=pd.DataFrame(rows);checks=pd.DataFrame(input_rows)
    if len(frame)!=180 or len(checks)!=90 or frame.duplicated(KEYS).any():
        raise ValueError("Incomplete R2 CO mechanism-case population")
    for col in ("demand_sha256","wind_cf_sha256","pv_cf_sha256"):
        if not (checks.groupby(["weather_year","county_weight_scheme"])[col].nunique()==1).all():
            raise ValueError(f"Original input inconsistency across 40/50/60: {col}")
    frozen=check_frozen(frame,frozen3x3_csv,continuity_csv)
    frame.to_csv(output/"CO_R2_180_hourly_SOC_curtailment_dual_case_summaries.csv",index=False)
    checks.to_csv(output/"CO_R2_90_hourly_input_array_SHA256.csv",index=False)
    frame_wide=frame.pivot(index=["weather_year","county_weight_scheme","wind_share_ac"],
                           columns="battery_duration_h",
                           values=["soc_at_upper_hours","curtailment_positive_hours",
                                   "curtailment_mwh","firm_generation_mwh",
                                   "sum_energy_upper_dual_usd_per_mwh"])
    frame_wide.columns=["_".join(map(str,col)) for col in frame_wide.columns]
    frame_wide.reset_index().to_csv(output/"CO_R2_90_duration_active_set_differences.csv",index=False)
    manifest=dict(status="SOURCE_VERIFIED_HOURLY_MECHANISM_CANDIDATE",
                  original_frozen_objective_gate=frozen,
                  new_lp_resolves=180,source_input_hash_rows=90,
                  retained_full_year_trace_files=len(trace_files),
                  only_trace_weather_years=[2012,2023],
                  hourly_trace_source_hours=HOURS,
                  soc_schedule_may_be_LP_degenerate=True,
                  shadow_prices_are_basis_dependent=True,
                  charging_saturation_causality_established=False,
                  original_design_grid_modified=False,paper_C2_modified=False)
    (output/"CO_R2_hourly_mechanism_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    (output/"partial_hourly_mechanism_summary.csv").unlink(missing_ok=True)
    print("PAPER_S_CO_R2_180_HOURLY_MECHANISM_SUCCESS",json.dumps(manifest),flush=True)

def main():
    q=argparse.ArgumentParser()
    for name in ("wind_h5","pv_h5","wind_sc","pv_sc","county_shares",
                 "wind_ref","pv_ref","demand_h5","frozen3x3_csv","continuity_csv"):
        q.add_argument("--"+name.replace("_","-"),type=Path,required=True)
    q.add_argument("--out",type=Path,required=True)
    x=q.parse_args()
    run(x.wind_h5,x.pv_h5,x.wind_sc,x.pv_sc,x.county_shares,
        x.wind_ref,x.pv_ref,x.demand_h5,x.frozen3x3_csv,x.continuity_csv,x.out)

if __name__=="__main__":main()
