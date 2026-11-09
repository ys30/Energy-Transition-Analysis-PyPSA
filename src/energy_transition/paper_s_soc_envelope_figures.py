"""Figure S16 — constrained near-optimal annual-average SOC occupancy envelopes.

This is an interval in aggregate annual SOC from min/max SECONDARY LPs under
an explicit near-optimal original-cost cap; not pointwise SOC bounds.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SHAPES={"flat_50pct":"Flat","ordinal24_wave_A":"Wave A","ordinal24_wave_B":"Wave B"}
KEY=["source_shape_group","synthetic_supply_shape","battery_power_peak_ratio","battery_energy_peak_hours"]

def validate(data):
    required=set(KEY+["state","reeds_zone","solution","total_soc_mwh_hours",
        "mean_soc_fraction","original_cost_candidate_usd","reference_original_lp_cost_usd",
        "allowed_cost_increase_usd","candidate_cost_gap_usd"])
    if not required.issubset(data):raise ValueError("Missing original SOC envelope source fields")
    if len(data)!=24 or data.duplicated(KEY+["solution"]).any():
        raise ValueError("Expected 24 original min/base/max configurations")
    if set(data.solution)!={"baseline","min","max"} or set(data.source_shape_group)!={1,7}:
        raise ValueError("Unexpected archived SOC envelope source population")
    numeric=data[["mean_soc_fraction","total_soc_mwh_hours","original_cost_candidate_usd",
                  "reference_original_lp_cost_usd","allowed_cost_increase_usd",
                  "candidate_cost_gap_usd"]].to_numpy(dtype=float)
    if not np.isfinite(numeric).all():raise ValueError("Nonfinite source envelope value")
    if ((data.candidate_cost_gap_usd>data.allowed_cost_increase_usd+.02).any() or
        (data.candidate_cost_gap_usd<-.05).any()):
        raise ValueError("Original objective cap/reconciliation failed")
    if not data.mean_soc_fraction.between(-1e-7,1+1e-7).all():
        raise ValueError("Storage occupancy outside physical capacity")
    rows=[]
    for key,group in data.groupby(KEY):
        if len(group)!=3 or set(group.solution)!={"baseline","min","max"}:
            raise ValueError("Incomplete original SOC envelope triple")
        if group[["state","reeds_zone"]].drop_duplicates().shape[0]!=1:
            raise ValueError("Original representative zone identity mismatch")
        a=group.set_index("solution")
        low=float(a.loc["min","mean_soc_fraction"])
        mid=float(a.loc["baseline","mean_soc_fraction"])
        high=float(a.loc["max","mean_soc_fraction"])
        if low>mid+1e-6 or mid>high+1e-6:
            raise ValueError("Baseline SOC fraction is outside optimized interval")
        original_cost=a.reference_original_lp_cost_usd.to_numpy(dtype=float)
        if original_cost.max()-original_cost.min()>.05:
            raise ValueError("Inconsistent original optimal objective across modes")
        label=f"{a.loc['min','state']} · {SHAPES[key[1]]}"
        if key[1]=="ordinal24_wave_A" and key[2]==.125:
            label+=" (P 12.5%)"
        rows.append({"label":label,"source_shape_group":int(key[0]),
             "synthetic_supply_shape":key[1],
             "battery_power_peak_ratio":key[2],
             "battery_energy_peak_hours":key[3],
             "soc_min_pct":100*low,"soc_baseline_pct":100*mid,
             "soc_max_pct":100*high,
             "soc_interval_width_percentage_points":100*(high-low),
             "max_original_cost_increase_usd":float(a.candidate_cost_gap_usd.max())})
    result=pd.DataFrame(rows).sort_values(KEY).reset_index(drop=True)
    if len(result)!=8:raise ValueError("Not eight archived SOC intervals")
    return result

def draw(data,out_dir):
    p=Path(out_dir);p.mkdir(parents=True,exist_ok=True)
    a=validate(data)
    fig,ax=plt.subplots(figsize=(10.6,5.3))
    ys=np.arange(len(a))[::-1]
    for j,r in a.iterrows():
        yy=ys[j]
        ax.plot([r.soc_min_pct,r.soc_max_pct],[yy,yy],
                color="C0" if r.source_shape_group==1 else "C1",linewidth=4,
                solid_capstyle="round")
        ax.scatter([r.soc_min_pct,r.soc_max_pct],[yy,yy],marker="|",s=125,
                   color="C0" if r.source_shape_group==1 else "C1",zorder=3)
        ax.scatter(r.soc_baseline_pct,yy,marker="o",s=34,color="black",zorder=4)
    ax.set_yticks(ys,a.label)
    ax.set_xlim(left=0,right=100)
    ax.set_xlabel("Annual mean SOC (% of installed MWh capacity)")
    ax.set_title("Figure S16 | Occupancy envelopes under an explicit near-optimal cost cap")
    ax.grid(axis="x",alpha=.2)
    ax.set_axisbelow(True)
    fig.text(.5,.035,"Line: min–max SOC over constrained LP solutions; black dot: original optimum. No pointwise SOC bounds.",
             fontsize=8,ha="center")
    fig.text(.5,.01,"EFS source ordinal + synthetic supply; 1e-9 relative cost allowance (min $0.05); no CAPEX/Western OPF.",
             fontsize=8,ha="center")
    fig.tight_layout(rect=[0,.065,1,1])
    for ext in (".png",".svg"):
        fig.savefig(p/("Figure_S16_SOC_occupancy_cost_cap_envelopes"+ext),dpi=220,bbox_inches="tight")
    plt.close(fig)
    a.to_csv(p/"paper_s_eight_SOC_occupancy_intervals.csv",index=False)
    cert={"status":"PAPER_S_FIGURE_S16_FROM_EIGHT_ORIGINAL_COST_CAPPED_SOC_INTERVALS",
        "source_LP_solutions":24,"intervals":8,
        "bounds_are_on_annual_mean_SOC":True,
        "bounds_are_on_every_individual_hour":False,
        "real_solar_wind_or_western_opf":False}
    (p/"Figure_S16_manifest.json").write_text(json.dumps(cert,indent=2)+"\n")
    print(json.dumps(cert,indent=2))
    return cert

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--summary",required=True,type=Path)
    parser.add_argument("--out-dir",required=True,type=Path)
    a=parser.parse_args()
    draw(pd.read_csv(a.summary),a.out_dir)

if __name__=="__main__":main()
