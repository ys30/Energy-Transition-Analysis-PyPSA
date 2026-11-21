"""AC-nameplate-consistent ReEDS2022 county-source 2030 battery sensitivity.

ReEDS utility PV raw CF denominator is MW_DC_array; ILR 1.34 converts
to MW_AC_grid / MW_AC_nameplate. The scenario ratio and wind shares
here are BOTH defined on common AC-nameplate MW, unlike the archived
original source-denominator sensitivity. Never rescale the raw source
resource series in place; only change the scenario unit convention.
The publisher original instantaneous CF is approximated to an hourly
interval using a prespecified noncyclic trapezoid with first-hour
endpoint fallback. The small CF>1 clipping tolerance is solely for
published decimal rounding (raw max 0.7463*1.34=1.000042).
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from energy_transition.efs_cyclic_storage_lp import solve_zone
from energy_transition.reeds2022_joint_resource_shape import STATES,read_native
from energy_transition.reeds2022_county_full_state_lp import modeled_hourly_cf,HOURS
from energy_transition.reeds2022_county_storage_mix_duration_2030 import (
    MODEL_YEAR,RATIOS,WIND_MIX,POWER_RATIOS,DURATIONS,MODE,EFFICIENCY,
    build_paired_table,
)
from energy_transition.reeds_2022_clocked_demand_branch import (
    verify_official_file,check_fixed_cst_native_labels
)

ILR=1.34
ROUNDING_EXCESS_TOL=1.0e-4
DESIGN_FIELDS=("state","demand_model_year","renewable_peak_ratio",
               "wind_share_installed_mw","battery_duration_h",
               "battery_power_peak_ratio")

def normalized_pv_ac_cf(original_pv_cf, *, ilr=ILR):
    """AC CF = (MW_grid_AC/MW_array_DC) * (MW_array_DC/MW_nameplate_AC)."""
    x=np.asarray(original_pv_cf,dtype=float)
    if x.shape!=(HOURS,) or not np.isfinite(x).all() or np.any(x<0) or np.any(x>1):
        raise ValueError("Invalid publisher original PV DC-denominated CF")
    if not np.isfinite(ilr) or ilr<=0:
        raise ValueError("Invalid PV DC-to-AC ILR")
    converted=x*ilr
    if converted.max()>1+ROUNDING_EXCESS_TOL:
        raise ValueError("Unphysical PV AC-normalized CF above documented rounding tolerance")
    return np.clip(converted,0.,1.)

def compare_source_basis(ac, original):
    a=ac.set_index(list(DESIGN_FIELDS)).sort_index()
    b=original.set_index(list(DESIGN_FIELDS)).sort_index()
    if len(a)!=180 or len(b)!=180 or a.index.has_duplicates or b.index.has_duplicates or not a.index.equals(b.index):
        raise ValueError("Missing source-AC paired 180-scenario model comparison")
    results=pd.DataFrame(index=a.index)
    for suffix,d in (("ac",a),("legacy_source_denominator",b)):
        results[f"annual_objective_usd_{suffix}"]=d.objective_illustrative_variable_usd
        results[f"curtailment_mwh_{suffix}"]=d.unused_renewable_mwh
        results[f"firm_mwh_{suffix}"]=d.firm_generation_mwh
    results["ac_minus_legacy_variable_objective_usd"]=(
        results.annual_objective_usd_ac-results.annual_objective_usd_legacy_source_denominator)
    return results.reset_index()

def run(demand_h5,wind_csv,pv_csv,original_180_csv,out):
    import h5py
    verify_official_file(Path(demand_h5))
    w,tw=read_native(wind_csv,"wind")
    p,tp=read_native(pv_csv,"pv")
    if not tw.equals(tp):raise ValueError("Original weather wind and PV CST timestamps differ")
    original=pd.read_csv(original_180_csv)
    rows=[]
    with h5py.File(demand_h5,"r") as source:
        group=source[str(MODEL_YEAR)]
        check_fixed_cst_native_labels(group["datetime"][:])
        native=pd.DatetimeIndex(pd.to_datetime(
            [v.decode() if isinstance(v,bytes) else str(v) for v in group["datetime"][:]],
            utc=True))
        if not native.equals(tw):raise ValueError("Demand/meteorology publisher source timestamps differ")
        for state in STATES:
            load=np.asarray(group[state][:],dtype=float)
            if load.shape!=(HOURS,) or not np.isfinite(load).all() or (load<0).any():
                raise ValueError("Invalid original demand array")
            peak=float(load.max())
            wind_ac=modeled_hourly_cf(w[state],MODE)
            pv_ac=normalized_pv_ac_cf(modeled_hourly_cf(p[state],MODE))
            for ratio in RATIOS:
                for wind_share in WIND_MIX:
                    cf=wind_share*wind_ac+(1-wind_share)*pv_ac
                    if cf.min() <0 or cf.max()>1:raise ValueError("Invalid AC normalized mix CF")
                    alternatives=[(0,0.)]+[(duration,power)
                         for duration in DURATIONS for power in POWER_RATIOS]
                    for duration,power in alternatives:
                        opt=solve_zone(load,cf,duration,renewable_peak_ratio=ratio,
                            battery_power_peak_ratio=power if duration else 0.,
                            roundtrip_efficiency=EFFICIENCY)
                        rows.append({
                          "experiment":"2030 fixed total AC nameplate and wind AC MW mix",
                          "state":state,"demand_model_year":MODEL_YEAR,
                          "reference_weather_year":2012,
                          "hour_approximation":MODE,
                          "renewable_peak_ratio":ratio,
                          "wind_share_installed_mw":wind_share,
                          "battery_power_peak_ratio":power,
                          "battery_duration_h":duration,
                          "total_renewable_installed_mw_ac_hypothetical":peak*ratio,
                          "wind_installed_mw_ac_hypothetical":peak*ratio*wind_share,
                          "pv_inverter_installed_mw_ac_hypothetical":peak*ratio*(1-wind_share),
                          "pv_array_installed_mw_dc_hypothetical":peak*ratio*(1-wind_share)*ILR,
                          "pv_inverter_loading_ratio":ILR,
                          "pv_cf_source_MW_grid_ac_per_MW_array_dc":True,
                          "pv_capacity_to_mwac_normalized":True,
                          "developable_potential_is_not_actual_buildout":True,
                          "actual_hour_ending_generation_energy_certified":False,
                          "actual_network_dispatch_certified":False,
                          **opt})
    frame=pd.DataFrame(rows)
    if len(frame)!=180 or not frame.solver_status.eq("optimal").all() or frame.max_equality_residual_mwh.max()>1e-5:
        raise ValueError("180 AC-consistent LPs not all optimal or balanced")
    pairs=build_paired_table(frame)
    old=compare_source_basis(frame,original)
    if len(pairs)!=144 or len(old)!=180:raise ValueError("Incomplete original matched scenarios")
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    frame.to_csv(out/"paper_s_reeds2022_2030_ac_normalized_180_LP.csv",index=False,float_format="%.12g")
    pairs.to_csv(out/"paper_s_reeds2022_2030_ac_normalized_144_storage_hurdles.csv",index=False,float_format="%.12g")
    old.to_csv(out/"paper_s_reeds2022_2030_ac_vs_original_180_matched_scenarios.csv",index=False,float_format="%.12g")
    report={
       "status":"REEDS2022_AC_NORMALIZED_PV_180_LP_EXPLICIT_SOURCE_UNITS",
       "reeds_pv_source_zenodo_record":"https://zenodo.org/records/18407660",
       "source_weather_cf_job":42962740548,
       "original_heterogeneous_nameplate_lp_job":43051615043,
       "pv_source_ac_grid_per_dc_array":True,"pv_ILR":ILR,
       "common_AC_nameplate_total_and_wind_share":True,
       "original_pv_source_profiles_unchanged":True,
       "pv_ac_normalization_done_once":True,
       "tiny_publisher_decimal_rounding_clip_tolerance":ROUNDING_EXCESS_TOL,
       "LPs":len(frame),"storage_pairs":len(pairs),"source_basis_matches":len(old),
       "installed_capacity_real_fleet":False,
       "publisher_hourly_integral_certified":False,
       "battery_capex_in_model":False,
       "electric_network_reliability_certified":False,
       "old_EFS2020_study_modified":False}
    (out/"paper_s_reeds2022_2030_ac_normalized_manifest.json").write_text(json.dumps(report,indent=2)+"\n")
    print(pairs.loc[(pairs.renewable_peak_ratio==1.5)&
        (pairs.wind_share_installed_mw==.5)&(pairs.battery_duration_h==4)&
        (pairs.battery_power_peak_ratio==.25),
        ["state","operating_savings_usd_per_reference_year",
         "break_even_power_only_usd_per_kw_year"]].to_string(index=False))
    print("REEDS2022_AC_NORMALIZED_180_LP_AND_144_PAIRS_PASS")
    return frame,pairs,old

def main():
    a=argparse.ArgumentParser()
    for name in ("demand_h5","wind_csv","pv_csv","original_180_csv"):
        a.add_argument("--"+name.replace("_","-"),type=Path,required=True)
    a.add_argument("--out",type=Path,required=True)
    x=a.parse_args()
    run(x.demand_h5,x.wind_csv,x.pv_csv,x.original_180_csv,x.out)

if __name__=="__main__":
    main()
