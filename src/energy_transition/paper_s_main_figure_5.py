"""Paper S candidate main Fig 5: independent P/E marginal response plus cross-interaction.

All numbers are cross-audited from accepted 189-case LP and 84 interaction
archives; counts are descriptive across seven *unique normalized demand shapes*
in 2030, not independent geographical replications or statistical tests.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SHAPES=("flat_50pct","ordinal24_wave_A","ordinal24_wave_B")
LABELS=("Flat","Wave A","Wave B")
AXES=("energy_at_fixed_power","power_at_fixed_energy")
COLORS=("#577590","#43aa8b","#f8961e")
KEYS=["source_shape_group","synthetic_supply_shape","axis","held_constant",
      "from_level","to_level"]
IK=["source_shape_group","synthetic_supply_shape","low_power_peak_ratio",
    "high_power_peak_ratio","low_energy_peak_hours","high_energy_peak_hours"]

def certify(contrasts,interactions):
    cr={"source_shape_group","synthetic_supply_shape","axis","held_constant",
        "from_level","to_level","added_discharge_mwh","toy_objective_reduction_usd"}
    ir=set(IK+["mw_mwh_objective_interaction_usd",
               "mw_mwh_interaction_pct_of_baseline_cost",
               "energy_benefit_low_power_usd","energy_benefit_high_power_usd"])
    if not cr.issubset(contrasts) or not ir.issubset(interactions):
        raise ValueError("Missing source archived factorial contrast columns")
    if len(contrasts)!=252 or contrasts.duplicated(KEYS).any():
        raise ValueError("Expected 252 unique original one-axis contrasts")
    if len(interactions)!=84 or interactions.duplicated(IK).any():
        raise ValueError("Expected 84 unique original four-corner interactions")
    for source in (contrasts,interactions):
        if set(source.source_shape_group)!={1,2,3,4,5,6,7} or set(source.synthetic_supply_shape)!=set(SHAPES):
            raise ValueError("Original seven-shape x three-supply experiment incomplete")
    if set(contrasts.axis)!=set(AXES):
        raise ValueError("Original axes changed")
    for (g,s),a in contrasts.groupby(["source_shape_group","synthetic_supply_shape"]):
        if len(a)!=12 or a.axis.value_counts().to_dict()!={"energy_at_fixed_power":6,"power_at_fixed_energy":6}:
            raise ValueError("Incomplete unique source-demand axis contrasts")
    for (g,s),a in interactions.groupby(["source_shape_group","synthetic_supply_shape"]):
        if len(a)!=4:raise ValueError("Incomplete source 2x2 interaction rectangles")
    fields=["added_discharge_mwh","toy_objective_reduction_usd"]
    if not np.isfinite(contrasts[fields].to_numpy(dtype=float)).all():
        raise ValueError("Invalid contrast response values")
    if not np.isfinite(interactions[[
        "mw_mwh_objective_interaction_usd","mw_mwh_interaction_pct_of_baseline_cost"]].to_numpy(dtype=float)).all():
        raise ValueError("Invalid interaction response values")
    if not np.allclose(interactions.energy_benefit_high_power_usd-
       interactions.energy_benefit_low_power_usd,
       interactions.mw_mwh_objective_interaction_usd,atol=.1,rtol=1e-9):
        raise ValueError("Four-corner LP interaction identity violated")
    counts=[]
    for axis,constant,steps in (
       ("energy_at_fixed_power",.25,((.5,1.),(1.,2.))),
       ("power_at_fixed_energy",1.,((.125,.25),(.25,.5)))):
        for supply in SHAPES:
            for low,high in steps:
                a=contrasts[(contrasts.axis==axis)&
                  np.isclose(contrasts.held_constant,constant)&
                  (contrasts.synthetic_supply_shape==supply)&
                  np.isclose(contrasts.from_level,low)&np.isclose(contrasts.to_level,high)]
                if len(a)!=7:
                    raise ValueError("Missing one selected source response group")
                counts.append({"axis":axis,"held_constant":constant,
                    "synthetic_supply_shape":supply,"from_level":low,
                    "to_level":high,
                    "positive_groups_of_7":int((a.added_discharge_mwh>1e-3).sum())})
    n=pd.DataFrame(counts)
    signs=[]
    for shape in SHAPES:
        a=interactions[interactions.synthetic_supply_shape==shape]
        if len(a)!=28:raise ValueError("Expected 28 interactions per supply")
        positives=int((a.mw_mwh_objective_interaction_usd>1.).sum())
        negatives=int((a.mw_mwh_objective_interaction_usd< -1.).sum())
        signs.append({"synthetic_supply_shape":shape,
                      "positive_interactions_of_28":positives,
                      "near_zero_interactions_of_28":28-positives-negatives,
                      "negative_interactions_of_28":negatives,
                      "median_interaction_pct_baseline":float(a.mw_mwh_interaction_pct_of_baseline_cost.median()),
                      "max_interaction_pct_baseline":float(a.mw_mwh_interaction_pct_of_baseline_cost.max())})
    return n,pd.DataFrame(signs)

def render(contrasts,interactions,out_dir):
    responses,signs=certify(contrasts,interactions)
    out_dir=Path(out_dir);out_dir.mkdir(parents=True,exist_ok=True)
    fig,axes=plt.subplots(1,3,figsize=(15,5.6),gridspec_kw={"width_ratios":[1,1,1.13]})
    xx=np.arange(3); width=.32
    specs=[
      ("energy_at_fixed_power",.25,((.5,1.),(1.,2.)),
       "A  More MWh, fixed P = 25% peak",("E: 0.5→1","E: 1→2")),
      ("power_at_fixed_energy",1.,((.125,.25),(.25,.5)),
       "B  More MW, fixed E = 1 peak-hour",("P: 12.5→25%","P: 25→50%"))
    ]
    for ax,(axis,constant,steps,title,legends) in zip(axes[:2],specs):
        for k,((low,high),legend) in enumerate(zip(steps,legends)):
            values=[]
            for s in SHAPES:
                a=responses[(responses.axis==axis)&
                 (responses.synthetic_supply_shape==s)&
                 np.isclose(responses.held_constant,constant)&
                 np.isclose(responses.from_level,low)&
                 np.isclose(responses.to_level,high)]
                assert len(a)==1
                values.append(int(a.positive_groups_of_7.iloc[0]))
            bars=ax.bar(xx+(k-.5)*width,values,width,
                label=legend,color=("#447a9e" if k==0 else "#dea654"))
            ax.bar_label(bars,padding=2,fontsize=10)
        ax.set_xticks(xx,LABELS)
        ax.set_ylim(0,8)
        ax.set_yticks(range(0,8,2))
        ax.set_ylabel("Demand shapes with higher annual discharge (of 7)")
        ax.set_title(title,fontsize=10.5,weight="bold")
        ax.legend(loc="upper left",fontsize=8.4,frameon=False)
        ax.set_axisbelow(True);ax.grid(axis="y",alpha=.18)
    ax=axes[2]
    positive=signs.positive_interactions_of_28.to_numpy()
    near=signs.near_zero_interactions_of_28.to_numpy()
    negative=signs.negative_interactions_of_28.to_numpy()
    ax.barh(xx,positive,color="#43aa8b",label="Positive (> USD 1)")
    ax.barh(xx,near,left=positive,color="#cbd5df",label="Near zero (±USD 1)")
    if negative.any():ax.barh(xx,negative,left=positive+near,color="#d65c60",label="Negative (< -USD 1)")
    for i in range(3):
        if positive[i]:
            ax.text(positive[i]/2,i,str(positive[i]),ha="center",va="center",color="white",weight="bold",fontsize=10)
        ax.text(positive[i]+near[i]/2,i,str(near[i]),ha="center",va="center",fontsize=10)
    ax.set_yticks(xx,LABELS)
    ax.invert_yaxis()
    ax.set_xlim(0,31)
    ax.set_xticks([0,7,14,21,28])
    ax.set_xlabel("2×2 LP cost interactions (28 per supply)")
    ax.set_title("C  MW × MWh complementarity",fontsize=10.5,weight="bold")
    ax.legend(loc="lower center",bbox_to_anchor=(.5,-.3),ncol=1,frameon=False,fontsize=8.4)
    ax.grid(axis="x",alpha=.18);ax.set_axisbelow(True)
    fig.suptitle("Paper S — Independently sized storage power and energy reveal conditional interactions",
                 fontsize=13.4,weight="bold",y=.975)
    fig.text(.5,.07,"2030: 7 distinct normalized demand chronologies × 3 synthetic supply shapes. Counted responses are descriptive, not independent statistical replicates.",ha="center",fontsize=9)
    fig.text(.5,.042,"Interaction = added MWh cost benefit at high MW minus benefit at low MW. USD 1 is a numerical classification threshold, not a significance test.",ha="center",fontsize=8.6)
    fig.text(.5,.013,"Illustrative variable operating objective only; no measured wind/PV, battery investment costs, physical UTC, or Western network OPF.",ha="center",fontsize=8.6)
    fig.subplots_adjust(left=.055,right=.985,top=.83,bottom=.25,wspace=.31)
    for ext in (".png",".svg"):
        fig.savefig(out_dir/("Paper_S_proposed_main_Figure_5_independent_MW_MWh"+ext),dpi=235,bbox_inches="tight")
    plt.close(fig)
    responses.to_csv(out_dir/"Paper_S_main_Figure_5_12_axis_counts.csv",index=False)
    signs.to_csv(out_dir/"Paper_S_main_Figure_5_interaction_signs.csv",index=False)
    manifest={"status":"PROPOSED_PAPER_S_MAIN_FIGURE_5_TWO_ACCEPTED_SOURCE_ARCHIVES",
       "orthogonal_189LP_source_run":42674534963,
       "interaction_84_source_run":42675999423,
       "one_axis_contrasts_used":252,"interaction_rectangles_used":84,
       "unique_normalized_demand_shapes":7,
       "supply_profiles_synthetic":True,
       "seven_shapes_are_not_iid_statistical_samples":True,
       "threshold_one_USD_is_not_statistical_significance":True}
    (out_dir/"Paper_S_main_Figure_5_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--contrasts",type=Path,required=True)
    p.add_argument("--interactions",type=Path,required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(render(pd.read_csv(a.contrasts),pd.read_csv(a.interactions),a.out_dir),indent=2))
if __name__=="__main__":main()
