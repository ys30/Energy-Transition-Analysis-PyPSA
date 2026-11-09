"""Figure S15: SOC upper-bound hours under nearly cost-equivalent LP schedules.

Input is the accepted, original-objective re-scored 32-case SOC perturbation audit.
The figure is evidence for schedule sensitivity, NOT mathematical proof of multiple
strictly identical optimal bases.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

MODES=("baseline","soc_penalty","soc_reward","ordinal_wiggle")
PROBES=(("flat_50pct",.25,1.),("ordinal24_wave_A",.125,.5),
        ("ordinal24_wave_A",.25,1.),("ordinal24_wave_B",.25,1.))
SHAPES={"flat_50pct":"Flat","ordinal24_wave_A":"Wave A","ordinal24_wave_B":"Wave B"}

def validate(df):
    keys=["source_shape_group","synthetic_supply_shape",
          "battery_power_peak_ratio","battery_energy_peak_hours","perturbation_mode"]
    required=set(keys+["state","reeds_zone","original_objective_gap_usd",
                     "soc_bound_hours_delta","max_abs_hourly_soc_change_mwh",
                     "near_optimal_within_1ppm"])
    if not required.issubset(df):raise ValueError("Missing original schedule audit fields")
    if len(df)!=32 or df.duplicated(keys).any() or set(df.source_shape_group)!={1,7}:
        raise ValueError("Incomplete original 32-case schedule audit")
    if set(df.perturbation_mode)!=set(MODES):
        raise ValueError("Incomplete original perturbation modes")
    for group,subset in df.groupby("source_shape_group"):
        if len(subset)!=16:raise ValueError("Original source group incomplete")
        items=set(zip(subset.synthetic_supply_shape,
                      subset.battery_power_peak_ratio,subset.battery_energy_peak_hours))
        if items!=set(PROBES):raise ValueError("Original scheduled probes mismatch")
        if subset[["state","reeds_zone"]].drop_duplicates().shape[0]!=1:
            raise ValueError("Group source ID mismatch")
    if not df.near_optimal_within_1ppm.all():raise ValueError("Candidate outside 1ppm objective bound")
    numerical=df[["original_objective_gap_usd","soc_bound_hours_delta",
                  "max_abs_hourly_soc_change_mwh"]].to_numpy(dtype=float)
    if not np.isfinite(numerical).all():raise ValueError("Invalid nonfinite source values")
    if df.original_objective_gap_usd.abs().max()>.03:
        raise ValueError("Source schedule cost gap is too large for plotted claim")
    return df

def plot(source,out):
    df=validate(source)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    base=df[df.perturbation_mode=="baseline"].sort_values([
        "source_shape_group","synthetic_supply_shape","battery_power_peak_ratio"])
    labels=[]
    for r in base.itertuples(index=False):
        labels.append(f"{r.state} · {SHAPES[r.synthetic_supply_shape]}\nP={r.battery_power_peak_ratio:g}, E={r.battery_energy_peak_hours:g}")
    fig,ax=plt.subplots(figsize=(13,5.2))
    modes=("soc_penalty","soc_reward","ordinal_wiggle")
    for i,mode in enumerate(modes):
        values=[]
        for r in base.itertuples(index=False):
            v=df[(df.source_shape_group==r.source_shape_group)&
                 (df.synthetic_supply_shape==r.synthetic_supply_shape)&
                 (df.battery_power_peak_ratio==r.battery_power_peak_ratio)&
                 (df.battery_energy_peak_hours==r.battery_energy_peak_hours)&
                 (df.perturbation_mode==mode)]
            if len(v)!=1:raise ValueError("Missing one matching perturbation")
            values.append(int(v.soc_bound_hours_delta.iloc[0]))
        ax.scatter(np.arange(len(base))+(i-1)*.13,values,s=58,label=mode.replace("_"," "))
    ax.axhline(0,color="black",linewidth=.8)
    ax.set_xticks(range(len(base)),labels,fontsize=8)
    ax.set_ylabel("Change in hours with SOC at installed energy capacity")
    ax.set_title("Figure S15 | SOC binding counts under near-optimal schedules")
    ax.legend(frameon=False,ncol=3)
    ax.grid(axis="y",alpha=.18)
    fig.text(.5,.012,
        "32 original-archive reconciled LPs, rescored without SOC tie-break; max cost difference < $0.000001. EFS ordinal + synthetic supply.",
        ha="center",fontsize=8)
    fig.tight_layout(rect=[0,.055,1,1])
    for extension in (".png",".svg"):
        fig.savefig(out/("Figure_S15_SOC_schedule_sensitivity"+extension),
                    dpi=220,bbox_inches="tight")
    plt.close(fig)
    report={"status":"PAPER_S_FIGURE_S15_ORIGINAL_32_SCHEDULE_AUDIT_PASS",
            "candidate_schedules":32,"source_demand_groups":2,
            "max_abs_unperturbed_cost_difference_usd":float(df.original_objective_gap_usd.abs().max()),
            "strict_multiple_exact_optima_mathematically_proven":False,
            "not_physical_utc_or_observed_renewable":True}
    (out/"Figure_S15_manifest.json").write_text(json.dumps(report,indent=2)+"\n")
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(plot(pd.read_csv(a.source),a.out_dir),indent=2))
if __name__=="__main__":main()
