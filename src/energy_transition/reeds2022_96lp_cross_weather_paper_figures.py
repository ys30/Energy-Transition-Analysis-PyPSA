"""Paper S 96-LP four-weather-year × county-siting reproducible main-text figure.

Reads only archived authenticated 2010–2013 96-LP paired output. Makes
a four-panel illustration. These are deterministic operating value
scenarios (not future climate projections, interval-certified generation
or battery net investment revenue).
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
STATES=("AZ","CO","ID","WY")
YEARS=(2010,2011,2012,2013)
RUN_ID=43281182390
REEDS_COLUMN="energy_annuity_hurdle_usd_kwh_year_potential"
EIA_COLUMN="energy_annuity_hurdle_usd_kwh_year_EIA2025_county"

def validate(x):
    needed={"weather_year","state",REEDS_COLUMN,EIA_COLUMN,
            "spatial_weight_10usd_screen_flips"}
    if not needed.issubset(x.columns):
        raise ValueError(f"Missing source columns: {sorted(needed-set(x.columns))}")
    if len(x)!=16 or x[["weather_year","state"]].duplicated().any():
        raise ValueError("Exactly 16 unique source-backed year×state pairs required")
    if set(x.weather_year)!=set(YEARS) or set(x.state)!=set(STATES):
        raise ValueError("Year/state support differs from frozen original 96-LP run")
    s=x.set_index(["state","weather_year"]).loc[
        pd.MultiIndex.from_product([STATES,YEARS],names=["state","weather_year"])]
    a=s[REEDS_COLUMN].to_numpy(float)
    b=s[EIA_COLUMN].to_numpy(float)
    if (not np.isfinite(a).all() or not np.isfinite(b).all()
        or (a<0).any() or (b<0).any()):
        raise ValueError("Missing or physically invalid annual storage marginal value")
    flips=np.logical_xor(a>=10,b>=10)
    if not np.array_equal(flips,s["spatial_weight_10usd_screen_flips"].astype(bool)):
        raise ValueError("Archived source screening flag contradicts original objective ratios")
    pairs=np.array([(st,y) for st in STATES for y in YEARS],dtype=object)
    if [tuple(v) for v in pairs[flips]] != [("AZ",2012)]:
        raise ValueError("Frozen source shows only AZ 2012 illustrative screen crossing")
    anchors_a=np.array([11.067844,12.016612,10.955400,12.821096])
    anchors_b=np.array([10.726983,11.421001,9.868276,12.842341])
    if not np.allclose(a[:4],anchors_a,rtol=0,atol=.0005) or not np.allclose(b[:4],anchors_b,rtol=0,atol=.0005):
        raise ValueError("Original Arizona 96-LP source archive was changed")
    return s,a,b,flips

def run(source,out):
    s,a,b,flips=validate(pd.read_csv(source))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    out=Path(out)
    out.mkdir(parents=True,exist_ok=True)
    fig,axs=plt.subplots(2,2,figsize=(10.8,7.4),sharex=True,layout="constrained")
    colors=("#2764B2","#DD744A")
    for i,(ax,st) in enumerate(zip(axs.flat,STATES)):
        x=np.asarray(YEARS)
        v0=a[i*4:(i+1)*4];v1=b[i*4:(i+1)*4]
        ax.plot(x,v0,marker="o",lw=2,color=colors[0],label="ReEDS potential counties")
        ax.plot(x,v1,marker="s",lw=2,color=colors[1],label="EIA 2025 operating county shares")
        ax.axhline(10,ls="--",lw=1.1,c="0.42")
        ax.set_title({"AZ":"Arizona","CO":"Colorado","ID":"Idaho","WY":"Wyoming"}[st],loc="left",fontweight="bold")
        ax.set_ylim(0,15)
        ax.set_xticks(x)
        ax.grid(axis="y",alpha=.18)
        if i in (0,2):ax.set_ylabel("4→8h operating-value ceiling\n($/added kWh-year)")
        if i in (2,3):ax.set_xlabel("Original ReEDS historical weather reference")
        if st=="AZ":
            ax.annotate("2012: $10 screen flips",xy=(2012,v1[2]),xytext=(2010.1,6.8),
                arrowprops={"arrowstyle":"->","lw":1.0},fontsize=9)
    handles,labels=axs[0,0].get_legend_handles_labels()
    fig.legend(handles,labels,ncol=2,loc="outside upper center",bbox_to_anchor=(.5,1.04),fontsize=10)
    fig.suptitle("Storage duration value depends on renewable county siting and weather year",y=1.09,fontsize=13)
    for suffix in ("png","pdf"):
        fig.savefig(out/f"paper_s_96lp_weather_x_county_siting_main_figure.{suffix}",dpi=250,bbox_inches="tight")
    plt.close(fig)
    fig2,ax=plt.subplots(figsize=(8.4,4.5),layout="constrained")
    matrix=(b-a).reshape(4,4)
    lim=max(.1,float(np.abs(matrix).max()))
    im=ax.imshow(matrix,cmap="RdBu_r",vmin=-lim,vmax=lim,aspect="auto")
    ax.set_xticks(np.arange(4),YEARS)
    ax.set_yticks(np.arange(4),STATES)
    ax.set_xlabel("Historical ReEDS weather reference")
    ax.set_ylabel("State")
    for row in range(4):
        for col in range(4):
            val=matrix[row,col]
            ax.text(col,row,f"{val:+.2f}",ha="center",va="center",
                    color="white" if abs(val)>.62*lim else "black",fontsize=10)
    bar=fig2.colorbar(im,ax=ax,shrink=.86)
    bar.set_label("EIA 2025 county shares minus ReEDS potential\n($/added kWh-year)")
    ax.set_title("County geography changes the marginal storage operating-value ceiling")
    for suffix in ("png","pdf"):
        fig2.savefig(out/f"paper_s_96lp_weather_x_siting_difference_heatmap.{suffix}",dpi=250)
    plt.close(fig2)
    manifest={
      "status":"PAPER_S_AUTHENTICATED_96LP_CROSS_WEATHER_FIGURE_PASS",
      "source_original_96LP_run":RUN_ID,
      "source_original_state_weather_pairs":16,
      "source_original_LPs":96,
      "source_weather_years":list(YEARS),
      "threshold_flips":int(flips.sum()),
      "flip_state_weather":[{"state":st,"weather_year":int(y)} for (st,y),flip in
        zip([(st,y) for st in STATES for y in YEARS],flips) if flip],
      "chart_difference_EIA_minus_ReEDS_range":[float(matrix.min()),float(matrix.max())],
      "source_native_point_CF_not_hour_integral":True,
      "nonleap_Feb29_synthetically_interpolated":True,
      "source_weather_is_not_future_climate_change":True,
      "EIA_2025_siting_is_not_projected_2030_actual_fleet":True,
      "battery_capex_and_market_profit_not_modeled":True}
    (out/"paper_s_96lp_weather_x_siting_figures_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest,indent=2))
    return manifest

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    run(a.source,a.out)
if __name__=="__main__":main()
