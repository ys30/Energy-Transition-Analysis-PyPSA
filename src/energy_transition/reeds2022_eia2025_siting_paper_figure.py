"""Paper S main-text source-verified county siting 24-LP counterfactual figure.

No new optimization or fabricated uncertainty. EIA2025 observed county
capacity-share source is an external 2025 siting snapshot, not the 2030
future fleet. 2012 ReEDS resource weather is not true-hour-integrated.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

EXPECTED_STATES=("AZ","CO","ID","WY")
SOURCE_RUN=43159121663

def prepare(frame):
    required={"state",
        "incremental_4_to_8h_energy_annuity_usd_per_kwh_year_potential",
        "incremental_4_to_8h_energy_annuity_usd_per_kwh_year_EIA2025_county",
        "10usd_energy_annuity_screen_flips"}
    if not required.issubset(frame.columns) or len(frame)!=4:
        raise ValueError("Incomplete 24-LP source comparison")
    if frame.state.duplicated().any() or set(frame.state)!=set(EXPECTED_STATES):
        raise ValueError("Four source-matched states required")
    s=frame.set_index("state").loc[list(EXPECTED_STATES)]
    a=s.incremental_4_to_8h_energy_annuity_usd_per_kwh_year_potential.to_numpy(float)
    b=s.incremental_4_to_8h_energy_annuity_usd_per_kwh_year_EIA2025_county.to_numpy(float)
    if not np.isfinite(a).all() or not np.isfinite(b).all() or (a<0).any() or (b<0).any():
        raise ValueError("Nonphysical value of LP annuity ceiling")
    flips=(a>=10)!=(b>=10)
    if list(flips)!=list(s["10usd_energy_annuity_screen_flips"].astype(bool)):
        raise ValueError("Source CSV inconsistent with $10 threshold decisions")
    if flips.sum()!=1 or not flips[0]:
        raise ValueError("Archived source must preserve Arizona-only threshold reversal")
    anchor=(10.955400,6.220671,4.134846,3.540569)
    if not np.allclose(a,anchor,atol=1e-3,rtol=0):
        raise ValueError("Original frozen common-AC source baseline not reproduced")
    return a,b,flips

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    x=p.parse_args()
    df=pd.read_csv(x.source)
    a,b,flips=prepare(df)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    out=Path(x.out);out.mkdir(parents=True,exist_ok=True)
    fig,ax=plt.subplots(figsize=(8.1,5.3),layout="constrained")
    xloc=np.arange(4)
    width=.35
    first=ax.bar(xloc-width/2,a,width,label="ReEDS developable resource potential")
    second=ax.bar(xloc+width/2,b,width,label="EIA 2025 operating county shares")
    for bars in (first,second):
        for bar in bars:
            ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+.15,
                    f"{bar.get_height():.2f}",ha="center",va="bottom",fontsize=9)
    ax.axhline(10,color="gray",linestyle="--",linewidth=1.5,
               label="Illustrative $10/kWh-year energy-cost-only screen")
    ax.set_xticks(xloc,EXPECTED_STATES)
    ax.set_ylim(0,max(12.,float(np.max(np.r_[a,b]))+1.4))
    ax.set_ylabel("Additional 4→8h duration operating-value ceiling ($/kWh-year)")
    ax.set_title("County siting sensitivity: 2012 weather, 2025 sites, 2030 demand")
    ax.annotate("Arizona threshold reversal",xy=(xloc[0]+width/2,b[0]),
                xytext=(.48,11.75),arrowprops={"arrowstyle":"->"},fontsize=9)
    ax.legend(fontsize=8,loc="upper right")
    for ext in ("png","pdf"):
        fig.savefig(out/f"paper_s_fig_county_siting_24_lp_4_to_8h.{ext}",dpi=250)
    plt.close(fig)
    report={
        "status":"PAPER_S_AUTHENTICATED_24LP_COUNTY_SITING_ANNUITY_FIGURE_PASS",
        "source_workflow_run":SOURCE_RUN,
        "archived_source_LPs":24,
        "plot_comparisons":4,
        "conditional_10usd_threshold_flips":int(flips.sum()),
        "threshold_flip_states":[EXPECTED_STATES[i] for i,x in enumerate(flips) if x],
        "siting_year":2025,"original_weather_year":2012,"projected_demand_year":2030,
        "not_current_installed_generator_generation":True,
        "not_true_hour_integrated_energy":True,
        "not_actual_2030_fleet_or_battery_profit":True}
    (out/"paper_s_fig_county_siting_24_lp_manifest.json").write_text(
        json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
    print("PAPER_S_24LP_SOURCE_COUNTY_SITING_FIGURE_PASS")

if __name__=="__main__":main()
