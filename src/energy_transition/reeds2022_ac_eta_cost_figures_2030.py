"""Paper S accepted-source common-AC 108 LP robustness plot panels.

Read archived successful 36-pair source results, with fixed 2012
reference weather and 2030 synthetic scenario load. Generated charts
are descriptive sensitivity maps, not statistical confidence regions.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

STATES=("AZ","CO","ID","WY")
EFFICIENCIES=(.80,.90,.95)
COSTS=(60.,90.,120.)
HURDLE=10.
SOURCE_RUN=43060677031

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    df=pd.read_csv(a.source)
    keys=["state","roundtrip_efficiency","firm_cost_usd_per_mwh"]
    if len(df)!=36 or df.duplicated(keys).any() or set(df.state)!=set(STATES):
        raise ValueError("Incomplete source 36-case grid")
    out=Path(a.out)
    out.mkdir(parents=True,exist_ok=True)
    report={"status":"COMMON_AC_108_LP_EFFICIENCY_COST_FOUR_STATE_HEATMAPS",
            "source_run":SOURCE_RUN,"scenario_triplets":36,
            "figures":8,"conditional_annual_energy_cost_usd_kwh_year":HURDLE,
            "original_source_profiles_unchanged":True,
            "battery_capex_NPV_or_reliability_certified":False,
            "states_over_hypothetical_hurdle":{}}
    for state in STATES:
        subset=df[df.state.eq(state)]
        mat=subset.pivot(index="roundtrip_efficiency",
                         columns="firm_cost_usd_per_mwh",
                         values="incremental_energy_annuity_hurdle_usd_per_kwh_year")
        if list(mat.index)!=list(EFFICIENCIES) or list(mat.columns)!=list(COSTS):
            raise ValueError(f"Missing efficiency-cost grid for {state}")
        vals=mat.to_numpy(float)
        report["states_over_hypothetical_hurdle"][state]=int((vals>=HURDLE).sum())
        for style in ("absolute","above_10"):
            plot=vals if style=="absolute" else vals-HURDLE
            fig,ax=plt.subplots(figsize=(7.1,4.8),layout="constrained")
            v=ax.imshow(plot,aspect="auto",cmap="viridis" if style=="absolute" else "coolwarm")
            fig.colorbar(v,ax=ax,label="Incremental energy annuity ceiling ($/kWh-year)" if style=="absolute"
                         else "Margin above illustrative $10/kWh-year energy annuity")
            ax.set_xticks(range(3),[f"${x:.0f}" for x in COSTS])
            ax.set_yticks(range(3),[f"{x:.0%}" for x in EFFICIENCIES])
            ax.set_xlabel("Illustrative firm marginal cost ($/MWh)")
            ax.set_ylabel("Battery round-trip efficiency")
            ax.set_title(f"{state}: 2030 demand, 2012 weather · 4h → 8h · common AC")
            for yi in range(3):
                for xi in range(3):
                    ax.text(xi,yi,f"{plot[yi,xi]:.2f}",ha="center",va="center",
                            fontsize=10,color="white" if plot[yi,xi]<(plot.max()+plot.min())/2 else "black")
            fig.savefig(out/f"paper_s_2030_{state}_ac_eta_cost_{style}.png",dpi=250)
            fig.savefig(out/f"paper_s_2030_{state}_ac_eta_cost_{style}.pdf")
            plt.close(fig)
    if report["states_over_hypothetical_hurdle"]!={"AZ":5,"CO":0,"ID":0,"WY":0}:
        raise ValueError("Source robustness classification differs from archived 108 LP")
    (out/"paper_s_2030_ac_eta_cost_eight_figures_manifest.json").write_text(
         json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
    print("COMMON_AC_SOURCE_108_LP_EIGHT_COST_ETA_FIGURES_PASS")

if __name__=="__main__":
    main()
