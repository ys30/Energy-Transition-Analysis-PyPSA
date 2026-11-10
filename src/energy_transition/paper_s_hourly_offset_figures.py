"""Postprocess accepted full-hour cost-capped LP traces into Figure S20.

Positive and negative discharge differences can cancel across source hours.
The 24-hour block plot is a local view, not a claim that all changes are local.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

WINDOW=(4001,4168)
DEMAND_GROUPS={1:("Arizona","p28"),7:("Wyoming","p24")}
MODES=("baseline","min","max")
COLS=("storage_charge_input_mwh","storage_discharge_to_load_mwh","soc_end_mwh",
      "firm_generation_mwh","unused_renewable_mwh")

def audit(traces,summaries):
    if len(traces)!=2*3*8760 or len(summaries)!=6:
        raise ValueError("Expected 52,560 source-hour trace rows and 6 archived schedules")
    if not {"source_shape_group","solution","local_hour_id",*COLS}.issubset(traces):
        raise ValueError("Missing original full-hour physical dispatch variables")
    if not {"source_shape_group","solution","window_discharge_mwh","annual_discharge_mwh",
            "original_cost_usd","allowed_extra_cost_usd"}.issubset(summaries):
        raise ValueError("Missing accepted source archive schedule summary")
    if traces.duplicated(["source_shape_group","solution","local_hour_id"]).any():
        raise ValueError("Duplicate original source hour")
    results=[]
    for group,(state,zone) in DEMAND_GROUPS.items():
        batch=traces.loc[traces.source_shape_group==group]
        certified=summaries.loc[summaries.source_shape_group==group].set_index("solution")
        if set(batch.solution)!=set(MODES) or set(certified.index)!=set(MODES):
            raise ValueError("Missing source-archived min/base/max solution")
        vectors={}
        for mode in MODES:
            v=batch.loc[batch.solution==mode].sort_values("local_hour_id")
            if len(v)!=8760 or not np.array_equal(v.local_hour_id.to_numpy(),np.arange(1,8761)):
                raise ValueError("Source hour completeness or chronological order mismatch")
            if not np.isfinite(v[list(COLS)].to_numpy(dtype=float)).all():
                raise ValueError("Nonfinite LP hourly primal output")
            discharge=v.storage_discharge_to_load_mwh.to_numpy(dtype=float)
            selected=np.arange(1,8761)
            inside=(selected>=WINDOW[0])&(selected<=WINDOW[1])
            if not np.isclose(discharge.sum(),float(certified.loc[mode,"annual_discharge_mwh"]),atol=.02):
                raise ValueError("Original archived annual discharge does not match trace")
            if not np.isclose(discharge[inside].sum(),float(certified.loc[mode,"window_discharge_mwh"]),atol=.02):
                raise ValueError("Original archived window discharge does not match trace")
            vectors[mode]=v.set_index("local_hour_id")
        for mode in ("min","max"):
            delta=(vectors[mode].storage_discharge_to_load_mwh-
                   vectors["baseline"].storage_discharge_to_load_mwh).to_numpy(dtype=float)
            selected=np.arange(1,8761)
            inside=(selected>=WINDOW[0])&(selected<=WINDOW[1])
            near=(selected>=3801)&(selected<=4368)&(~inside)
            outside=~inside
            records={"source_shape_group":group,"state":state,"reeds_zone":zone,
                 "candidate_solution":mode,
                 "inside_delta_mwh":float(delta[inside].sum()),
                 "outside_net_delta_mwh":float(delta[outside].sum()),
                 "annual_net_delta_mwh":float(delta.sum()),
                 "outside_absolute_delta_mwh":float(np.abs(delta[outside]).sum()),
                 "outside_positive_delta_mwh":float(np.clip(delta[outside],0,None).sum()),
                 "outside_negative_delta_mwh":float(np.clip(delta[outside],None,0).sum()),
                 "outside_nonzero_hours_over_1mwh":int((np.abs(delta[outside])>1).sum()),
                 "near_window_outside_net_delta_mwh":float(delta[near].sum()),
                 "distant_outside_net_delta_mwh":float(delta[outside].sum()-delta[near].sum())}
            if abs(records["inside_delta_mwh"]+records["outside_net_delta_mwh"]-
                   records["annual_net_delta_mwh"])>1e-5:
                raise ValueError("Source-hour inside/outside accounting failure")
            ref=certified.loc[mode,"annual_discharge_mwh"]-certified.loc["baseline","annual_discharge_mwh"]
            if not np.isclose(records["annual_net_delta_mwh"],ref,atol=.03):
                raise ValueError("Archive-derived annual difference not reproduced")
            results.append(records)
    return pd.DataFrame(results)

def draw(traces,summaries,out_dir):
    metric=audit(traces,summaries)
    out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    fig,axes=plt.subplots(2,2,figsize=(13,7.3),sharex=True)
    for row,(group,(state,zone)) in enumerate(DEMAND_GROUPS.items()):
        x=traces[traces.source_shape_group==group]
        base=x[x.solution=="baseline"].set_index("local_hour_id")
        for col,mode in enumerate(("min","max")):
            actual=x[x.solution==mode].set_index("local_hour_id")
            delta=actual.storage_discharge_to_load_mwh-base.storage_discharge_to_load_mwh
            ids=delta.index.to_numpy()
            chosen=(ids>=3601)&(ids<=4560)
            blocks=pd.DataFrame({"source_block":(ids[chosen]-1)//24+1,
                                 "delta":delta.to_numpy()[chosen]}).groupby("source_block").delta.sum()
            ax=axes[row,col]
            ax.bar(blocks.index,blocks.to_numpy(),width=.82)
            ax.axvspan((WINDOW[0]-1)//24+.5,(WINDOW[1]-1)//24+1.5,
                       color="gray",alpha=.16)
            ax.axhline(0,color="black",linewidth=.8)
            ax.set_title(f"{state} {zone}, {mode} window discharge")
            ax.set_ylabel("Net MWh change per source 24h block")
            ax.grid(axis="y",alpha=.15)
            ax.set_axisbelow(True)
    for ax in axes[-1,:]:
        ax.set_xlabel("Original source 24-hour block (not a calendar day)")
    fig.suptitle("Figure S20 | Local view of near-optimal discharge reallocation",fontsize=14)
    fig.text(.5,.012,"Only source hours 3601–4560 shown; nonzero changes also occur throughout the year. Synthetic Wave A; no physical UTC or Western OPF.",
             ha="center",fontsize=8)
    fig.tight_layout(rect=[0,.035,1,.95])
    for extension in (".png",".svg"):
        fig.savefig(out/("Figure_S20_original_hour_discharge_offsets"+extension),
                    dpi=220,bbox_inches="tight")
    plt.close(fig)
    metric.to_csv(out/"paper_s_four_source_hour_gross_and_net_offset_metrics.csv",index=False)
    manifest={"status":"PAPER_S_FIGURE_S20_ORIGINAL_52560_SOURCE_HOUR_TRACES_AUDITED",
       "hourly_rows":len(traces),"certified_schedules":6,
       "source_hours_not_physical_UTC":True,
       "gross_hourly_redistribution_not_additional_energy":True,
       "calendar_day_labels_not_claimed":True}
    (out/"Figure_S20_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(metric.to_string(index=False))
    return manifest

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--arizona-hourly",required=True,type=Path)
    ap.add_argument("--wyoming-hourly",required=True,type=Path)
    ap.add_argument("--arizona-summary",required=True,type=Path)
    ap.add_argument("--wyoming-summary",required=True,type=Path)
    ap.add_argument("--out-dir",required=True,type=Path)
    a=ap.parse_args()
    data=pd.concat([pd.read_csv(a.arizona_hourly,compression="infer"),
                    pd.read_csv(a.wyoming_hourly,compression="infer")],ignore_index=True)
    sums=pd.concat([pd.read_csv(a.arizona_summary),
                    pd.read_csv(a.wyoming_summary)],ignore_index=True)
    print(json.dumps(draw(data,sums,a.out_dir),indent=2))
if __name__=="__main__":main()
