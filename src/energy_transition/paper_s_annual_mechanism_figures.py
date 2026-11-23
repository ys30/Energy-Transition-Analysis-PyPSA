"""Publication-ready descriptive annual input-only mechanism figures.
Reads only source-audited 15-year Y2/Y3 outputs; never invents result values.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

STATES=("AZ","CO","ID","WY")
HORIZONS=("daily","weekly","annual")

def validate(pair,summary):
    required={"state","renewable_peak_ratio","weather_year","lp_spatial_effect_usd_kwh_year"}
    required.update(f"{h}_spatial_effect_mwh" for h in HORIZONS)
    if not required.issubset(pair.columns):
        raise ValueError("Missing source-pinned annual paired values")
    if len(pair)!=60 or pair.duplicated(["state","weather_year","renewable_peak_ratio"]).any():
        raise ValueError("Exactly 60 matched annual paired state-year observations required")
    if len(summary)!=4 or set(summary.state)!=set(STATES):
        raise ValueError("Require original four states, full year summaries")
    if not summary.n_matched_weather_years.eq(15).all():
        raise ValueError("Each state must contain all 15 weather-year spatial pairs")
    if (pair.groupby("state").size().reindex(STATES)!=15).any():
        raise ValueError("State-level matched years incomplete")
    numeric_fields=sorted(required-{"state"})
    vals=pair[numeric_fields].select_dtypes(include="number")
    if not np.isfinite(vals.to_numpy(dtype=float)).all():
        raise ValueError("Nonfinite annual source/LP paired effects")
    expected={"AZ":1.5,"CO":2.,"ID":1.5,"WY":1.5}
    for state,ratio in expected.items():
        if not np.allclose(pair.loc[pair.state.eq(state),"renewable_peak_ratio"],ratio):
            raise ValueError("State-specific prescribed penetration drift")
    for _,r in summary.iterrows():
        x=pair[pair.state.eq(r.state)]
        lp=x.lp_spatial_effect_usd_kwh_year
        for h in HORIZONS:
            a=x[f"{h}_spatial_effect_mwh"]
            correlation=(a.corr(lp) if a.std()>1e-9 and lp.std()>1e-9 else np.nan)
            recorded=r[f"{h}_pearson_spatial_effect"]
            if pd.notna(correlation) and not np.isclose(correlation,recorded,atol=2e-6):
                raise ValueError("Published figure disagrees with source summary")
    return True

def render(pair,summary,out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    validate(pair,summary)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    source=summary.set_index("state").loc[list(STATES)]
    correlations=source[[f"{h}_pearson_spatial_effect" for h in HORIZONS]].to_numpy(float)
    fig,ax=plt.subplots(figsize=(7.8,5.0))
    im=ax.imshow(correlations,cmap="RdBu_r",vmin=-1,vmax=1,aspect="auto")
    ax.set_xticks(range(3),["24 h resets","168 h resets","8760 h continuous"])
    ax.set_yticks(range(4),["AZ (R=1.5)","CO (R=2.0)","ID (R=1.5)","WY (R=1.5)"])
    for i in range(4):
        for j in range(3):
            v=correlations[i,j]
            ax.text(j,i,"NA" if not np.isfinite(v) else f"{v:+.2f}",ha="center",va="center",
                    color="white" if np.isfinite(v) and abs(v)>.55 else "black",fontsize=11)
    fig.colorbar(im,ax=ax,label="Pearson r: input-only MWh siting effect vs annual LP value effect")
    ax.set_title("Paper S — Annual input-only mechanism sensitivity (15 source weather years)")
    fig.text(.02,.015,"Paired source-weather-year spatial differences; descriptive, not causal or observed revenue.",
             fontsize=8)
    fig.tight_layout(rect=(0,.055,1,1))
    fig.savefig(out/"paper_s_annual_input_only_mechanism_heatmap.png",dpi=240)
    fig.savefig(out/"paper_s_annual_input_only_mechanism_heatmap.pdf")
    plt.close(fig)

    fig,axs=plt.subplots(2,2,figsize=(10,7.5),sharex=False,sharey=False)
    for state,ax in zip(STATES,axs.flat):
        p=pair[pair.state.eq(state)].sort_values("weather_year")
        ax.scatter(p.annual_spatial_effect_mwh/1000,
                   p.lp_spatial_effect_usd_kwh_year,s=26)
        ax.axhline(0,linewidth=.8,color="gray")
        ax.axvline(0,linewidth=.8,color="gray")
        for _,r in p.iterrows():
            ax.annotate(str(int(r.weather_year)),(r.annual_spatial_effect_mwh/1000,
                        r.lp_spatial_effect_usd_kwh_year),fontsize=6,xytext=(3,2),
                        textcoords="offset points")
        ax.set_title(f"{state} — 15 source years")
        ax.set_xlabel("Annual max renewable-only 4→8 h siting effect (10³ MWh)")
        ax.set_ylabel("Original annual LP siting effect (USD / added kWh-year)")
    fig.suptitle("Paper S — within-year county-weight contrasts: annual physical vs model-economic",fontsize=12)
    fig.tight_layout(rect=(0,0,1,.97))
    fig.savefig(out/"paper_s_annual_input_only_vs_lp_scatter.png",dpi=240)
    fig.savefig(out/"paper_s_annual_input_only_vs_lp_scatter.pdf")
    plt.close(fig)
    return {"figures":4,"states":4,"weather_years_per_state":15,
            "relationship":"descriptive_input_only_MWh_vs_original_LP_siting_effect"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pairs",type=Path,required=True)
    p.add_argument("--summary",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    print(render(pd.read_csv(a.pairs),pd.read_csv(a.summary),a.out))

if __name__=="__main__":main()
