"""Paper S main Figure 6 candidate: aggregate-versus-window identifiability contrast.

All cells are re-derived from *two separate accepted* original LP archives;
the figure MUST NOT be described as a certified journal panel before its own CI.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

GROUPS={1:("Arizona","p28"),7:("Wyoming","p24")}
WINDOW="middle_4001_4168"

def reconcile(annual,window):
    ac={"source_shape_group","state","reeds_zone","synthetic_supply_shape",
        "battery_power_peak_ratio","battery_energy_peak_hours",
        "baseline","min","max","width_mwh"}
    wc={"source_shape_group","state","reeds_zone","window","baseline",
        "min","max","span_mwh"}
    if not ac.issubset(annual) or not wc.issubset(window):
        raise ValueError("Missing source-archived annual or window LP columns")
    if annual.duplicated(["source_shape_group","synthetic_supply_shape",
        "battery_power_peak_ratio","battery_energy_peak_hours"]).any() or len(annual)!=8:
        raise ValueError("Annual source archive does not cover eight unique configurations")
    if window.duplicated(["source_shape_group","window"]).any() or len(window)!=4:
        raise ValueError("Window source archive not four unique prespecified intervals")
    a=annual[(annual.synthetic_supply_shape=="ordinal24_wave_A")&
        np.isclose(annual.battery_power_peak_ratio,.25)&
        np.isclose(annual.battery_energy_peak_hours,1.)]
    w=window[window.window==WINDOW]
    if len(a)!=2 or len(w)!=2 or set(a.source_shape_group)!={1,7} or set(w.source_shape_group)!={1,7}:
        raise ValueError("Archived annual and window cases are not matched")
    rows=[]
    for g,(state,zone) in GROUPS.items():
        r=a[a.source_shape_group==g].iloc[0]
        q=w[w.source_shape_group==g].iloc[0]
        if (r.state!=state or r.reeds_zone!=zone or
            q.state!=state or q.reeds_zone!=zone):
            raise ValueError("Zonal source provenance changed")
        av=np.array([r.baseline,r["min"],r["max"],r.width_mwh],dtype=float)
        wv=np.array([q.baseline,q["min"],q["max"],q.span_mwh],dtype=float)
        if (not np.isfinite(av).all() or not np.isfinite(wv).all()
            or av[:3].min()<=0 or wv[0]<=0 or wv[1]<-.01):
            raise ValueError("Invalid source delivered-energy levels")
        if (not np.isclose(av[2]-av[1],av[3],atol=.02,rtol=1e-8) or
            not np.isclose(wv[2]-wv[1],wv[3],atol=.02,rtol=1e-8)):
            raise ValueError("Source LP extrema differences do not reconcile")
        if not (av[1]-.03<=av[0]<=av[2]+.03 and wv[1]-.03<=wv[0]<=wv[2]+.03):
            raise ValueError("Original optimum missing from source ranges")
        rows.append(dict(source_shape_group=g,state=state,reeds_zone=zone,
             original_annual_discharge_mwh=float(av[0]),
             annual_interval_span_mwh=float(av[3]),
             annual_interval_relative_percent=100*float(av[3]/av[0]),
             original_window_discharge_mwh=float(wv[0]),
             window_interval_span_mwh=float(wv[3]),
             window_interval_relative_percent=100*float(wv[3]/wv[0]),
             window_min_mwh=float(wv[1]),window_max_mwh=float(wv[2]),
             ratio_of_relative_spans=float((wv[3]/wv[0])/(av[3]/av[0]))))
    return pd.DataFrame(rows)

def plot(annual,window,out_dir):
    x=reconcile(annual,window)
    p=Path(out_dir);p.mkdir(parents=True,exist_ok=True)
    fig,ax=plt.subplots(figsize=(9.6,5.9))
    pos=np.arange(len(x))
    width=.32
    annual_pct=x.annual_interval_relative_percent.to_numpy()
    window_pct=x.window_interval_relative_percent.to_numpy()
    b1=ax.bar(pos-width/2,annual_pct,width,label="Full-year discharge")
    b2=ax.bar(pos+width/2,window_pct,width,label="Predeclared 168-source-hour window")
    for bars,values in ((b1,annual_pct),(b2,window_pct)):
        for bar,val in zip(bars,values):
            ax.annotate(f"{val:.5g}%",(bar.get_x()+bar.get_width()/2,val),
                    xytext=(0,5),textcoords="offset points",ha="center",fontsize=9)
    ax.set_yscale("log")
    ax.set_ylim(1e-5,3e3)
    ax.set_xticks(pos,[f"{r.state} {r.reeds_zone}" for r in x.itertuples()])
    ax.set_ylabel("Near-optimal min–max span / original delivered MWh (%) — logarithmic")
    ax.set_title("Proposed Paper S Fig. 6 | Annual totals conceal window dispatch ambiguity")
    ax.grid(axis="y",which="major",alpha=.2)
    ax.set_axisbelow(True)
    ax.legend(frameon=False,loc="upper left")
    fig.text(.5,.053,"Both extents use the same original-cost cap: C(x) ≤ C* + max($0.05, 10⁻⁹ C*).",ha="center",fontsize=9)
    fig.text(.5,.025,"Different denominators: annual MWh versus window MWh. Source hours 4001–4168 are not certified calendar dates.",ha="center",fontsize=8)
    fig.text(.5,.004,"Synthetic wave-A renewable availability; 2030 EFS demand; not observed grid operation or investment value.",ha="center",fontsize=8)
    fig.tight_layout(rect=[0,.085,1,1])
    for ext in (".png",".svg"):
        fig.savefig(p/("paper_s_proposed_main_Figure_6_annual_vs_window"+ext),dpi=230,bbox_inches="tight")
    plt.close(fig)
    x.to_csv(p/"paper_s_main_figure_6_two_source_comparisons.csv",index=False)
    manifest={"status":"PAPER_S_MAIN_FIGURE_6_SOURCE_ARCHIVE_RECONCILIATION",
      "historical_source_annual_workflow":42747095388,
      "historical_source_window_workflow":42780417107,
      "matched_cases":2,"full_year_source_hours":8760,
      "window_source_hours":[4001,4168],
      "near_optimal_not_exact_optimal_face":True,
      "synthetic_supply_not_observed_renewables":True,
      "calendar_source_hours_certified_UTC":False,
      "intervals_from_distinct_secondary_LPs":True}
    (p/"paper_s_main_Figure_6_source_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest

def main():
    args=argparse.ArgumentParser()
    args.add_argument("--annual",type=Path,required=True)
    args.add_argument("--window",type=Path,required=True)
    args.add_argument("--out-dir",type=Path,required=True)
    a=args.parse_args()
    print(json.dumps(plot(pd.read_csv(a.annual),pd.read_csv(a.window),a.out_dir),indent=2))
if __name__=="__main__":main()
