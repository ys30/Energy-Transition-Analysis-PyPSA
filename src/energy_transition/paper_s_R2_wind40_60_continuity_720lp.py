"""Independent R=2.0 wind AC share 40%/60% LP mechanism continuity check.

Uses exactly the same original 2012-clock fixed-2030 demand, county-aggregated
15-weather-year wind/PV, input source hashes and physical LP parameters as
the frozen Paper S 3x3 study. New solves only. No baseline overwrite.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import h5py,numpy as np,pandas as pd
from energy_transition.reeds2022_all_weather_year_720lp import WEATHER_YEARS
from energy_transition.reeds2022_four_weather_year_siting_lp import (
    reaggregate_years,STATES,DESIGNS,DURATIONS,POWER,RTE,HOURS)
from energy_transition.reeds2022_county_full_state_lp import modeled_hourly_cf
from energy_transition.reeds2022_county_ac_normalized_2030 import normalized_pv_ac_cf
from energy_transition.reeds_2022_clocked_demand_branch import (
    verify_official_file,check_fixed_cst_native_labels)
from energy_transition.efs_cyclic_storage_lp import solve_zone

RATIO=2.0
NEW_WIND_SHARES=(.40,.60)
HOUR="trapezoid_with_first_endpoint"
KEYS=("weather_year","state","county_weight_scheme","wind_share_ac","battery_duration_h")

def digest_numeric(a):
    x=np.asarray(a,dtype="<f8")
    return hashlib.sha256(x.tobytes()).hexdigest()

def run(wind_h5,pv_h5,wind_sc,pv_sc,county_shares,wind_ref,pv_ref,demand_h5,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    verify_official_file(Path(demand_h5))
    wind,_,tw=reaggregate_years(
        wind_h5,wind_sc,"wind",county_shares,wind_ref,years=WEATHER_YEARS)
    pv,_,tp=reaggregate_years(
        pv_h5,pv_sc,"pv",county_shares,pv_ref,years=WEATHER_YEARS)
    if not tw.equals(tp):raise ValueError("Original wind/pv source calendar mismatch")
    rows=[];audit=[];trip=[]
    with h5py.File(demand_h5,"r") as h5:
        g=h5["2030"]
        check_fixed_cst_native_labels(g["datetime"][:])
        dtime=pd.DatetimeIndex(pd.to_datetime([
            v.decode() if isinstance(v,bytes) else str(v)
            for v in g["datetime"][:]],utc=True))
        if not dtime.equals(tw):raise ValueError("Original frozen demand source clock mismatch")
        for state in STATES:
            demand=np.asarray(g[state][:],dtype=float)
            if demand.shape!=(HOURS,) or not np.isfinite(demand).all() or (demand<0).any():
                raise ValueError("Missing or invalid source 2030 fixed demand")
            demand_hash=digest_numeric(demand)
            for year in WEATHER_YEARS:
                for scheme in DESIGNS:
                    w=modeled_hourly_cf(wind[(year,scheme,state)],HOUR)
                    p=normalized_pv_ac_cf(modeled_hourly_cf(pv[(year,scheme,state)],HOUR))
                    if w.shape!=demand.shape or p.shape!=demand.shape:
                        raise ValueError("Original input length drift")
                    for share in NEW_WIND_SHARES:
                        combined=share*w+(1.-share)*p
                        if not np.isfinite(combined).all() or (combined<0).any() or (combined>1).any():
                            raise ValueError("Invalid combined source AC CF")
                        audit.append(dict(state=state,weather_year=year,
                            county_weight_scheme=scheme,wind_share_ac=share,
                            source_hours=len(combined),demand_sha256=demand_hash,
                            wind_input_sha256=digest_numeric(w),
                            pv_input_sha256=digest_numeric(p),
                            combined_input_sha256=digest_numeric(combined),
                            demand_annual_mwh=demand.sum(),
                            wind_cf_mean=w.mean(),pv_cf_mean=p.mean(),
                            combined_cf_mean=combined.mean()))
                        local={}
                        for duration in DURATIONS:
                            sol=solve_zone(demand,combined,duration,
                                renewable_peak_ratio=RATIO,
                                battery_power_peak_ratio=POWER if duration else 0.,
                                roundtrip_efficiency=RTE,
                                renewable_unit_cost=5.,firm_unit_cost=90.)
                            if sol["solver_status"]!="optimal" or sol["max_equality_residual_mwh"]>1e-5:
                                raise ValueError("LP solver failure")
                            rows.append(dict(weather_year=year,state=state,
                                county_weight_scheme=scheme,renewable_peak_ratio=RATIO,
                                wind_share_ac=share,battery_duration_h=duration,**sol))
                            local[duration]=sol
                        denom=(local[8]["storage_capacity_mwh"]-
                               local[4]["storage_capacity_mwh"])*1000
                        if denom<=0:raise ValueError("Invalid 4-to-8h storage size")
                        value=(local[4]["objective_illustrative_variable_usd"]-
                               local[8]["objective_illustrative_variable_usd"])/denom
                        trip.append(dict(weather_year=year,state=state,
                            county_weight_scheme=scheme,renewable_peak_ratio=RATIO,
                            wind_share_ac=share,
                            marginal_4to8_usd_added_kwh_year=value,
                            curtailment_4h_mwh=local[4]["unused_renewable_mwh"],
                            curtailment_8h_mwh=local[8]["unused_renewable_mwh"],
                            firm_generation_4h_mwh=local[4]["firm_generation_mwh"],
                            firm_generation_8h_mwh=local[8]["firm_generation_mwh"]))
            print("PAPER_S_40_60_SHARE_STATE_DONE",state,len(rows),flush=True)
            pd.DataFrame(rows).to_csv(out/"partial_new_lp.csv",index=False)
    a=pd.DataFrame(rows);t=pd.DataFrame(trip);checks=pd.DataFrame(audit)
    if len(a)!=720 or len(t)!=240 or len(checks)!=240 or a.duplicated(KEYS).any():
        raise ValueError("Missing or duplicate 40/60 source LP cases")
    x=t.pivot(index=["weather_year","state","renewable_peak_ratio","wind_share_ac"],
              columns="county_weight_scheme",values="marginal_4to8_usd_added_kwh_year")
    if len(x)!=120 or x.isna().any().any():raise ValueError("Incomplete siting pair")
    paired=x.reset_index()
    paired["siting_effect_eia_minus_potential"]=paired[DESIGNS[1]]-paired[DESIGNS[0]]
    summary=(paired.groupby(["state","renewable_peak_ratio","wind_share_ac"])
             .agg(weather_years=("weather_year","size"),
                  median_siting_effect=("siting_effect_eia_minus_potential","median"),
                  min_siting_effect=("siting_effect_eia_minus_potential","min"),
                  max_siting_effect=("siting_effect_eia_minus_potential","max"),
                  positive_weather_years=("siting_effect_eia_minus_potential",
                                          lambda z:int((z>0).sum()))).reset_index())
    if len(summary)!=8 or not summary.weather_years.eq(15).all():
        raise ValueError("Bad 8-cell R2 continuity summary")
    a.to_csv(out/"paper_s_R2_wind40_60_720_NEW_lp.csv",index=False)
    t.to_csv(out/"paper_s_R2_wind40_60_240_duration_values.csv",index=False)
    checks.to_csv(out/"paper_s_R2_wind40_60_240_input_sha256.csv",index=False)
    paired.to_csv(out/"paper_s_R2_wind40_60_120_paired_effects.csv",index=False)
    summary.to_csv(out/"paper_s_R2_wind40_60_8_cell_summary.csv",index=False)
    (out/"partial_new_lp.csv").unlink(missing_ok=True)
    manifest=dict(status="R2_WIND_SHARE_40_60_SOURCE_LP_NEW_SOLVES",
       newly_solved_lp_count=len(a),new_duration_triplets=len(t),
       paired_weather_year_effects=len(paired),state_share_summary_cells=len(summary),
       source_hours=HOURS,fixed_2030_demand=True,source_clock_hour_method=HOUR,
       historical_input_2012_reference=True,original_3x3_LP_changed=False,
       new_historical_weather_years=False,mechanism_proven=False,
       paper_C2_changed=False)
    (out/"paper_s_R2_wind40_60_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("PAPER_S_R2_40_60_720_LP_SUCCESS",json.dumps(manifest),flush=True)

def main():
    q=argparse.ArgumentParser()
    for x in ("wind_h5","pv_h5","wind_sc","pv_sc","county_shares",
              "wind_ref","pv_ref","demand_h5"):
        q.add_argument("--"+x.replace("_","-"),type=Path,required=True)
    q.add_argument("--out",type=Path,required=True)
    a=q.parse_args()
    run(a.wind_h5,a.pv_h5,a.wind_sc,a.pv_sc,a.county_shares,
        a.wind_ref,a.pv_ref,a.demand_h5,a.out)

if __name__=="__main__":main()
