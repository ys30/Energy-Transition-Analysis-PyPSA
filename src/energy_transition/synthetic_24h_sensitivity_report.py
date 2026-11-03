"""Render publication-style *synthetic* 24-hour OPF diagnostics from verified JSON."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def render(result_path:Path,out_dir:Path):
    data=json.loads(result_path.read_text())
    if (data.get("hours"),data.get("scenarios"))!=(24,6):
        raise ValueError("Unexpected 24-hour scenario matrix")
    if data.get("real_western_opf_executed") is not False or data.get("all_operational_inputs_synthetic") is not True:
        raise ValueError("Source provenance flags inconsistent")
    cases=data["hourly_cases"]
    summary=pd.DataFrame([{k:v for k,v in case.items() if k!="hourly"} for case in cases])
    hourly=pd.DataFrame([{
        "hypothetical_line_capacity_mw":case["hypothetical_line_capacity_mw"],
        "hypothetical_solar_nameplate_mw":case["hypothetical_solar_nameplate_mw"], **row}
        for case in cases for row in case["hourly"]])
    if len(summary)!=6 or len(hourly)!=144:
        raise ValueError("Missing scenario/hour records")
    out_dir.mkdir(parents=True,exist_ok=True)
    summary.to_csv(out_dir/"synthetic_24h_scenario_metrics.csv",index=False)
    hourly.to_csv(out_dir/"synthetic_24h_hourly_metrics.csv",index=False)
    fig,ax=plt.subplots(figsize=(8,4.7))
    for solar,group in summary.groupby("hypothetical_solar_nameplate_mw"):
        ordered=group.sort_values("hypothetical_line_capacity_mw")
        ax.plot(ordered.hypothetical_line_capacity_mw,ordered.objective_synthetic_cost_units,
                marker="o",label=f"Assumed solar {solar:g} MW")
    ax.set(xlabel="Assumed capacity of every branch (MW)",
           ylabel="24-hour optimized synthetic cost (arbitrary units)",
           title="Source-topology synthetic network sensitivity (not actual grid)")
    ax.legend(frameon=False)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_dir/"synthetic_24h_cost_capacity.png",dpi=170)
    plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,4.7))
    for solar,group in summary.groupby("hypothetical_solar_nameplate_mw"):
        ordered=group.sort_values("hypothetical_line_capacity_mw")
        ax.plot(ordered.hypothetical_line_capacity_mw,ordered.daily_backup_mwh,
                marker="o",label=f"Assumed solar {solar:g} MW")
    ax.set(xlabel="Assumed capacity of every branch (MW)",
           ylabel="24-hour expensive backup generation (MWh)",
           title="Synthetic network backup dispatch (not actual grid)")
    ax.legend(frameon=False)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_dir/"synthetic_24h_backup_capacity.png",dpi=170)
    plt.close(fig)
    return summary,hourly


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    args=p.parse_args()
    s,h=render(args.input,args.out_dir)
    print(s.to_string(index=False))
    print("Synthetic scenario rows:",len(s),"hourly rows:",len(h))
