"""Figure S18: two source-ordinal-window discharge intervals under original cost cap.

No pointwise-hourly discharge bounds, and windows are not authenticated UTC.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

WINDOWS=("early_1_168","middle_4001_4168")
GROUPS={1:"Arizona p28",7:"Wyoming p24"}
REQUIRED={"source_shape_group","state","reeds_zone","window",
          "baseline","min","max","span_mwh","relative_span_pct_of_baseline"}

def validate(df):
    if not REQUIRED.issubset(df):raise ValueError("Missing original archived discharge interval columns")
    if len(df)!=4 or df.duplicated(["source_shape_group","window"]).any():
        raise ValueError("Expected four source-backed window intervals")
    if set(df.source_shape_group)!={1,7}:
        raise ValueError("Wrong source demand group")
    for group in (1,7):
        part=df[df.source_shape_group==group]
        if set(part.window)!=set(WINDOWS):
            raise ValueError("Missing source-ordinal window")
    if not np.isfinite(df[["baseline","min","max","span_mwh"]].to_numpy(dtype=float)).all():
        raise ValueError("Nonfinite interval")
    if (df["min"]<-.02).any() or (df["max"]<df["min"]).any():
        raise ValueError("Invalid nonnegative window discharge bounds")
    if not np.allclose(df["max"]-df["min"],df["span_mwh"],rtol=1e-9,atol=.01):
        raise ValueError("Source interval width does not reconcile")
    if (df["baseline"]<df["min"]-.03).any() or (df["baseline"]>df["max"]+.03).any():
        raise ValueError("Original discharge outside source interval")
    if (df[(df.source_shape_group==1)].state!="Arizona").any() or (df[(df.source_shape_group==7)].state!="Wyoming").any():
        raise ValueError("Source state identity mismatch")
    return df

def render(df,out):
    a=validate(df);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    fig,axes=plt.subplots(1,2,figsize=(12.4,4.5))
    for ax,group in zip(axes,(1,7)):
        sub=a[a.source_shape_group==group].set_index("window").loc[list(WINDOWS)]
        ys=np.array([1,0])
        vals=sub[["min","max","baseline"]].to_numpy(dtype=float)
        for yy,(low,hi,base) in zip(ys,vals):
            ax.plot([low,hi],[yy,yy],linewidth=5,solid_capstyle="round")
            ax.scatter([low,hi],[yy,yy],marker="|",s=170,zorder=3)
            ax.scatter([base],[yy],marker="o",s=45,c="black",zorder=4)
            ax.text(hi,yy+.16,f"Span {hi-low:,.1f} MWh",fontsize=8,ha="right")
        ax.set_yticks(ys,["Source hours 1–168","Source hours 4001–4168"])
        ax.set_xlim(left=-.02*max(1,sub["max"].max()),right=1.10*max(1,sub["max"].max()))
        ax.set_ylim(-.5,1.55)
        ax.set_xlabel("Discharge to load within selected window (MWh)")
        ax.set_title(GROUPS[group])
        ax.grid(axis="x",alpha=.2);ax.set_axisbelow(True)
    fig.suptitle("Figure S18 | Annual dispatch stability can mask window-level redistribution",fontsize=13)
    fig.text(.5,.045,"Horizontal range: min–max under same original cost cap; black dot: original LP schedule. Separate x-axis scales.",ha="center",fontsize=8)
    fig.text(.5,.012,"Source-hour ordinals, not certified calendar weeks. Synthetic supply, no storage CAPEX or actual Western grid dispatch.",ha="center",fontsize=8)
    fig.tight_layout(rect=[0,.085,1,.89])
    for ext in (".png",".svg"):
        fig.savefig(out/("Figure_S18_window_discharge_redistribution"+ext),dpi=230,bbox_inches="tight")
    plt.close(fig)
    a.to_csv(out/"paper_s_four_source_hour_window_intervals.csv",index=False)
    summary={"status":"FIGURE_S18_SOURCE_CERTIFIED_FOUR_168H_WINDOW_INTERVALS",
        "windows":[list(WINDOWS),[168,168]],
        "comparison":"window-specific near-optimal annual original-cost-capped discharge",
        "pointwise_hourly_bounds":False,"physical_UTC_certified":False,
        "resource_profiles_observed":False,"western_OPF":False}
    (out/"Figure_S18_manifest.json").write_text(json.dumps(summary,indent=2)+"\n")
    return summary

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--out-dir",required=True,type=Path)
    args=p.parse_args()
    print(json.dumps(render(pd.read_csv(args.source),args.out_dir),indent=2))
if __name__=="__main__":main()
