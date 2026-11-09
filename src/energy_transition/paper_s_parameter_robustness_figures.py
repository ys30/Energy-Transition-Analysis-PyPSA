"""Figure S10 from archive-verified Paper S 294 LP sensitivity cases.

This chart counts distinct normalized EFS demand-source shapes (not
statistically independent regional draws). Power-ratio changes ALSO change
assumed battery energy MWh because energy capacity = power MW * duration h.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ORDER=("baseline","half_power","double_power","rte_80pct","rte_95pct",
       "firm_60usd","firm_150usd")
SHAPES=("flat_50pct","ordinal24_wave_A","ordinal24_wave_B")
LABELS=("Baseline","Half power","Double power","80% efficiency",
        "95% efficiency","$60/MWh firm","$150/MWh firm")
SCHEMA={"source_shape_group","scenario","synthetic_supply_shape",
        "additional_discharge_mwh","avoided_firm_mwh","avoided_unused_mwh",
        "toy_objective_reduction_usd","firm_unit_cost"}

def validate(frame):
    if not SCHEMA.issubset(frame):raise ValueError("Missing archive comparison fields")
    k=["source_shape_group","scenario","synthetic_supply_shape"]
    if len(frame)!=147 or frame.duplicated(k).any():
        raise ValueError("Expected 147 unique shape-scenario LP comparisons")
    if (set(frame.source_shape_group)!=set(range(1,8)) or
        set(frame.scenario)!=set(ORDER) or
        set(frame.synthetic_supply_shape)!=set(SHAPES)):
        raise ValueError("Incomplete seven-shape scenario population")
    cols=["additional_discharge_mwh","avoided_firm_mwh","avoided_unused_mwh",
          "toy_objective_reduction_usd","firm_unit_cost"]
    if not np.isfinite(frame[cols].to_numpy(dtype=float)).all():
        raise ValueError("Nonfinite optimized source results")
    predicted=frame.firm_unit_cost*frame.avoided_firm_mwh-5.*frame.avoided_unused_mwh
    if not np.allclose(predicted,frame.toy_objective_reduction_usd,rtol=1e-9,atol=.1):
        raise ValueError("Parameter objective source identity failed")
    return frame

def generate(frame,outdir):
    df=validate(frame)
    counts=(df.assign(positive=df.additional_discharge_mwh>1e-3)
              .groupby(["scenario","synthetic_supply_shape"]).positive.sum().unstack()
              .loc[list(ORDER),list(SHAPES)])
    out=Path(outdir);out.mkdir(parents=True,exist_ok=True)
    counts.to_csv(out/"paper_s_Figure_S10_positive_shapes_counts.csv")
    fig,ax=plt.subplots(figsize=(11.5,5.4))
    x=np.arange(len(ORDER));width=.25
    for index,shape in enumerate(SHAPES):
        bars=ax.bar(x+(index-1)*width,counts[shape].to_numpy(),width,
                    label={"flat_50pct":"Flat 50%","ordinal24_wave_A":"Wave A",
                           "ordinal24_wave_B":"Wave B"}[shape])
        ax.bar_label(bars,padding=2,fontsize=9)
    ax.set_xticks(x,LABELS,rotation=22,ha="right")
    ax.set_ylim(0,8);ax.set_yticks(range(8))
    ax.set_ylabel("Distinct source-demand shapes with positive 4h→8h extra discharge (of 7)")
    ax.set_title("Figure S10 | Sensitivity of storage-duration response")
    ax.legend(ncol=3,frameon=False)
    ax.grid(axis="y",alpha=.18);ax.set_axisbelow(True)
    fig.text(.5,.012,"EFS ordinal demand + synthetic resources. Power changes also alter energy capacity; no battery CAPEX or Western OPF.",
             ha="center",fontsize=8)
    fig.tight_layout(rect=[0,.06,1,1])
    for extension in (".png",".svg"):
        fig.savefig(out/("Figure_S10_2030_parameter_robustness"+extension),
                    dpi=220,bbox_inches="tight")
    plt.close(fig)
    manifest={"status":"FIGURE_S10_294_ARCHIVED_LP_ROBUSTNESS_REPRODUCED",
        "source_lp_cases":294,"source_marginal_comparisons":147,
        "distinct_normalized_load_shapes":7,"sensitivity_scenarios":list(ORDER),
        "positive_threshold_mwh":1e-3,"physical_hour_UTC_verified":False,
        "actual_renewable_profiles":False,"storage_capex_included":False}
    (out/"Figure_S10_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--comparisons",type=Path,required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(generate(pd.read_csv(a.comparisons),a.out_dir),indent=2))

if __name__=="__main__":main()
