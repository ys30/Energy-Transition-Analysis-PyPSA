"""Source-derived publication figures for Paper T (NOT a physical UTC comparison).

Input 1: 33 state/year nonwrapping EFS2020 versus ReEDS2022 source-index
lag diagnostics archived in passing Actions run 42122065064.
Input 2: Idaho original-source frozen Transportation shift 2030--2050,
passing Actions run 42131969905.
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
STATES=("AZ","CA","CO","ID","MT","NM","NV","OR","UT","WA","WY")
NOTE="Published source-index comparison; lag is NOT a certified EFS2020-to-UTC conversion."

def validate(nonwrap,transfer):
    needed={"year","state","best_nonwrap_offset","best_nonwrap_mae_mw","second_best_mae_mw","best_nonwrap_compared_hours"}
    if not needed.issubset(nonwrap):raise ValueError("Missing archived source lag metrics")
    if len(nonwrap)!=33 or nonwrap.duplicated(["year","state"]).any() or set(nonwrap.year)!=set(YEARS):
        raise ValueError("Incomplete original 33 state/year cases")
    for year,g in nonwrap.groupby("year"):
        if set(g.state)!=set(STATES):raise ValueError("Incomplete year source states")
    if (nonwrap.best_nonwrap_compared_hours<8748).any():raise ValueError("Unexpected source overlap")
    if (nonwrap.best_nonwrap_mae_mw<0).any() or (nonwrap.second_best_mae_mw<nonwrap.best_nonwrap_mae_mw).any():
        raise ValueError("Invalid lag source residuals")
    required={"planning_year","baseline_firsthalf_mae_mw","fixed_2030_transport_plus1_firsthalf_mae_mw",
              "baseline_heldout_mae_mw","fixed_2030_transport_plus1_heldout_mae_mw"}
    if not required.issubset(transfer):raise ValueError("Missing frozen original-sector outcomes")
    if len(transfer)!=3 or set(transfer.planning_year)!=set(YEARS) or transfer.planning_year.duplicated().any():
        raise ValueError("Incomplete frozen candidate cross-year results")
    return nonwrap.sort_values(["year","state"]),transfer.sort_values("planning_year")

def generate(nonwrap,transfer,out):
    a,b=validate(nonwrap,transfer)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    # T2: full source scope with 2030 state lag on left and residual on right.
    first=a[a.year==2030].set_index("state").loc[list(STATES)]
    fig,(ax1,ax2)=plt.subplots(1,2,figsize=(12.4,5),gridspec_kw={"width_ratios":[.85,1.15]})
    y=np.arange(len(STATES))
    ax1.barh(y,first.best_nonwrap_offset,color="#4c78a8")
    ax1.set_yticks(y,STATES);ax1.invert_yaxis()
    ax1.set(xlabel="Best nonwrapping source-index lag (h)",title="Source index displacement (2030)")
    ax1.set_xticks([-3,-2,0]);ax1.grid(axis="x",alpha=.2)
    # log axis to retain both near-.25 and Idaho >17 MW; label explicitly
    ax2.barh(y,first.best_nonwrap_mae_mw,color=["#e45756" if s=="ID" else "#72b7b2" for s in STATES])
    ax2.set_yticks(y,[""]*len(STATES));ax2.invert_yaxis()
    ax2.set_xscale("log");ax2.set(xlabel="Mean absolute source discrepancy (MW; log scale)",
        title="After best lag (2030, no year-end wrapping)")
    ax2.grid(axis="x",alpha=.2)
    fig.suptitle("EFS 2020 vs independent ReEDS 2022: original-source numerical lag",y=1.03)
    fig.text(.5,-.02,NOTE,ha="center",fontsize=8)
    fig.tight_layout()
    for ext in ("svg","png"):fig.savefig(out/f"figure_T2_source_lag_2030.{ext}",dpi=200,bbox_inches="tight")
    plt.close(fig)
    # T4: strict same fixed candidate, no reranking on 2040/2050
    x=np.arange(3);w=.34
    first_diff=(b.baseline_firsthalf_mae_mw-b.fixed_2030_transport_plus1_firsthalf_mae_mw).to_numpy()
    second_diff=(b.baseline_heldout_mae_mw-b.fixed_2030_transport_plus1_heldout_mae_mw).to_numpy()
    fig,ax=plt.subplots(figsize=(8.5,4.8))
    ax.bar(x-w/2,first_diff,w,label="First half",color="#4c78a8")
    ax.bar(x+w/2,second_diff,w,label="Held-out second half",color="#e45756")
    ax.axhline(0,color="black",linewidth=.8)
    ax.set_xticks(x,[str(year) for year in YEARS])
    ax.set(xlabel="EFS projected planning year",ylabel="Reduction in cross-release MAE (MW)",
           title="Frozen 2030 Transportation +1h candidate: evaluation-window reversal")
    ax.legend(frameon=False)
    ax.grid(axis="y",alpha=.2);ax.set_axisbelow(True)
    fig.text(.5,-.02,"Positive = smaller discrepancy. Frozen source-index hypothesis; no physical Idaho timezone attribution.",ha="center",fontsize=8)
    fig.tight_layout()
    for ext in ("svg","png"):fig.savefig(out/f"figure_T4_frozen_shift_holdout.{ext}",dpi=200,bbox_inches="tight")
    plt.close(fig)
    return {
      "status":"PAPER_T_FIGURES_SOURCE_DERIVED","source_state_year_lag_pairs":33,
      "source_frozen_rule_years":3,"figures":["figure_T2_source_lag_2030","figure_T4_frozen_shift_holdout"],
      "frozen_shift_first_half_improvements_mw":dict(zip(map(str,YEARS),map(float,first_diff))),
      "frozen_shift_heldout_improvements_mw":dict(zip(map(str,YEARS),map(float,second_diff))),
      "EFS2020_physical_UTC_certified":False,
      "Idaho_geographical_timezone_identified":False,
      "wind_solar_resource_join_admitted":False}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--nonwrap",required=True,type=Path)
    p.add_argument("--transfer",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    result=generate(pd.read_csv(args.nonwrap),pd.read_csv(args.transfer),args.out)
    (args.out/"manifest.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
