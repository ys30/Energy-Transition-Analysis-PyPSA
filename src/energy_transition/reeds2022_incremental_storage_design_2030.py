"""Incremental storage sizing frontier from the archived 180 source-weather LPs.

Only compare identical state, projected load, source weather, renewable
nameplate scenario and wind/PV mix. Duration comparison holds charge and
discharge power fixed; power comparison holds duration fixed (and so
necessarily increases BOTH power and energy MWh). All outputs are annual
illustrative variable-operating-cost upper bounds, not project NPVs.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

STATES=("AZ","CO","ID","WY")
RATIOS=(0.9,1.5,2.0)
WIND_SHARES=(0.25,0.5,0.75)
DURATIONS=(4,8)
POWERS=(0.10,0.25)
ENERGY_ANNUITIES=(0.,10.,25.)
KEYS=("state","demand_model_year","renewable_peak_ratio","wind_share_installed_mw")
METRICS=("objective_illustrative_variable_usd","storage_power_mw","storage_capacity_mwh",
         "storage_discharge_to_load_mwh","firm_generation_mwh","unused_renewable_mwh")


def incremental_design_comparisons(source):
    src=source.copy()
    if len(src)!=180 or src.duplicated(list(KEYS)+["battery_duration_h","battery_power_peak_ratio"]).any():
        raise ValueError("Source must have 180 unique original LP scenarios")
    if set(src.state)!=set(STATES) or set(src.demand_model_year)!={2030}:
        raise ValueError("Wrong geographic/year scope")
    if set(src.renewable_peak_ratio)!=set(RATIOS) or set(src.wind_share_installed_mw)!=set(WIND_SHARES):
        raise ValueError("Non-prespecified renewable deployments or wind shares")
    if not src.solver_status.eq("optimal").all():
        raise ValueError("Nonoptimal source experiment")
    storage=src[src.battery_duration_h.gt(0)].copy()
    if len(storage)!=144 or set(storage.battery_duration_h)!=set(DURATIONS) or set(storage.battery_power_peak_ratio)!=set(POWERS):
        raise ValueError("Missing original storage designs")
    for metric in METRICS:
        if not np.isfinite(storage[metric].to_numpy(dtype=float)).all():
            raise ValueError("Nonfinite LP original metric")

    def match(lower,upper,keys,kind):
        a=lower.set_index(keys).sort_index()
        b=upper.set_index(keys).sort_index()
        if len(a)!=len(b) or a.index.has_duplicates or b.index.has_duplicates or not a.index.equals(b.index):
            raise ValueError("Cannot form exact source-matched design pairs")
        delta_s=a["objective_illustrative_variable_usd"]-b["objective_illustrative_variable_usd"]
        delta_p=(b["storage_power_mw"]-a["storage_power_mw"])*1000
        delta_e=(b["storage_capacity_mwh"]-a["storage_capacity_mwh"])*1000
        if (delta_s<-.1).any() or (delta_e<=0).any():
            raise ValueError("LP storage design monotonicity/capacity violation")
        if kind=="duration" and (np.abs(delta_p)>.001).any():
            raise ValueError("Duration-only case changed power")
        if kind=="power" and (delta_p<=0).any():
            raise ValueError("Power increase must enlarge power capacity")
        out=pd.DataFrame(index=a.index)
        out["comparison"]=kind
        out["lower_power_mw"]=a["storage_power_mw"]
        out["upper_power_mw"]=b["storage_power_mw"]
        out["lower_energy_mwh"]=a["storage_capacity_mwh"]
        out["upper_energy_mwh"]=b["storage_capacity_mwh"]
        out["incremental_power_kw"]=delta_p
        out["incremental_energy_kwh"]=delta_e
        out["incremental_annual_variable_savings_usd"]=delta_s
        out["max_combined_incremental_annuity_usd_per_year"]=delta_s
        out["max_incremental_energy_annuity_usd_per_kwh_year"]=delta_s/delta_e
        out["incremental_firm_energy_displacement_mwh"]=a["firm_generation_mwh"]-b["firm_generation_mwh"]
        out["incremental_curtailment_reduction_mwh"]=a["unused_renewable_mwh"]-b["unused_renewable_mwh"]
        # For power+energy enlargement, power-only annuity is a bound
        # conditional on zero additional cost of extra energy.
        out["max_incremental_power_only_annuity_usd_per_kw_year"]=np.where(
            delta_p>0,delta_s/delta_p,np.nan)
        for annualized_energy_cost in ENERGY_ANNUITIES:
            name=str(int(annualized_energy_cost))
            out[f"remaining_power_annuity_if_extra_energy_{name}_usd_per_kw_year"]=np.where(
                delta_p>0,(delta_s-annualized_energy_cost*delta_e)/delta_p,np.nan)
        return out.reset_index()

    duration=match(
        storage[storage.battery_duration_h.eq(4)],
        storage[storage.battery_duration_h.eq(8)],
        [*KEYS,"battery_power_peak_ratio"],"4_to_8h_fixed_power")
    power=match(
        storage[storage.battery_power_peak_ratio.eq(.10)],
        storage[storage.battery_power_peak_ratio.eq(.25)],
        [*KEYS,"battery_duration_h"],"10_to_25pct_peak_fixed_duration")
    if len(duration)!=72 or len(power)!=72:
        raise ValueError("Expected 72 duration and 72 power design comparisons")
    if not np.isclose(power.incremental_energy_kwh/
                      power.incremental_power_kw,
                      power.battery_duration_h).all():
        raise ValueError("Fixed-duration storage power comparison energy mismatch")
    if not np.isnan(duration.max_incremental_power_only_annuity_usd_per_kw_year).all():
        raise ValueError("Duration-only increment should not have power-unit break-even")
    return duration,power


def run(source,out):
    data=pd.read_csv(source)
    duration,power=incremental_design_comparisons(data)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    duration.to_csv(out/"paper_s_reeds2022_72_incremental_4h_to_8h_fixed_power.csv",index=False,float_format="%.12g")
    power.to_csv(out/"paper_s_reeds2022_72_incremental_10_to_25pct_fixed_duration.csv",index=False,float_format="%.12g")
    m={"status":"REEDS2022_COUNTY_144_STORAGE_INCREMENTAL_DESIGN_COMPARISONS_PASS",
       "source_180_lp_run_id":43051615043,"duration_pairs":len(duration),
       "power_pairs":len(power),"demand_model_year":2030,
       "weather_reference_year":2012,
       "duration_increment_power_held_fixed":True,
       "power_increment_energy_necessarily_increases_at_fixed_duration":True,
       "not_actual_investment_npv":True,"battery_capex_not_in_source_LP":True,
       "real_network_or_reliability_verified":False,
       "source_PV_DC_and_wind_capacity_mix_not_common_AC_verified":True}
    (out/"paper_s_reeds2022_144_incremental_storage_design_manifest.json").write_text(json.dumps(m,indent=2)+"\n")
    selected=duration[(duration.renewable_peak_ratio.eq(1.5))&
        (duration.wind_share_installed_mw.eq(.5))&
        (duration.battery_power_peak_ratio.eq(.25))]
    print("4_TO_8H_FIXED_POWER_2030_1P5X_WIND50")
    print(selected[["state","incremental_annual_variable_savings_usd",
                    "incremental_energy_kwh",
                    "max_incremental_energy_annuity_usd_per_kwh_year"]].to_string(index=False))
    selected2=power[(power.renewable_peak_ratio.eq(1.5))&
        (power.wind_share_installed_mw.eq(.5))&
        (power.battery_duration_h.eq(4))]
    print("10_TO_25PCT_POWER_FIXED_4H_2030_1P5X_WIND50")
    print(selected2[["state","incremental_annual_variable_savings_usd",
                     "incremental_power_kw","incremental_energy_kwh",
                     "max_incremental_power_only_annuity_usd_per_kw_year"]].to_string(index=False))
    print("REEDS2022_144_INCREMENTAL_STORAGE_DESIGN_PAIRS_PASS")
    return duration,power


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    run(a.source,a.out)

if __name__=="__main__":
    main()
