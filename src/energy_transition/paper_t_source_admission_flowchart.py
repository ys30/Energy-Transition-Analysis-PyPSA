"""Reproducible Paper T source-admission diagram (conceptual, not measured data).

The diagram draws only independently evidenced source admission states.
"""
from pathlib import Path
import argparse
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

STEPS = [
 ("efs",.09,.78,"EFS 2020 original CSV\nReference / Moderate\nLocalHourID: 1–8760","#e8f1fb"),
 ("reeds",.63,.78,"ReEDS 2022 HDF5\nEFS_REFERENCE; 2012 CST clock\nMD5-verified original","#e8f1fb"),
 ("source",.09,.53,"Source integrity gate\nState × year × hour coverage\nOriginal Idaho sector reconciliation","#f1f4f7"),
 ("source2",.63,.53,"Publisher source gate\nHDF5 2012 calendar / UTC−06\nNo inherited EFS 2020 clock","#f1f4f7"),
 ("numeric",.345,.32,"Numerical comparability only\nAnnual totals; 33 × 8760 hours\nNonwrapping lags; Idaho residuals","#e6f5ec"),
 ("physical",.345,.12,"Physical-hour join admission\nEFS 2020 source-clock crosswalk\nWeather-year + geography verification","#fff0e2")
]
def render(out_dir):
    out_dir=Path(out_dir);out_dir.mkdir(parents=True,exist_ok=True)
    fig,ax=plt.subplots(figsize=(12.5,8.8));ax.set(xlim=(0,1),ylim=(0,1));ax.axis("off")
    for key,x,y,label,color in STEPS:
        w=.31 if key in ("numeric","physical") else .29
        ax.add_patch(FancyBboxPatch((x,y),w,.145,boxstyle="round,pad=0.012,rounding_size=0.012",
                                   edgecolor="#52657b",facecolor=color,linewidth=1.3))
        ax.text(x+w/2,y+.0725,label,ha="center",va="center",fontsize=10.1,linespacing=1.45)
    for start,end in [((.235,.775),(.235,.695)),((.775,.775),(.775,.695)),
                      ((.235,.52),(.43,.475)),((.775,.52),(.58,.475)),((.5,.31),(.5,.275))]:
        ax.add_patch(FancyArrowPatch(start,end,arrowstyle="-|>",mutation_scale=16,lw=1.7,color="#63758a"))
    ax.text(.5,.967,"Figure T1 | Cross-release provenance and time-join admission",
            fontsize=16,ha="center",weight="bold")
    ax.text(.682,.21,"BLOCKED: original EFS2020\nphysical clock not certified",
            color="#a04c1a",ha="left",va="center",weight="bold",fontsize=10)
    ax.text(.5,.035,"Numeric alignment ≠ certified UTC. No future wind/solar resource join or real Western OPF is admitted.",
            ha="center",color="#7b3e25",fontsize=10)
    for ext in ("svg","png"):
        fig.savefig(out_dir/f"figure_T1_source_admission.{ext}",dpi=220,bbox_inches="tight")
    plt.close(fig)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out-dir",required=True);a=p.parse_args()
    render(a.out_dir)
