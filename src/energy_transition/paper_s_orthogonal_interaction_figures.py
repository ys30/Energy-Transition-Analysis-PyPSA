"""Figure S13: source-verified MW/MWh objective interactions across 7 EFS shapes.

Inputs must be the accepted 84-rectangle audit artifact. Each heatmap cell is
the incremental value of extra MWh at higher MW (as percent of its own
zone-shape baseline toy variable objective), *not* a storage investment ROI.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SHAPES=("flat_50pct","ordinal24_wave_A","ordinal24_wave_B")
COLS=((.125,.25,.5,1.),(.125,.25,1.,2.),(.25,.5,.5,1.),(.25,.5,1.,2.))
TITLES=("Flat 50%","Synthetic wave A","Synthetic wave B")

def validate(data:pd.DataFrame)->pd.DataFrame:
    required={"source_shape_group","state","reeds_zone","synthetic_supply_shape",
      "low_power_peak_ratio","high_power_peak_ratio","low_energy_peak_hours",
      "high_energy_peak_hours","energy_benefit_low_power_usd",
      "energy_benefit_high_power_usd","mw_mwh_objective_interaction_usd",
      "mw_mwh_interaction_pct_of_baseline_cost","interaction_avoided_firm_component_usd",
      "interaction_avoided_unused_component_usd"}
    if not required.issubset(data):raise ValueError("Missing archived interaction fields")
    if len(data)!=84 or set(data.source_shape_group)!=set(range(1,8)) or set(data.synthetic_supply_shape)!=set(SHAPES):
        raise ValueError("Incomplete original 84 interactions")
    keys=["source_shape_group","synthetic_supply_shape","low_power_peak_ratio",
          "high_power_peak_ratio","low_energy_peak_hours","high_energy_peak_hours"]
    if data.duplicated(keys).any():raise ValueError("Duplicated factorial interaction cell")
    fields=["energy_benefit_low_power_usd","energy_benefit_high_power_usd",
      "mw_mwh_objective_interaction_usd","mw_mwh_interaction_pct_of_baseline_cost",
      "interaction_avoided_firm_component_usd","interaction_avoided_unused_component_usd"]
    if not np.isfinite(data[fields].to_numpy(dtype=float)).all():
        raise ValueError("Nonfinite original interaction")
    if not np.allclose(data.energy_benefit_high_power_usd-data.energy_benefit_low_power_usd,
                       data.mw_mwh_objective_interaction_usd,rtol=1e-9,atol=.1):
        raise ValueError("Incorrect original interaction formula")
    if not np.allclose(data.interaction_avoided_firm_component_usd+
                       data.interaction_avoided_unused_component_usd,
                       data.mw_mwh_objective_interaction_usd,rtol=1e-9,atol=.1):
        raise ValueError("Cost decomposition not reconciled")
    for (group,shape),g in data.groupby(["source_shape_group","synthetic_supply_shape"]):
        if len(g)!=4:raise ValueError("Missing 2x2 factorial rectangles")
        coords=set(zip(g.low_power_peak_ratio,g.high_power_peak_ratio,
                       g.low_energy_peak_hours,g.high_energy_peak_hours))
        if coords!=set(COLS):raise ValueError("Unexpected orthogonal factor steps")
        if len(g[["state","reeds_zone"]].drop_duplicates())!=1:
            raise ValueError("Multiple source zones in single demand-shape group")
    return data

def figure(source:pd.DataFrame,out_dir:Path):
    data=validate(source)
    out_dir=Path(out_dir);out_dir.mkdir(parents=True,exist_ok=True)
    labels=[]
    for group in range(1,8):
        s=data[data.source_shape_group==group].iloc[0]
        labels.append(str(s.state))
    max_value=max(1.,float(data.mw_mwh_interaction_pct_of_baseline_cost.max()))
    fig,axes=plt.subplots(1,3,figsize=(14.4,5.8),sharex=True,sharey=True)
    for ax,shape,title in zip(axes,SHAPES,TITLES):
        vals=np.zeros((7,4))
        for group in range(1,8):
            a=data[(data.source_shape_group==group)&(data.synthetic_supply_shape==shape)]
            for j,(pl,ph,el,eh) in enumerate(COLS):
                row=a[(a.low_power_peak_ratio==pl)&(a.high_power_peak_ratio==ph)&
                      (a.low_energy_peak_hours==el)&(a.high_energy_peak_hours==eh)]
                if len(row)!=1:raise ValueError("Missing one exact factorial cell")
                vals[group-1,j]=row.mw_mwh_interaction_pct_of_baseline_cost.iloc[0]
        im=ax.imshow(vals,aspect="auto",vmin=0,vmax=max_value)
        for i in range(7):
            for j in range(4):
                ax.text(j,i,f"{(0. if abs(vals[i,j])<.005 else vals[i,j]):.2f}",ha="center",va="center",
                        color="white" if vals[i,j]>.58*max_value else "black",fontsize=9)
        ax.set_title(title)
        ax.set_xticks(range(4),["MW .125→.25\nMWh .5→1","MW .125→.25\nMWh 1→2",
                                 "MW .25→.5\nMWh .5→1","MW .25→.5\nMWh 1→2"],rotation=35,ha="right",fontsize=8)
        ax.set_yticks(range(7),labels)
    axes[0].set_ylabel("Unique peak-normalized source demand group")
    fig.subplots_adjust(left=.11,right=.84,top=.82,bottom=.26,wspace=.12)
    color_axis=fig.add_axes([.86,.30,.014,.47])
    cb=fig.colorbar(im,cax=color_axis)
    cb.set_label("MW–MWh interaction (% of baseline LP cost)",fontsize=9)
    fig.suptitle("Figure S13 | Interaction of independently rated storage power and capacity",fontsize=13)
    fig.text(.5,.01,"Annual EFS source ordinal × synthetic renewables; conditional variable objective only. No storage CAPEX or Western OPF.",ha="center",fontsize=8)
    for ext in (".png",".svg"):
        fig.savefig(out_dir/("Figure_S13_orthogonal_MW_MWh_interaction_heatmap"+ext),
                    dpi=220,bbox_inches="tight")
    plt.close(fig)
    manifest={"status":"FIGURE_S13_SOURCE_CERTIFIED_84_ORTHOGONAL_INTERACTIONS",
              "factor_rectangles":84,"source_demand_shapes":7,"synthetic_supply_shapes":3,
              "source_clock_certified_utc":False,"real_resource_data":False,
              "battery_investment_cost_included":False}
    (out_dir/"Figure_S13_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--interactions",type=Path,required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(figure(pd.read_csv(a.interactions),a.out_dir),indent=2))

if __name__=="__main__":main()
