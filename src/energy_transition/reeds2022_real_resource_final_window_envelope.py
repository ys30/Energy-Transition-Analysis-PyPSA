"""Final limited near-optimal annual-versus-168h envelope with genuine 2012 ReEDS CF.

Different 2022 state-level source system, NOT original 2020 EFS p-zone.
Exactly 2030, AZ CO ID WY, fixed source hour 4001:4168 and a prespecified
trapezoidal instantaneous-CF-to-hourly-average model assumption.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from .reeds2022_real_wind_pv_state_storage_lp import (
 STATES,read_weighted_source_cf,strict_pure_ba_crosswalk,WIND_SHARE,ILR_PV
)
from .reeds2022_real_resource_intake import CROSSWALK_MD5,require_md5,decode
from .reeds_2022_clocked_demand_branch import verify_official_file,check_fixed_cst_native_labels
from .efs_cyclic_storage_lp import solve_zone
from .paper_s_soc_optimal_envelope import RELATIVE_BUDGET,MINIMUM_BUDGET_USD,COST_NUMERICAL_SLACK_USD

FIRST,LAST=4001,4168
def validate_controls(states=STATES,window=(FIRST,LAST)):
 if tuple(states)!=("AZ","CO","ID","WY") or window!=(4001,4168):
  raise ValueError("Frozen real-source window/source group contract changed")
 if LAST-FIRST+1!=168:raise ValueError("Wrong source-hour window length")
 return True

def evaluate(demand_path,wind_path,pv_path,wind_sc,pv_sc,crosswalk,pilot_csv,out):
 import h5py
 validate_controls()
 verify_official_file(demand_path);require_md5(crosswalk,CROSSWALK_MD5)
 pure,coverage=strict_pure_ba_crosswalk(pd.read_csv(crosswalk,dtype={"FIPS":str}))
 wind,winfo,wclock=read_weighted_source_cf(wind_path,wind_sc,"wind",pure)
 solar,sinfo,pclock=read_weighted_source_cf(pv_path,pv_sc,"pv",pure)
 if (wclock["2012_first"],wclock["2012_last"])!=(pclock["2012_first"],pclock["2012_last"]):
  raise ValueError("Wind/PV original physical time keys mismatch")
 pilot=pd.read_csv(pilot_csv)
 results=[];envelopes=[]
 with h5py.File(demand_path) as f:
  gp=f["2030"]
  check_fixed_cst_native_labels(gp["datetime"][:])
  demand_times=pd.to_datetime(decode(gp["datetime"][:]),utc=True)
  if demand_times[0]!=pd.Timestamp(wclock["2012_first"]).tz_convert("UTC") or demand_times[-1]!=pd.Timestamp(wclock["2012_last"]).tz_convert("UTC"):
   raise ValueError("Verified demand and wind/PV 2012 native timestamps mismatch")
  mask=np.zeros(8760);mask[FIRST-1:LAST]=1.
  for state in STATES:
   d=np.asarray(gp[state][:],dtype=float)
   cf=WIND_SHARE*wind[state]["trapezoidal_previous_instant"]+(1.-WIND_SHARE)*solar[state]["trapezoidal_previous_instant"]
   m0,tr0=solve_zone(d,np.clip(cf,0,1),4,return_trace=True,renewable_peak_ratio=.9)
   cost=float(m0["objective_illustrative_variable_usd"])
   historical=pilot[(pilot.state==state)&(pilot.hour_approximation=="trapezoidal_previous_instant")&
     (pilot.battery_duration_h==4)]
   if len(historical)!=1 or abs(cost-float(historical.objective_illustrative_variable_usd.iloc[0]))>.05:
    raise ValueError("New primary 4h original LP result fails source-based archive reconciliation")
   tolerance=max(MINIMUM_BUDGET_USD,RELATIVE_BUDGET*cost)
   solves={"baseline":(m0,tr0)}
   for ext in ("min","max"):
    solves["annual_"+ext]=solve_zone(d,np.clip(cf,0,1),4,return_trace=True,
      discharge_extremum=ext,discharge_hour_weights=np.ones(8760),
      original_cost_ceiling_usd=cost+tolerance,renewable_peak_ratio=.9)
    solves["window_"+ext]=solve_zone(d,np.clip(cf,0,1),4,return_trace=True,
      discharge_extremum=ext,discharge_hour_weights=mask,
      original_cost_ceiling_usd=cost+tolerance,renewable_peak_ratio=.9)
   bymode={}
   for mode,(sumry,trace) in solves.items():
    annual=float(trace.storage_discharge_to_load_mwh.sum())
    window=float(trace.storage_discharge_to_load_mwh.to_numpy()@mask)
    value=float(sumry["objective_illustrative_variable_usd"])
    if value>cost+tolerance+COST_NUMERICAL_SLACK_USD or value<cost-max(.03,tolerance):
     raise ValueError("Original cost cap violation")
    if sumry["max_equality_residual_mwh"]>1e-5 or abs(sumry["storage_terminal_soc_mwh"])>1e-5:
     raise ValueError("Source hourly primal/cyclic SOC validation failed")
    bymode[mode]=(annual,window)
    results.append({"state":state,"source_release":"ReEDS2022_EFS_REFERENCE",
      "model_year":2030,"weather_year":2012,"weather_hour_integration":"trapezoidal_previous_instant",
      "label":"source hour 4001–4168, not original EFS2020 LocalHourID",
      "solution":mode,"annual_discharge_mwh":annual,"window_discharge_mwh":window,
      "original_cost_usd":value,"baseline_optimal_original_cost_usd":cost,
      "positive_original_cost_tolerance_usd":tolerance,
      "max_hourly_equality_residual_mwh":sumry["max_equality_residual_mwh"],
      "terminal_soc_mwh":sumry["storage_terminal_soc_mwh"]})
   annual_low= bymode["annual_min"][0]
   annual_high=bymode["annual_max"][0]
   window_low=bymode["window_min"][1]
   window_high=bymode["window_max"][1]
   if annual_low> bymode["baseline"][0]+.04 or bymode["baseline"][0]>annual_high+.04 or window_low>bymode["baseline"][1]+.04 or bymode["baseline"][1]>window_high+.04:
    raise ValueError("Original primary optimal schedule not in computed discharge intervals")
   envelopes.append({"state":state,"model_year":2030,"weather_year":2012,
      "annual_original_baseline_mwh":bymode["baseline"][0],
      "annual_min_mwh":annual_low,"annual_max_mwh":annual_high,
      "annual_width_mwh":annual_high-annual_low,
      "window_first_hour":FIRST,"window_last_hour":LAST,
      "window_original_baseline_mwh":bymode["baseline"][1],
      "window_min_mwh":window_low,"window_max_mwh":window_high,
      "window_width_mwh":window_high-window_low,
      "window_width_pct_original_window_baseline":100*(window_high-window_low)/bymode["baseline"][1] if bymode["baseline"][1]>0 else None,
      "positive_original_cost_tolerance_usd":tolerance,
      "exact_optimal_face_certified":False,
      "physical_resource_data_source_verified":True,
      "interval_energy_trapezoid_assumed":True,
      "model_is_network_constrained":False})
 out.mkdir(parents=True,exist_ok=True)
 pd.DataFrame(envelopes).to_csv(out/"paper_s_reeds2022_real_resource_four_state_annual_vs_window_envelopes.csv",index=False,float_format="%.12g")
 pd.DataFrame(results).to_csv(out/"paper_s_reeds2022_real_resource_twenty_source_LP_schedules.csv",index=False,float_format="%.12g")
 (out/"paper_s_reeds2022_source_real_window_manifest.json").write_text(json.dumps({
  "status":"REAL_REEDS2022_SOURCE_2030_FOUR_STATES_ANNUAL_VS_168H_WINDOW_CERTIFIED",
  "state_count":4,"original_LP_solves":20,
  "prespecified_original_source_window":[FIRST,LAST],
  "source_clock":"ReEDS2022 2012 CST UTC-06, not old EFS2020 source",
  "physical_hourly_weather_source_authenticated":True,
  "wind_pv_point_to_hour_average_numerically_assumed":True,
  "sampled_BA_county_coverage":coverage.to_dict("records"),
  "installed_wind_solar_capacities_are_hypothetical":True,
  "near_optimal_cost_tolerance_positive":True,
  "real_network_OPF_or_reliability_certified":False
 },indent=2)+"\n")
 print(pd.DataFrame(envelopes).to_string(index=False))
 print("REEDS2022_AUTHENTIC_WIND_PV_ANNUAL_VS_168_WINDOW_ENVELOPES_PASS")
 return pd.DataFrame(envelopes)

def main():
 p=argparse.ArgumentParser()
 for key in ("demand_h5","wind_h5","pv_h5","wind_sc","pv_sc","county2zone","pilot_csv"):
  p.add_argument("--"+key.replace("_","-"),required=True,type=Path)
 p.add_argument("--out",required=True,type=Path)
 x=p.parse_args()
 evaluate(x.demand_h5,x.wind_h5,x.pv_h5,x.wind_sc,x.pv_sc,x.county2zone,x.pilot_csv,x.out)
if __name__=="__main__":main()
