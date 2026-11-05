"""Publication-style figures from archived, verified 540-case cyclic EFS LP evidence.

Only plots *assumption-dependent* values; never model results as real Western
grid generation, curtailment, costs, or observed renewable generation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

YEARS=(2030,2040,2050)
SHAPES=("flat_50pct","ordinal24_wave_A","ordinal24_wave_B")
DURATIONS=(0,4,8)
WARNING="EFS projected load; supply/battery synthetic. No physical UTC or Western network OPF."

def validate(summary: pd.DataFrame) -> pd.DataFrame:
    req={"planning_year","synthetic_supply_shape","battery_duration_h",
         "demand_mwh","renewable_available_mwh","unused_renewable_mwh",
         "firm_generation_mwh","storage_discharge_to_load_mwh",
         "objective_illustrative_variable_usd"}
    if not req.issubset(summary):
        raise ValueError("Missing source-result columns")
    if summary[list(req)].isna().any().any():
        raise ValueError("Missing source results")
    k=["planning_year","synthetic_supply_shape","battery_duration_h"]
    if summary.duplicated(k).any() or len(summary)!=27:
        raise ValueError("Duplicate or incomplete scenario")
    if (set(summary.planning_year)!=set(YEARS) or
        set(summary.synthetic_supply_shape)!=set(SHAPES) or
        set(summary.battery_duration_h)!=set(DURATIONS)):
        raise ValueError("Unexpected scenario population")
    vals=summary[[c for c in req if c not in k]].to_numpy(dtype=float)
    if not np.isfinite(vals).all() or (vals<0).any():
        raise ValueError("Invalid source scenario metrics")
    for (year,shape),g in summary.groupby(["planning_year","synthetic_supply_shape"]):
        if not np.allclose(g.demand_mwh,g.demand_mwh.iloc[0],rtol=1e-10,atol=.1):
            raise ValueError("Demand changes with battery")
        if not np.allclose(g.renewable_available_mwh,g.renewable_available_mwh.iloc[0],rtol=1e-10,atol=.1):
            raise ValueError("Renewable available MWh changes with battery")
        if not np.all(g.sort_values("battery_duration_h").firm_generation_mwh.diff().dropna()<=.1):
            raise ValueError("Increasing battery duration increases firm generation")
    return summary.sort_values(k).reset_index(drop=True)


def save_figure(fig,base):
    fig.savefig(base.with_suffix(".png"),dpi=200,bbox_inches="tight")
    fig.savefig(base.with_suffix(".svg"),bbox_inches="tight")
    plt.close(fig)


def make_figures(data,out_dir):
    frame=validate(data)
    out_dir=Path(out_dir);out_dir.mkdir(parents=True,exist_ok=True)
    palette={"flat_50pct":"#4c78a8","ordinal24_wave_A":"#e45756","ordinal24_wave_B":"#54a24b"}
    names={"flat_50pct":"Flat (assumed 50%)","ordinal24_wave_A":"Synthetic wave A","ordinal24_wave_B":"Synthetic wave B"}
    # Figure 1: 2030 demand-equal supply shapes and battery, grouped series
    fig,ax=plt.subplots(figsize=(8.0,4.8))
    for shape in SHAPES:
        sub=frame[(frame.planning_year==2030)&(frame.synthetic_supply_shape==shape)].sort_values("battery_duration_h")
        ax.plot(sub.battery_duration_h,sub.unused_renewable_mwh/1e6,marker="o",
                color=palette[shape],linewidth=2,label=names[shape])
    ax.set(xlabel="Assumed battery duration (hours)",ylabel="Modeled unused renewable availability (TWh)",
           title="2030 EFS-based illustrative battery sensitivity")
    ax.set_xticks(DURATIONS);ax.grid(axis="y",alpha=.25);ax.legend(frameon=False)
    fig.text(.5,-.005,WARNING,ha="center",fontsize=8)
    fig.tight_layout();save_figure(fig,out_dir/"fig1_2030_model_unused_supply")

    # Figure 2: 3-year wave A results, physically labeled as toy outputs
    fig,axes=plt.subplots(1,2,figsize=(11.3,4.6))
    for year in YEARS:
        sub=frame[(frame.planning_year==year)&(frame.synthetic_supply_shape=="ordinal24_wave_A")].sort_values("battery_duration_h")
        axes[0].plot(sub.battery_duration_h,sub.unused_renewable_mwh/1e6,marker="o",label=str(year))
        axes[1].plot(sub.battery_duration_h,sub.firm_generation_mwh/1e6,marker="o",label=str(year))
    axes[0].set(ylabel="Unused hypothetical renewable availability (TWh)",xlabel="Battery duration (hours)")
    axes[1].set(ylabel="Illustrative firm energy (TWh)",xlabel="Battery duration (hours)")
    for ax in axes:ax.set_xticks(DURATIONS);ax.grid(axis="y",alpha=.25)
    axes[0].legend(frameon=False);fig.suptitle("Wave A assumptions: EFS projected load, cyclic LP",y=1.01)
    fig.text(.5,-.015,WARNING,ha="center",fontsize=8)
    fig.tight_layout();save_figure(fig,out_dir/"fig2_wave_A_three_years")

    # Figure 3: diminishing avoided model firm energy in 2030 for wave A
    sub=frame[(frame.planning_year==2030)&(frame.synthetic_supply_shape=="ordinal24_wave_A")].sort_values("battery_duration_h")
    firm=sub.firm_generation_mwh.to_numpy()/1e6
    fig,ax=plt.subplots(figsize=(7.2,4.6))
    bars=ax.bar(["0 → 4 hours","4 → 8 hours"],[firm[0]-firm[1],firm[1]-firm[2]],
                color=["#4c78a8","#e45756"])
    ax.bar_label(bars,fmt="%.2f TWh",padding=3)
    ax.set(ylabel="Additional assumed firm energy displaced (TWh)",
           title="2030 wave A: incremental assumed battery duration benefit")
    ax.set_ylim(0,max(firm[0]-firm[1],firm[1]-firm[2])*1.2)
    ax.grid(axis="y",alpha=.25);ax.set_axisbelow(True)
    fig.text(.5,-.005,WARNING,ha="center",fontsize=8)
    fig.tight_layout();save_figure(fig,out_dir/"fig3_incremental_2030_firm")
    return {
        "status":"ARTIFACT_DERIVED_540_LP_FIGURES_GENERATED",
        "source_scenario_rows":len(frame),
        "years":list(YEARS),
        "shapes":list(SHAPES),
        "storage_duration_hours":list(DURATIONS),
        "files":[p.name for p in sorted(out_dir.glob("fig*.*"))],
        "raw_source_EFS_demand":True,
        "supply_and_storage_empirical":False,
        "calendar_UTC_certified":False,
        "real_Western_OPF_admitted":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--summary",required=True,type=Path)
    p.add_argument("--out-dir",required=True,type=Path)
    a=p.parse_args()
    result=make_figures(pd.read_csv(a.summary),a.out_dir)
    (a.out_dir/"figure_manifest.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))


if __name__=="__main__":main()
