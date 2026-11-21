"""Create paper-ready 3×3 conditional siting-effect maps from admitted LP CSVs.

This is postprocessing, not a new solver or climate attribution. It is safe to
run ONLY after the 2880-LP workflow finishes successfully.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
from energy_transition.paper_s_siting_design_grid_3x3_2880lp import RATIOS,WIND_SHARES,STATES

def summarize(pairs):
    required={"weather_year","state","renewable_peak_ratio","wind_share_ac",
              "siting_effect_eia_minus_potential"}
    if not required.issubset(pairs.columns) or len(pairs)!=540 or pairs[list(required-{ "siting_effect_eia_minus_potential"})].duplicated().any():
        raise ValueError("Missing/duplicate 540 design-grid matched effects")
    expected=pd.MultiIndex.from_product(
        [STATES,RATIOS,WIND_SHARES],names=["state","renewable_peak_ratio","wind_share_ac"])
    z=pairs.groupby(["state","renewable_peak_ratio","wind_share_ac"]).agg(
        weather_years=("weather_year","nunique"),
        median_effect=("siting_effect_eia_minus_potential","median"),
        min_effect=("siting_effect_eia_minus_potential","min"),
        max_effect=("siting_effect_eia_minus_potential","max"),
        positive_years=("siting_effect_eia_minus_potential",lambda x:int((x>0).sum())),
        negative_years=("siting_effect_eia_minus_potential",lambda x:int((x<0).sum()))
    )
    if len(z)!=36 or len(expected.difference(z.index)) or not z.weather_years.eq(15).all():
        raise ValueError("Incomplete 36-point 15-year state grid")
    return z.reset_index()

def run(source,out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    pairs=pd.read_csv(source)
    summary=summarize(pairs)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    summary.to_csv(out/"paper_s_design_36_grid_paper_table.csv",index=False,float_format="%.12g")
    for key,filename,vmin,vmax in [
        ("median_effect","Figure_D1_3x3_spatial_weight_effect_median.png",None,None),
        ("positive_years","Figure_D2_3x3_positive_weather_year_counts.png",0,15),
    ]:
        fig,axes=plt.subplots(2,2,figsize=(10.0,8.4),constrained_layout=True)
        values=summary[key].to_numpy(float)
        lim=max(abs(values.min()),abs(values.max())) if key=="median_effect" else None
        if key=="median_effect": vmin,vmax=-lim,lim
        for ax,st in zip(axes.ravel(),STATES):
            s=summary[summary.state==st].pivot(
                index="renewable_peak_ratio",columns="wind_share_ac",values=key)
            s=s.reindex(index=RATIOS,columns=WIND_SHARES)
            im=ax.imshow(s.values,origin="lower",aspect="auto",vmin=vmin,vmax=vmax,
                         cmap="coolwarm" if key=="median_effect" else "viridis")
            ax.set_xticks(range(3),[f"{int(100*w)}%" for w in WIND_SHARES])
            ax.set_yticks(range(3),[str(r) for r in RATIOS])
            ax.set_title(st)
            ax.set_xlabel("Wind fraction of wind+PV AC capacity")
            ax.set_ylabel("Renewable AC / load peak")
            for i in range(3):
                for j in range(3):
                    value=s.values[i,j]
                    ax.text(j,i,f"{value:+.2f}" if key=="median_effect" else f"{int(value)}/15",
                            ha="center",va="center",fontsize=9,color="black")
            ax.add_patch(plt.Rectangle((0.5,0.5),1.0,1.0,fill=False,edgecolor="black",lw=2))
        fig.colorbar(im,ax=axes.ravel().tolist(),shrink=.8,label=(
            "Median EIA minus potential storage value, USD/(added kWh-year)"
            if key=="median_effect" else "Weather years with positive siting effect (out of 15)"))
        fig.suptitle(("Conditional 4→8 h storage-value effect across renewable design points"
                     if key=="median_effect" else
                     "Directional robustness across 15 weather years"),fontsize=13)
        fig.savefig(out/filename,dpi=260,bbox_inches="tight")
        plt.close(fig)
    md=["# Paper S: conditional renewable-mix sensitivity (3×3)","",
        "Generated from the successful 2880-new-LP result CSV; not from an inferred projection.","",
        "| State | R ratio | Wind share | Median siting effect | Positive years / 15 |",
        "|---|---:|---:|---:|---:|"]
    for _,r in summary.iterrows():
        md.append(f"| {r.state} | {r.renewable_peak_ratio:.1f} | {r.wind_share_ac:.0%} | {r.median_effect:+.3f} | {int(r.positive_years)}/15 |")
    md.extend(["",
        "Baseline (R=1.5, wind share=50%) highlighted with a black square.",
        "The results are conditional on a single-node perfect-foresight dispatch LP, fixed weather-2012-support 2030 demand, a 90% roundtrip storage efficiency, fixed battery power 25% of peak load, and trapezoid point-to-hour source CF approximation.",
        "A positive sign is not evidence that EIA weights are observationally more accurate; years are not independent random replicates."])
    (out/"PAPER_S_3x3_RESULTS_TABLE_AND_CAPTIONS.md").write_text("\n".join(md)+"\n",encoding="utf-8")
    return summary

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--paired-csv",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    run(a.paired_csv,a.out)
if __name__=="__main__":main()
