"""Paper T Figure T3: published ReEDS2022 reference-month × reference-hour error.

This is a diagnostic visualization of original EFS2020 vs independently
published ReEDS2022 source-index numerical mismatch, NOT an EFS physical clock.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

YEARS=(2030,2040,2050)
def validate(grouped):
    required={"year","state","group_type","reference_index_label","compared_hours","mean_absolute_error_mw"}
    if not required.issubset(grouped):raise ValueError("Missing source archived grouped metrics")
    if not set(grouped.state)=={"AZ","CA","ID"} or set(grouped.year)!=set(YEARS):
        raise ValueError("Missing source control years or state")
    if len(grouped)!=324 or grouped.duplicated(["year","state","group_type","reference_index_label"]).any():
        raise ValueError("Incomplete source-group population")
    if (grouped.compared_hours<=0).any() or (grouped.mean_absolute_error_mw<0).any():
        raise ValueError("Invalid grouped source errors")
    for (year,state),g in grouped.groupby(["year","state"]):
        month=g[g.group_type=="month"]
        hour=g[g.group_type=="hour"]
        if set(month.reference_index_label)!=set(range(1,13)) or set(hour.reference_index_label)!=set(range(24)):
            raise ValueError("Incorrect original month/hour group coverage")
    return grouped

def make(grouped,out):
    d=validate(grouped)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    # Data are separate month means and clock-hour means; a joint month×hour
    # heatmap CANNOT be reconstructed from them. We explicitly avoid inventing
    # the missing joint bins: figure uses month and hour marginal profiles.
    fig,axes=plt.subplots(2,3,figsize=(12.8,6.9),sharex="row")
    for i,year in enumerate(YEARS):
        for j,(dimension,labels) in enumerate([("month",range(1,13)),("hour",range(24))]):
            ax=axes[j,i]
            for state,color in (("ID","#d45047"),("AZ","#4c78a8"),("CA","#72b7b2")):
                a=d[(d.year==year)&(d.state==state)&(d.group_type==dimension)].set_index("reference_index_label")
                ax.plot(list(labels),a.loc[list(labels),"mean_absolute_error_mw"],label=state,color=color,
                        linewidth=1.8 if state=="ID" else 1.0,alpha=1 if state=="ID" else .85)
            if j==0:ax.set_title(str(year))
            if i==0:ax.set_ylabel("Residual MAE (MW)")
            ax.set_xlabel("ReEDS 2022 reference " + ("2012 month" if dimension=="month" else "CST hour"))
            ax.grid(alpha=.15)
            if j==0 and i==2:ax.legend(frameon=False)
    fig.suptitle("Idaho mismatch persists across published reference months and hours",y=1.02)
    fig.text(.5,-.01,"Two separate marginal curves, NOT a month×hour heatmap. ReEDS2022 reference clock ≠ certified EFS2020 physical clock.",
             ha="center",fontsize=8)
    fig.tight_layout()
    for ext in ("svg","png"):fig.savefig(out/f"figure_T3_idaho_month_hour_marginals.{ext}",dpi=200,bbox_inches="tight")
    plt.close(fig)
    return {"status":"PAPER_T_SOURCE_REFERENCE_MARGINAL_FIGURE_GENERATED",
            "archived_group_rows":324,"states":["ID","AZ","CA"],"years":list(YEARS),
            "figure_files":["figure_T3_idaho_month_hour_marginals.svg","figure_T3_idaho_month_hour_marginals.png"],
            "joint_month_by_hour_observations_available":False,
            "figure_is_joint_heatmap":False,
            "ReEDS_reference_clock_is_EFS2020_physical_UTC":False}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--grouped",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    r=make(pd.read_csv(a.grouped),a.out)
    (a.out/"manifest.json").write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps(r,indent=2))
if __name__=="__main__":main()
