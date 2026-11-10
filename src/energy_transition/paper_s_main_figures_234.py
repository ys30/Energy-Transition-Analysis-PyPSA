"""Paper S journal-candidate Figures 2–4 from two accepted full-year LP archives.

Figure 2: 2030 unused assumed renewable potential / available potential.
Figure 3: wave-A firm generation / projected demand across planning years.
Figure 4: marginal changes in original illustrative LP variable objective.
No real renewables, physical UTC, capital economics, or network OPF implied.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

YEARS=(2030,2040,2050)
SHAPES=("flat_50pct","ordinal24_wave_A","ordinal24_wave_B")
LABELS=("Flat","Wave A","Wave B")
DURATIONS=(0,4,8)
COLORS=("#3f7599","#df8d3f","#399a87")

def certify(annual,marginals):
    k=["planning_year","synthetic_supply_shape","battery_duration_h"]
    required=set(k+["demand_mwh","renewable_available_mwh","unused_renewable_mwh",
                   "firm_generation_mwh","objective_illustrative_variable_usd"])
    if not required.issubset(annual) or len(annual)!=27 or annual.duplicated(k).any():
        raise ValueError("Incomplete 27 original annual source cases")
    if set(annual.planning_year)!=set(YEARS) or set(annual.synthetic_supply_shape)!=set(SHAPES) or set(annual.battery_duration_h)!=set(DURATIONS):
        raise ValueError("Original annual source factorial mismatched")
    mk=["planning_year","synthetic_supply_shape"]
    if len(marginals)!=9 or marginals.duplicated(mk).any() or set(marginals.planning_year)!=set(YEARS) or set(marginals.synthetic_supply_shape)!=set(SHAPES):
        raise ValueError("Incomplete independent nine original marginal cases")
    if not {"zones","source_ordinal_hours_per_case"}.issubset(marginals) or not marginals.zones.eq(20).all() or not marginals.source_ordinal_hours_per_case.eq(8760).all():
        raise ValueError("Original twenty-zone hourly coverage mismatch")
    cols=["demand_mwh","renewable_available_mwh","unused_renewable_mwh",
          "firm_generation_mwh","objective_illustrative_variable_usd"]
    if not np.isfinite(annual[cols].to_numpy(dtype=float)).all() or (annual[cols]<0).any().any():
        raise ValueError("Invalid archived original annual metrics")
    if (annual.renewable_available_mwh<=0).any() or (annual.demand_mwh<=0).any():
        raise ValueError("Annual denominators not positive")
    for (year,shape),g in annual.groupby(mk):
        if len(g)!=3 or not np.allclose(g.demand_mwh,g.demand_mwh.iloc[0],atol=.01,rtol=1e-9) or not np.allclose(g.renewable_available_mwh,g.renewable_available_mwh.iloc[0],atol=.01,rtol=1e-9):
            raise ValueError("Fixed source demand or synthetic supply changes with battery")
        r=marginals[(marginals.planning_year==year)&(marginals.synthetic_supply_shape==shape)]
        if len(r)!=1:raise ValueError("Missing original marginal scenario")
        for dur in DURATIONS:
            x=g[g.battery_duration_h==dur].iloc[0]
            for metric in ("unused_renewable_mwh","firm_generation_mwh","objective_illustrative_variable_usd"):
                target=float(r[f"{metric}_{dur}h"].iloc[0])
                if not np.isclose(float(x[metric]),target,atol=.1,rtol=1e-10):
                    raise ValueError("540-LP and nine-marginal archival results disagree")
        for metric in ("unused_renewable_mwh","objective_illustrative_variable_usd"):
            r=r.iloc[0]
            for d1,d2,tag in ((0,4,"0to4h"),(4,8,"4to8h")):
                value=float(r[f"{metric}_{d1}h"]-r[f"{metric}_{d2}h"])
                if not np.isclose(value,float(r[f"{metric}_reduction_{tag}"]),atol=.1,rtol=1e-10):
                    raise ValueError("Marginal source differences not reconciled")
            r=marginals[(marginals.planning_year==year)&(marginals.synthetic_supply_shape==shape)]
    return annual,marginals

def render(annual,marginals,out_dir):
    annual,marginals=certify(annual,marginals)
    out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    fig,ax=plt.subplots(figsize=(8.4,5.3))
    for shape,label,color in zip(SHAPES,LABELS,COLORS):
        g=annual[(annual.planning_year==2030)&(annual.synthetic_supply_shape==shape)].sort_values("battery_duration_h")
        ax.plot(g.battery_duration_h,100*g.unused_renewable_mwh/g.renewable_available_mwh,
                marker="o",linewidth=2.2,markersize=7,color=color,label=label)
    ax.set_xticks(DURATIONS)
    ax.set_ylim(bottom=0)
    ax.set_xlabel("Assumed storage duration at 25% of source-zone peak power (h)")
    ax.set_ylabel("Unused modeled potential / synthetic renewable availability (%)")
    ax.set_title("Figure 2 | Timing of assumed supply changes unused potential")
    ax.legend(frameon=False);ax.grid(axis="y",alpha=.2)
    fig.text(.5,.025,"2030 EFS projected demand; 20 zones aggregated. Flat/waves are synthetic, not measured wind/PV.",ha="center",fontsize=8)
    fig.tight_layout(rect=[0,.055,1,1])
    _save(fig,out,"Paper_S_proposed_main_Figure_2_synthetic_supply_unused_fraction")

    fig,ax=plt.subplots(figsize=(8.4,5.3))
    for year,color in zip(YEARS,COLORS):
        g=annual[(annual.planning_year==year)&(annual.synthetic_supply_shape=="ordinal24_wave_A")].sort_values("battery_duration_h")
        ax.plot(g.battery_duration_h,100*g.firm_generation_mwh/g.demand_mwh,marker="o",
                linewidth=2.2,markersize=7,color=color,label=f"{year} projected demand")
    ax.set_xticks(DURATIONS)
    ax.set_ylim(bottom=0)
    ax.set_xlabel("Assumed storage duration (h)")
    ax.set_ylabel("Firm generation / planning-year projected demand (%)")
    ax.set_title("Figure 3 | Planning-year response after demand normalization")
    ax.grid(axis="y",alpha=.2);ax.legend(frameon=False)
    fig.text(.5,.025,"Synthetic Wave A held fixed; model-conditional normalized demand, not independent observed weather years.",ha="center",fontsize=8)
    fig.tight_layout(rect=[0,.055,1,1])
    _save(fig,out,"Paper_S_proposed_main_Figure_3_planning_year_normalized_firm")

    fig,axes=plt.subplots(1,3,figsize=(13.2,5.0),sharey=True)
    for ax,year in zip(axes,YEARS):
        source=marginals[marginals.planning_year==year].set_index("synthetic_supply_shape").loc[list(SHAPES)]
        a=source.objective_illustrative_variable_usd_reduction_0to4h.to_numpy(dtype=float)/1e9
        b=source.objective_illustrative_variable_usd_reduction_4to8h.to_numpy(dtype=float)/1e9
        pos=np.arange(3)
        ax.bar(pos-.18,a,.36,label="0→4h",color="#477ba1")
        ax.bar(pos+.18,b,.36,label="4→8h",color="#db9550")
        ax.set_xticks(pos,LABELS)
        ax.set_title(str(year))
        ax.grid(axis="y",alpha=.18);ax.set_axisbelow(True)
        if (a<-.000001).any() or (b<-.000001).any():
            raise ValueError("Original toy objective worsened with relaxed duration")
        if (b>a+.000001).any():raise ValueError("Non-declining duration marginal comparison")
    axes[0].set_ylabel("Reduction in illustrative LP variable objective (USD billion)")
    axes[0].legend(frameon=False)
    fig.suptitle("Figure 4 | The second four-hour storage increment has a smaller cost response",fontsize=12.8)
    fig.text(.5,.018,"These are modeled operating objective differences, NOT storage CAPEX, NPV, or realized energy-market savings.",ha="center",fontsize=8.3)
    fig.tight_layout(rect=[0,.055,1,.92])
    _save(fig,out,"Paper_S_proposed_main_Figure_4_marginal_duration_cost")
    manifest={"status":"THREE_PAPER_S_MAIN_FIGURES_TWO_SOURCE_ARCHIVES_RECONCILED",
        "540_LP_archive":42107237659,"nine_marginal_archive":42455745341,
        "annual_source_rows":27,"year_shape_marginal_rows":9,
        "main_figures":[2,3,4],"supply_is_synthetic":True,
        "physical_utc_certified":False,"actual_western_opf":False,
        "twenty_zones_not_independent_temporal_replicates":True}
    (out/"Paper_S_Figures_2_3_4_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest

def _save(fig,out,stem):
    for ext in (".png",".svg"):
        fig.savefig(out/(stem+ext),dpi=230,bbox_inches="tight")
    plt.close(fig)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--annual",type=Path,required=True)
    p.add_argument("--marginals",type=Path,required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(render(pd.read_csv(a.annual),pd.read_csv(a.marginals),a.out_dir),indent=2))
if __name__=="__main__":main()
