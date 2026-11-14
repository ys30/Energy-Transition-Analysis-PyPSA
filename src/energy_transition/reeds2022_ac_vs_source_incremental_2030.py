"""Compare incremental battery sizing under legacy heterogeneous source-MW and common AC nameplates.

Reuses two successful 180-LP source archives. Repeats no LP optimization.
All contrasts are *scenario-definition* differences: the AC-normalized
solar nameplate changes implied installed DC array MW relative to the
old source-denominator experiment.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from energy_transition.reeds2022_incremental_storage_design_2030 import incremental_design_comparisons

RUN_LEGACY=43051615043
RUN_AC=43058074434

def exact_pair(a,b,kind):
    fields=["state","demand_model_year","renewable_peak_ratio","wind_share_installed_mw",
            "battery_power_peak_ratio" if kind=="duration" else "battery_duration_h"]
    x=a.set_index(fields).sort_index()
    y=b.set_index(fields).sort_index()
    if len(x)!=72 or len(y)!=72 or x.index.has_duplicates or y.index.has_duplicates or not x.index.equals(y.index):
        raise ValueError("A common-AC/legacy 72-case incremental pairing is incomplete")
    out=pd.DataFrame(index=x.index)
    for label,df in (("source_denominator",x),("common_AC",y)):
        out[f"incremental_annual_savings_usd_{label}"]=df.incremental_annual_variable_savings_usd
        out[f"incremental_power_kw_{label}"]=df.incremental_power_kw
        out[f"incremental_energy_kwh_{label}"]=df.incremental_energy_kwh
        out[f"energy_only_annuity_usd_per_kwh_year_{label}"]=df.max_incremental_energy_annuity_usd_per_kwh_year
        out[f"power_only_annuity_usd_per_kw_year_{label}"]=df.max_incremental_power_only_annuity_usd_per_kw_year
    for measure in ("incremental_power_kw","incremental_energy_kwh"):
        if not np.allclose(out[f"{measure}_source_denominator"],out[f"{measure}_common_AC"],atol=1e-6,rtol=0):
            raise ValueError("Source capacity basis change illegally altered battery installed capacity")
    out["common_AC_minus_source_savings_usd"]=(
        out.incremental_annual_savings_usd_common_AC-out.incremental_annual_savings_usd_source_denominator)
    out["common_AC_minus_source_energy_annuity_usd_per_kwh_year"]=(
        out.energy_only_annuity_usd_per_kwh_year_common_AC-
        out.energy_only_annuity_usd_per_kwh_year_source_denominator)
    out["common_AC_minus_source_power_annuity_usd_per_kw_year"]=(
        out.power_only_annuity_usd_per_kw_year_common_AC-
        out.power_only_annuity_usd_per_kw_year_source_denominator)
    out["comparison_kind"]=kind
    return out.reset_index()


def analyze(legacy_csv,ac_csv,out):
    legacy=pd.read_csv(legacy_csv)
    ac=pd.read_csv(ac_csv)
    d_old,p_old=incremental_design_comparisons(legacy)
    d_ac,p_ac=incremental_design_comparisons(ac)
    duration=exact_pair(d_old,d_ac,"duration")
    power=exact_pair(p_old,p_ac,"power")
    if len(duration)!=72 or len(power)!=72:raise ValueError("Expected 144 matched incremental comparisons")
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    duration.to_csv(out/"paper_s_reeds2022_72_ac_vs_original_duration_incremental.csv",index=False,float_format="%.12g")
    power.to_csv(out/"paper_s_reeds2022_72_ac_vs_original_power_incremental.csv",index=False,float_format="%.12g")
    m={"status":"COMMON_AC_VS_LEGACY_144_INCREMENTAL_STORAGE_COMPARISONS_PASSED",
       "source_original_180_LP_run":RUN_LEGACY,"source_common_AC_180_LP_run":RUN_AC,
       "duration_pair_count":len(duration),"power_pair_count":len(power),
       "weather_year":2012,"demand_year":2030,
       "PV_common_AC_inverter_loading_ratio":1.34,
       "PV_array_dc_mw_differs_between_scenarios":True,
       "source_profiles_changed":False,
       "installed_fleet_known":False,
       "battery_investment_cost_included":False,
       "hour_integration_certified_by_publisher":False}
    (out/"paper_s_reeds2022_144_ac_source_incremental_basis_manifest.json").write_text(json.dumps(m,indent=2)+"\n")
    for name,df in (("4_TO_8H",duration),("10_TO_25PCT",power)):
        print(name,"2030 1.5x renewable, 50pct AC-nameplate wind, power .25 or duration 4h:")
        sub=df[df.renewable_peak_ratio.eq(1.5)&df.wind_share_installed_mw.eq(.5)]
        sub=sub[sub.battery_power_peak_ratio.eq(.25)] if name=="4_TO_8H" else sub[sub.battery_duration_h.eq(4)]
        print(sub[["state","incremental_annual_savings_usd_source_denominator",
                   "incremental_annual_savings_usd_common_AC",
                   "energy_only_annuity_usd_per_kwh_year_source_denominator",
                   "energy_only_annuity_usd_per_kwh_year_common_AC",
                   "power_only_annuity_usd_per_kw_year_source_denominator",
                   "power_only_annuity_usd_per_kw_year_common_AC"]].to_string(index=False))
    print("AC_AND_SOURCE_DENOMINATOR_144_INCREMENTAL_COMPARISONS_PASSED")
    return duration,power

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--legacy",required=True,type=Path)
    p.add_argument("--ac",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    analyze(a.legacy,a.ac,a.out)

if __name__=="__main__":
    main()
