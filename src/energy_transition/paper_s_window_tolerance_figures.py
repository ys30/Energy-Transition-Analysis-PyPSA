"""Figure S19, source-certified 168-hour discharge envelope under 3 cost caps.

Shows percentage of previously accepted interval remaining as dollar allowance
tightens. Does not purport to prove alternative *exact* LP optima.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BUDGETS=("absolute_0p05","absolute_0p20","archived_1e-9")
GROUPS={1:("Arizona p28",29352.336139),7:("Wyoming p24",1616.753223)}

def validate(frame):
    required={"source_shape_group","state","reeds_zone","tolerance_label",
      "allowed_extra_cost_usd","original_optimum_cost_usd",
      "baseline_window_discharge_mwh","minimum_window_discharge_mwh",
      "maximum_window_discharge_mwh","window_discharge_span_mwh",
      "minimum_schedule_cost_gap_usd","maximum_schedule_cost_gap_usd"}
    if not required.issubset(frame):
        raise ValueError("Missing source-reconciled tolerance fields")
    if len(frame)!=6 or frame.duplicated(["source_shape_group","tolerance_label"]).any():
        raise ValueError("Expected six source-original cost tolerance envelopes")
    if set(frame.source_shape_group)!=set(GROUPS):
        raise ValueError("Wrong source-demand groups")
    numbers=["allowed_extra_cost_usd","original_optimum_cost_usd","baseline_window_discharge_mwh",
      "minimum_window_discharge_mwh","maximum_window_discharge_mwh","window_discharge_span_mwh",
      "minimum_schedule_cost_gap_usd","maximum_schedule_cost_gap_usd"]
    if not np.isfinite(frame[numbers].to_numpy(dtype=float)).all():
        raise ValueError("Nonfinite original interval source")
    if not np.allclose(frame.maximum_window_discharge_mwh-frame.minimum_window_discharge_mwh,
            frame.window_discharge_span_mwh,rtol=1e-9,atol=.02):
        raise ValueError("Discharge interval source identity mismatch")
    if (frame.minimum_window_discharge_mwh>frame.baseline_window_discharge_mwh+.05).any() or (
            frame.baseline_window_discharge_mwh>frame.maximum_window_discharge_mwh+.05).any():
        raise ValueError("Original LP schedule not inside envelope")
    if ((frame.maximum_schedule_cost_gap_usd-frame.allowed_extra_cost_usd>.02).any() or
         (frame.minimum_schedule_cost_gap_usd-frame.allowed_extra_cost_usd>.02).any()):
        raise ValueError("Cost cap certificate mismatch")
    out=frame.copy()
    for group,(name,accepted_reference) in GROUPS.items():
        a=out.loc[out.source_shape_group==group].set_index("tolerance_label")
        if set(a.index)!=set(BUDGETS):
            raise ValueError("Missing one original source tolerance")
        if not set(a.state)=={name.split()[0]}:
            raise ValueError("Original zone identity mismatch")
        if not np.isclose(a.loc["archived_1e-9","window_discharge_span_mwh"],
                          accepted_reference,rtol=1e-5,atol=.03):
            raise ValueError("Previous source-certified interval differs")
        widths=a.loc[list(BUDGETS),"window_discharge_span_mwh"].to_numpy()
        if np.any(np.diff(widths)<-1.):
            raise ValueError("Nonmonotone cost-sublevel set interval")
    return out

def draw(source,out):
    data=validate(source);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    fig,ax=plt.subplots(figsize=(9.5,5.1))
    for group,(label,_) in GROUPS.items():
        a=data[data.source_shape_group==group].set_index("tolerance_label").loc[list(BUDGETS)]
        fraction=100*a.window_discharge_span_mwh.to_numpy()/a.window_discharge_span_mwh.iloc[-1]
        ax.plot(range(3),fraction,marker="o",markersize=8,linewidth=2,label=label)
        for j,num in enumerate(fraction):
            ax.annotate(f"{num:.3f}%",(j,num),textcoords="offset points",
                        xytext=(0,-18 if group==1 else 8),ha="center",fontsize=9)
    ax.set_xticks(range(3),["$0.05","$0.20","Archived 10⁻⁹ × C*"])
    ax.set_ylim(99.97,100.012)
    ax.set_ylabel("Retained window discharge interval (% of archived interval)")
    ax.set_title("Figure S19 | Large window dispatch ambiguity persists under tighter cost caps")
    ax.legend(frameon=False,loc="lower right")
    ax.grid(alpha=.2)
    ax.set_axisbelow(True)
    fig.text(.5,.025,"Source hours 4001–4168; 2030 EFS load and synthetic Wave A. No exact alternate-optimality proof or physical UTC.",
             ha="center",fontsize=8)
    fig.tight_layout(rect=[0,.055,1,1])
    for ext in (".png",".svg"):
        fig.savefig(out/("Figure_S19_window_discharge_cost_tolerance"+ext),
                    dpi=240,bbox_inches="tight")
    plt.close(fig)
    data.to_csv(out/"paper_s_six_verified_window_cost_tolerance_intervals.csv",index=False)
    metadata={"status":"FIGURE_S19_SOURCE_VERIFIED_COST_TOLERANCE_LADDER",
       "original_optimization_cases":12,
       "source_groups":[1,7],"cost_allowances":["0.05 USD","0.20 USD","1e-9 original objective"],
       "source_hour_window":"ordinal 4001–4168, not certified UTC",
       "exact_alternate_optimality_proven":False,"actual_solar_wind":False}
    (out/"Figure_S19_manifest.json").write_text(json.dumps(metadata,indent=2)+"\n")
    return metadata

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(draw(pd.read_csv(a.source),a.out_dir),indent=2))
if __name__=="__main__":main()
