"""Primal binding vs HiGHS upper-bound dual derivatives, cross-checked by reoptimization.

EFS 2030 source ordinal load, synthetic resource assumptions. One-sided finite
differences can cross an LP kink; disagreement is reported, never concealed.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from .efs_cyclic_storage_lp import solve_zone
from .efs_ordinal_storage_sensitivity import shape_cf

CASES=(("flat_50pct",.25,1.),("ordinal24_wave_A",.125,.5),
       ("ordinal24_wave_A",.25,1.),("ordinal24_wave_B",.25,1.))
STEP_RATIO=1e-4

def analyze(hourly,group):
    if group not in (1,7): raise ValueError("Selected two source shape groups are 1 and 7")
    source=hourly.loc[(hourly.synthetic_supply_shape=="flat_50pct")&
                      (hourly.battery_duration_h==0)].sort_values("local_hour_id")
    if len(source)!=8760 or not np.array_equal(source.local_hour_id.to_numpy(),np.arange(1,8761)):
        raise ValueError("Incomplete original source hour sequence")
    if len(source[["state","reeds_zone","planning_year"]].drop_duplicates())!=1 or source.planning_year.iloc[0]!=2030:
        raise ValueError("Invalid original demand identity")
    d=source.demand_mwh.to_numpy(dtype=float)
    if not np.isfinite(d).all() or d.max()<=0 or (d<0).any():raise ValueError("Invalid source demand")
    peak=float(d.max())
    results=[];traces=[]
    for shape,p,e in CASES:
        availability=shape_cf(np.arange(1,8761),shape)
        kwargs={"battery_power_peak_ratio":p,"storage_energy_peak_hours":e}
        base,dual=solve_zone(d,availability,4,return_duals=True,**kwargs)
        # Perturb absolute MW or MWh while holding the other physical dimension fixed.
        # Original dimensionless ratio step of 1e-4 = peak MW * 1e-4.
        plus_power=solve_zone(d,availability,4,battery_power_peak_ratio=p+STEP_RATIO,
                              storage_energy_peak_hours=e)
        plus_energy=solve_zone(d,availability,4,battery_power_peak_ratio=p,
                               storage_energy_peak_hours=e+STEP_RATIO)
        fd_p=(plus_power["objective_illustrative_variable_usd"]-
              base["objective_illustrative_variable_usd"])/(peak*STEP_RATIO)
        fd_e=(plus_energy["objective_illustrative_variable_usd"]-
              base["objective_illustrative_variable_usd"])/(peak*STEP_RATIO)
        dual_p=base["objective_derivative_installed_power_usd_per_mw"]
        dual_e=base["objective_derivative_installed_energy_usd_per_mwh"]
        row={"source_shape_group":group,"state":str(source.state.iloc[0]),
             "reeds_zone":str(source.reeds_zone.iloc[0]),"synthetic_supply_shape":shape,
             "battery_power_peak_ratio":p,"battery_energy_peak_hours":e,
             "installed_power_mw":base["storage_power_mw"],"installed_energy_mwh":base["storage_capacity_mwh"],
             "original_toy_objective_usd":base["objective_illustrative_variable_usd"],
             "dual_objective_derivative_power_usd_per_mw":dual_p,
             "dual_objective_derivative_energy_usd_per_mwh":dual_e,
             "forward_difference_power_usd_per_mw":fd_p,
             "forward_difference_energy_usd_per_mwh":fd_e,
             "dual_minus_forward_power_usd_per_mw":dual_p-fd_p,
             "dual_minus_forward_energy_usd_per_mwh":dual_e-fd_e,
             "power_derivative_disagrees_over_1pct":bool(abs(dual_p-fd_p)>max(1.,.01*max(abs(dual_p),abs(fd_p)))),
             "energy_derivative_disagrees_over_1pct":bool(abs(dual_e-fd_e)>max(1.,.01*max(abs(dual_e),abs(fd_e)))),
             "soc_upper_bound_hours":int(dual.soc_upper_bound_active.sum()),
             "charge_power_bound_hours":int(dual.charging_upper_bound_active.sum()),
             "discharge_power_bound_hours":int(dual.discharging_upper_bound_active.sum()),
             "nonzero_soc_dual_hours":base["num_nonzero_soc_energy_duals"],
             "nonzero_charge_dual_hours":base["num_nonzero_charge_power_duals"],
             "nonzero_discharge_dual_hours":base["num_nonzero_discharge_power_duals"],
             "cyclic_soc_verified":bool(base["cyclic_SOC_0_to_0_verified"])}
        # Relaxing an LP bound cannot increase the optimum.
        if fd_p>1e-3 or fd_e>1e-3 or dual_p>1e-5 or dual_e>1e-5:
            raise ValueError("Relaxing MW/MWh capacity increased optimal objective")
        if not row["cyclic_soc_verified"]:raise ValueError("SOC gate missing")
        for column in ("soc","charge","discharge"):
            if row[f"nonzero_{column}_dual_hours"]>row[{"soc":"soc_upper_bound_hours",
                "charge":"charge_power_bound_hours","discharge":"discharge_power_bound_hours"}[column]]:
                raise ValueError("Nonzero dual exists without an active bound")
        results.append(row)
        record=dual.copy()
        record.insert(0,"synthetic_supply_shape",shape)
        record.insert(0,"battery_power_peak_ratio",p)
        record.insert(0,"battery_energy_peak_hours",e)
        record.insert(0,"source_shape_group",group)
        traces.append(record)
    return pd.DataFrame(results),pd.concat(traces,ignore_index=True)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--original-hourly",required=True,type=Path)
    ap.add_argument("--group",required=True,type=int,choices=(1,7))
    ap.add_argument("--out-dir",required=True,type=Path)
    x=ap.parse_args()
    summary,dual=analyze(pd.read_csv(x.original_hourly,compression="infer"),x.group)
    x.out_dir.mkdir(parents=True,exist_ok=True)
    summary.to_csv(x.out_dir/"paper_s_dual_vs_fd_summary.csv",index=False)
    dual.to_csv(x.out_dir/"paper_s_hourly_bound_duals.csv.gz",index=False,compression="gzip")
    manifest={"status":"PAPER_S_ARCHIVED_SOURCE_DUAL_FINITE_DIFFERENCE_AUDIT_PASS",
        "zone_group":x.group,"cases":len(summary),"hourly_rows":len(dual),
        "forward_step_in_peak_ratio":STEP_RATIO,
        "derivative_disagreements_are_retained_not_hidden":True,
        "objective_excludes_capex":True,"source_utc_certified":False}
    (x.out_dir/"paper_s_dual_fd_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(summary.to_string(index=False))
    print(json.dumps(manifest,indent=2))
if __name__=="__main__":main()
