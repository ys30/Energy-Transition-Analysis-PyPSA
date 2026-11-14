"""Paper S county-native four-state ReEDS2022 2012 resource-shape LP scenarios.

Uses authenticated publisher original county-class resource-weighted CF
from Actions 42962740548 and separately authenticated ReEDS2022 demand H5.
The renewable MW deployment is a prespecified hypothetical scale, not the
developable potential nor a measured/planned installed fleet. Hourly energy
is approximated using point-sampling and trapezoid sensitivity. Trapezoid
first hour uses the end-point value (boundary approximation, not cyclic wrap).
No physical network or adequacy claims follow from this zonal LP.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
from energy_transition.efs_cyclic_storage_lp import solve_zone
from energy_transition.reeds_2022_clocked_demand_branch import (
    check_fixed_cst_native_labels, verify_official_file,
)
from energy_transition.reeds2022_joint_resource_shape import read_native, STATES

YEARS=(2030,2040,2050)
MODES=("end_instant_hold","trapezoid_with_first_endpoint")
DURATIONS=(0,4)
WIND_FRACTION=0.5
RENEWABLE_PEAK_RATIO=0.9
HOURS=8760


def modeled_hourly_cf(source_cf, mode):
    x=np.asarray(source_cf,dtype=float)
    if x.shape!=(HOURS,) or not np.isfinite(x).all() or (x<0).any() or (x>1).any():
        raise ValueError("Invalid authenticated 2012 source instantaneous CF")
    if mode=="end_instant_hold":
        return x.copy()
    if mode=="trapezoid_with_first_endpoint":
        # The archived county-only source-derived data start at 2012 hour 0.
        # No unsupported last-hour-to-first-hour cyclic boundary is used.
        return np.r_[x[0],(x[:-1]+x[1:])/2]
    raise ValueError("Unknown prespecified physical-hour approximation")


def evaluate(demand_h5,wind_csv,pv_csv,out,*,years=YEARS,states=STATES):
    import h5py
    verify_official_file(Path(demand_h5))
    wind,widx=read_native(wind_csv,"wind")
    pv,pidx=read_native(pv_csv,"pv")
    if not widx.equals(pidx):raise ValueError("Native 2012 wind/PV indexes differ")
    rows=[]
    with h5py.File(demand_h5) as handle:
        for year in years:
            g=handle[str(year)]
            check_fixed_cst_native_labels(g["datetime"][:])
            idx=pd.DatetimeIndex(pd.to_datetime(
                [v.decode() if isinstance(v,bytes) else str(v) for v in g["datetime"][:]],
                utc=True))
            if not idx.equals(widx):
                raise ValueError("2012 source demand hour-ending and weather native timestamps mismatch")
            for st in states:
                demand=np.asarray(g[st][:],dtype=float)
                if demand.shape!=(HOURS,) or not np.isfinite(demand).all() or (demand<0).any():
                    raise ValueError("Invalid 2012 source projected demand")
                for mode in MODES:
                    w_cf=modeled_hourly_cf(wind[st],mode)
                    p_cf=modeled_hourly_cf(pv[st],mode)
                    combined=WIND_FRACTION*w_cf+(1-WIND_FRACTION)*p_cf
                    for duration in DURATIONS:
                        result=solve_zone(
                            demand,combined,duration,
                            renewable_peak_ratio=RENEWABLE_PEAK_RATIO,
                            battery_power_peak_ratio=.25)
                        rows.append({
                            "experiment":"ReEDS2022 county-native full-state resource CF hypothetical MW deployment",
                            "state":st,"demand_model_year":year,"reference_weather_year":2012,
                            "hour_approximation":mode,
                            "first_hour_trapezoid_endpoint_fallback":mode=="trapezoid_with_first_endpoint",
                            "battery_duration_h":duration,
                            "installed_renewable_mw_as_fraction_of_peak_load":RENEWABLE_PEAK_RATIO,
                            "hypothetical_wind_fraction_of_installed_mw":WIND_FRACTION,
                            "available_resource_potential_mw_is_not_installed_capacity":True,
                            "state_cf_derived_from_original_county_hdf5":True,
                            "renewable_hour_energy_assumed_not_publisher_certified":True,
                            "network_opf_or_adequacy_claimed":False,
                            **result})
    frame=pd.DataFrame(rows)
    if len(frame)!=len(years)*len(states)*len(MODES)*len(DURATIONS):
        raise ValueError("Wrong experiment size")
    # Cross-check paired 0h/4h storage objective monotonicity.
    for (_,_,mode),grp in frame.groupby(["state","demand_model_year","hour_approximation"]):
        a=grp.set_index("battery_duration_h")
        if a.loc[4,"objective_illustrative_variable_usd"]>a.loc[0,"objective_illustrative_variable_usd"]+.05:
            raise ValueError("Battery LP has higher optimum objective than feasible no-storage LP")
        if (grp.max_equality_residual_mwh>1e-5).any():
            raise ValueError("Source-backed LP mass balance failed")
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    frame.to_csv(out/"paper_s_reeds2022_county_full_state_2012_weather_48_LP.csv",
                 index=False,float_format="%.12g")
    report={
        "status":"COUNTY_NATIVE_FOUR_STATE_2012_REFERENCE_WEATHER_HYPOTHETICAL_LP",
        "scenario_count":len(frame),"demand_years":list(years),
        "states":list(states),"reference_weather_year":2012,
        "source_wind_and_pv_artifacts_workflow":42962740548,
        "source_demand_original_HDF5_MD5_verified":True,
        "source_HDF5_and_geographic_county_authentication":True,
        "hourly_energy_integration_derived_assumption":True,
        "trapezoid_hour_zero_uses_endpoint_fallback":True,
        "source_installed_fleet_calibrated":False,
        "cross_state_BA_allocation_used":False,
        "old_EFS2020_results_modified":False,
        "physical_network_or_reliability_certified":False,
    }
    (out/"paper_s_reeds2022_county_full_state_lp_manifest.json").write_text(
        json.dumps(report,indent=2)+"\n")
    print(frame[["state","demand_model_year","hour_approximation","battery_duration_h",
                 "objective_illustrative_variable_usd","firm_generation_mwh",
                 "unused_renewable_mwh","storage_discharge_to_load_mwh"]].to_string(index=False))
    print("COUNTY_NATIVE_REEDS2022_ILLUSTRATIVE_LP_PASSED")
    return frame


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--demand-h5",type=Path,required=True)
    p.add_argument("--wind-csv",type=Path,required=True)
    p.add_argument("--pv-csv",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    evaluate(a.demand_h5,a.wind_csv,a.pv_csv,a.out)


if __name__=="__main__":
    main()
