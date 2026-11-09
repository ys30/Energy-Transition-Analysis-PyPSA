"""Figure S14 from accepted eight-case HiGHS dual/forward-difference diagnostics."""
from __future__ import annotations
import argparse
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def plot(source:pd.DataFrame, out:Path):
    needed={"state","synthetic_supply_shape","source_shape_group",
        "battery_power_peak_ratio","battery_energy_peak_hours",
        "dual_objective_derivative_power_usd_per_mw",
        "dual_objective_derivative_energy_usd_per_mwh",
        "forward_difference_power_usd_per_mw",
        "forward_difference_energy_usd_per_mwh"}
    if not needed.issubset(source):raise ValueError("Missing accepted source dual fields")
    keys=["source_shape_group","synthetic_supply_shape","battery_power_peak_ratio","battery_energy_peak_hours"]
    if len(source)!=8 or source.duplicated(keys).any() or set(source.source_shape_group)!={1,7}:
        raise ValueError("Expected eight preselected two-source chronology configurations")
    cols=list(needed.intersection(set(source.select_dtypes(include="number").columns)))
    if not np.isfinite(source[cols].to_numpy(dtype=float)).all():
        raise ValueError("Nonfinite source derivative")
    for axis in ("power","energy"):
        dual=source[f"dual_objective_derivative_{axis}_usd_per_{'mw' if axis=='power' else 'mwh'}"]
        fd=source[f"forward_difference_{axis}_usd_per_{'mw' if axis=='power' else 'mwh'}"]
        if (dual>1e-5).any() or (fd>1e-3).any():
            raise ValueError("Raising installed capacity raised optimum objective")
        if (np.abs(dual-fd)>np.maximum(1.,.01*np.maximum(np.abs(dual),np.abs(fd)))).any():
            raise ValueError("HiGHS dual and one-sided finite difference disagree")
    df=source.sort_values(keys).reset_index(drop=True)
    labels=[]
    names={"flat_50pct":"Flat","ordinal24_wave_A":"Wave A","ordinal24_wave_B":"Wave B"}
    for row in df.itertuples(index=False):
        labels.append(f"{row.state}\\n{names[row.synthetic_supply_shape]}\\nP={row.battery_power_peak_ratio:g}, E={row.battery_energy_peak_hours:g}")
    fig,ax=plt.subplots(figsize=(12.6,5.6))
    x=np.arange(len(df));w=.38
    ax.bar(x-w/2,-df.dual_objective_derivative_energy_usd_per_mwh,
           width=w,label="Variable-cost change from +1 MWh (dual)")
    ax.bar(x+w/2,-df.dual_objective_derivative_power_usd_per_mw,
           width=w,label="Variable-cost change from +1 MW (dual)")
    ax.set_xticks(x,labels,fontsize=8)
    ax.set_ylabel("Annual illustrative LP objective decrease\\n(USD per extra MW or MWh; distinct units)")
    ax.set_title("Figure S14 | Source-backed storage capacity marginal sensitivity")
    ax.legend(frameon=False)
    ax.set_axisbelow(True);ax.grid(axis="y",alpha=.18)
    fig.text(.5,.015,
             "Duals verified against one-sided LP reoptimization; source-ordinal EFS and synthetic supply. No battery CAPEX or network OPF.",
             ha="center",fontsize=8)
    fig.tight_layout(rect=[0,.055,1,1])
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    for ext in (".png",".svg"):
        fig.savefig(out/("Figure_S14_dual_capacity_marginal_values"+ext),dpi=220,bbox_inches="tight")
    plt.close(fig)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--csv",required=True,type=Path)
    p.add_argument("--out-dir",required=True,type=Path)
    a=p.parse_args()
    plot(pd.read_csv(a.csv),a.out_dir)
    print("FIGURE_S14_VERIFIED_SOURCE_DUALS_PASS")
if __name__=="__main__":main()
