"""ReEDS2022 county-native 2030 storage dimension and resource-mix experiment.

Four source states x 3 renewable deployment ratios x 3 wind MW shares x
(1 no storage + 2 storage power ratios x 2 durations) = 180 HiGHS LPs.
Reference meteorology is publisher-authenticated 2012 8760-hour
instantaneous CF; trapezoid plus endpoint first-hour approximation is a
declared numerical assumption, NOT certified physical interval generation.
The source resource potential is NEVER treated as deployed nameplate MW.
No network, capex, capacity credit, adequacy or observed grid claims.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from energy_transition.efs_cyclic_storage_lp import solve_zone
from energy_transition.reeds2022_county_full_state_lp import (
    modeled_hourly_cf,HOURS,MODES,
)
from energy_transition.reeds2022_joint_resource_shape import STATES,read_native
from energy_transition.reeds_2022_clocked_demand_branch import (
    verify_official_file,check_fixed_cst_native_labels,
)

MODEL_YEAR=2030
RATIOS=(0.9,1.5,2.0)
WIND_MIX=(0.25,0.50,0.75)
POWER_RATIOS=(0.10,0.25)
DURATIONS=(4,8)
MODE="trapezoid_with_first_endpoint"
EFFICIENCY=.9
ENERGY_ANNUITY_USD_PER_KWH_YEAR=(0.,10.,25.)


def build_paired_table(frame):
    keys=["state","demand_model_year","renewable_peak_ratio","wind_share_installed_mw"]
    no=frame[frame.battery_duration_h.eq(0)].set_index(keys)
    yes=frame[frame.battery_duration_h.gt(0)].copy()
    if len(no)!=36 or len(yes)!=144 or no.index.has_duplicates:
        raise ValueError("Incomplete 36 no-storage and 144 storage scenarios")
    if not set(yes.set_index(keys).index)==set(no.index):
        raise ValueError("Storage experiment has unmatched reference")
    mapped=no["objective_illustrative_variable_usd"]
    yes["no_storage_variable_usd"]=yes.set_index(keys).index.map(mapped)
    yes["operating_savings_usd_per_reference_year"]=(
        yes.no_storage_variable_usd-yes.objective_illustrative_variable_usd)
    if (yes.operating_savings_usd_per_reference_year<-.10).any():
        raise ValueError("Battery improves feasible set but worsened optimum")
    yes["battery_power_kw"]=yes.storage_power_mw*1000
    yes["battery_energy_kwh"]=yes.storage_capacity_mwh*1000
    yes["max_combined_battery_annuity_usd_per_year"]=yes.operating_savings_usd_per_reference_year
    yes["break_even_power_only_usd_per_kw_year"]=(
        yes.operating_savings_usd_per_reference_year/yes.battery_power_kw)
    yes["break_even_energy_only_usd_per_kwh_year"]=(
        yes.operating_savings_usd_per_reference_year/yes.battery_energy_kwh)
    for annuity in ENERGY_ANNUITY_USD_PER_KWH_YEAR:
        tag=str(int(annuity))
        yes[f"remaining_power_annuity_usd_per_kw_year_if_energy_{tag}"] = (
            yes.operating_savings_usd_per_reference_year -
            annuity*yes.battery_energy_kwh)/yes.battery_power_kw
    if not np.isfinite(yes.select_dtypes(include="number")).all().all():
        raise ValueError("Invalid non-finite investment hurdle")
    return yes


def run(demand_h5,wind_csv,pv_csv,out,*,states=STATES):
    import h5py
    verify_official_file(Path(demand_h5))
    wind,t_w=read_native(wind_csv,"wind")
    pv,t_p=read_native(pv_csv,"pv")
    if not t_w.equals(t_p):
        raise ValueError("Native wind/PV publisher clocks differ")
    with h5py.File(demand_h5,"r") as f:
        group=f[str(MODEL_YEAR)]
        check_fixed_cst_native_labels(group["datetime"][:])
        native=pd.DatetimeIndex(pd.to_datetime(
            [v.decode() if isinstance(v,bytes) else str(v) for v in group["datetime"][:]],utc=True))
        if not native.equals(t_w):
            raise ValueError("Original 2012 weather and demand labels disagree")
        rows=[]
        for state in states:
            load=np.asarray(group[state][:],dtype=float)
            if load.shape!=(HOURS,) or not np.isfinite(load).all() or (load<0).any():
                raise ValueError("Source demand state shape invalid")
            w=modeled_hourly_cf(wind[state],MODE)
            p=modeled_hourly_cf(pv[state],MODE)
            peak=float(load.max())
            for ratio in RATIOS:
                for wind_share in WIND_MIX:
                    cf=wind_share*w+(1-wind_share)*p
                    combos=[(0,0.)]+[(duration,power) for duration in DURATIONS for power in POWER_RATIOS]
                    for duration,power in combos:
                        opt=solve_zone(
                            load,cf,duration,renewable_peak_ratio=ratio,
                            battery_power_peak_ratio=power if duration else 0.,
                            roundtrip_efficiency=EFFICIENCY)
                        rows.append({
                            "experiment":"source-weather assumed-buildout 2030 power-duration-mix sensitivity",
                            "state":state,"demand_model_year":MODEL_YEAR,
                            "reference_weather_year":2012,
                            "hour_approximation":MODE,
                            "renewable_peak_ratio":ratio,
                            "wind_share_installed_mw":wind_share,
                            "battery_power_peak_ratio":power,
                            "battery_duration_h":duration,
                            "renewable_installed_mw_hypothetical":peak*ratio,
                            "wind_installed_mw_hypothetical":peak*ratio*wind_share,
                            "pv_installed_mw_dc_hypothetical":peak*ratio*(1-wind_share),
                            "source_resource_potential_is_not_installed_MW":True,
                            "battery_annuity_not_in_LP_objective":True,
                            "physically_calibrated_grid":False,
                            **opt,
                        })
    frame=pd.DataFrame(rows)
    if len(frame)!=len(STATES)*len(RATIOS)*len(WIND_MIX)*5:
        raise ValueError("Wrong prespecified 180 LP matrix")
    if not frame.solver_status.eq("optimal").all() or frame.max_equality_residual_mwh.max()>1e-5:
        raise ValueError("HiGHS optimum or primal balance not verified")
    pairs=build_paired_table(frame)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    frame.to_csv(out/"paper_s_reeds2022_2030_180_mix_power_duration_LPs.csv",index=False,float_format="%.12g")
    pairs.to_csv(out/"paper_s_reeds2022_2030_144_storage_annuity_hurdles.csv",index=False,float_format="%.12g")
    manifest={
        "status":"COUNTY_SOURCE_2030_REFERENCE_180_MIX_POWER_DURATION_LPS_OPTIMAL",
        "state_count":len(STATES),"original_LPs":len(frame),
        "no_battery_reference_count":36,"storage_sensitivity_count":len(pairs),
        "weather_year":2012,"demand_model_year":2030,
        "prespecified_renewable_deployment_ratios":RATIOS,
        "wind_share_options":WIND_MIX,
        "battery_power_peak_options":POWER_RATIOS,
        "battery_duration_options":DURATIONS,
        "weather_hour_average_is_numerical_approximation":True,
        "battery_fixed_capex_operations_and_financing_not_modeled":True,
        "break_even_values_are_upper_bounds_not_actual_IRR":True,
        "energy_annuities_usd_per_kwh_year":ENERGY_ANNUITY_USD_PER_KWH_YEAR,
        "weather_source_artifact_run":42962740548,
        "demand_publisher_MD5_checked":True,
        "physical_grid_or_reliability_estimate":False,
        "legacy_EFS2020_model_unchanged":True,
    }
    (out/"paper_s_reeds2022_2030_180_mix_power_duration_manifest.json").write_text(
        json.dumps(manifest,indent=2)+"\n")
    subset=pairs[(pairs.renewable_peak_ratio==1.5)&
                 (pairs.wind_share_installed_mw==.5)&
                 (pairs.battery_duration_h==4)&
                 (pairs.battery_power_peak_ratio==.25)]
    print(subset[["state","operating_savings_usd_per_reference_year",
                   "storage_power_mw","storage_capacity_mwh",
                   "break_even_power_only_usd_per_kw_year"]].to_string(index=False))
    print("REEDS2022_180_SOURCE_LP_STORAGE_MIX_DURATION_SENSITIVITY_PASSED")
    return frame,pairs


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--demand-h5",type=Path,required=True)
    p.add_argument("--wind-csv",type=Path,required=True)
    p.add_argument("--pv-csv",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    run(args.demand_h5,args.wind_csv,args.pv_csv,args.out)


if __name__=="__main__":
    main()
