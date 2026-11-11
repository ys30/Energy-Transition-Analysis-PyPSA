"""Reproducible presentation figures from the archived source-backed 144-LP CSV.

No new model solve; no claims of actual grid benefit or battery investment
return. Error bars are *not* estimated, since the study is deterministic.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

STATES=("AZ","CO","ID","WY")
RATIOS=(0.9,1.5,2.0)
YEARS=(2030,2040,2050)
MODES=("end_instant_hold","trapezoid_with_first_endpoint")

def diagnostics(path,out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    df=pd.read_csv(path)
    if len(df)!=72 or df.duplicated(
        ["state","demand_model_year","hour_approximation","renewable_peak_ratio"]).any():
        raise ValueError("Expected 72 exact 0h/4h source pairs")
    if set(df.state)!=set(STATES) or set(df.demand_model_year)!=set(YEARS):
        raise ValueError("Incorrect states or years")
    if set(df.hour_approximation)!=set(MODES) or set(df.renewable_peak_ratio)!=set(RATIOS):
        raise ValueError("Incomplete original assumptions or penetration ratios")
    if (df.savings_variable_usd<-.01).any() or (df.renewable_available_mwh_0h<=0).any():
        raise ValueError("Non-monotonic storage savings or invalid renewable availability")
    out=Path(out);out.mkdir(parents=True,exist_ok=True)

    # Percent denominators are matched to *each specific* 0h scenario.
    pivot=df.pivot(index=["state","demand_model_year","renewable_peak_ratio"],
                   columns="hour_approximation",
                   values=["savings_pct_0h_cost","savings_variable_usd",
                           "curtailment_rate_without_storage_pct"])
    if len(pivot)!=36 or pivot.isna().any().any():
        raise ValueError("Missing 36 end/trapezoid paired sensitivity records")
    sensitivities=[]
    for (state,year,ratio),row in pivot.iterrows():
        endpoint=float(row[("savings_pct_0h_cost",MODES[0])])
        trap=float(row[("savings_pct_0h_cost",MODES[1])])
        sensitivities.append({
            "state":state,"demand_model_year":year,
            "renewable_peak_ratio":ratio,
            "storage_savings_pct_end_instant":endpoint,
            "storage_savings_pct_trapezoid":trap,
            "trapezoid_minus_endpoint_savings_pp":trap-endpoint,
            "end_minus_trap_absolute_pp":abs(trap-endpoint),
        })
    sensitivity=pd.DataFrame(sensitivities)
    sensitivity.to_csv(out/"paper_s_reeds2022_36_time_assumption_sensitivity.csv",index=False)
    data=df[df.hour_approximation.eq(MODES[1])]
    for state in STATES:
        selected=data[data.state.eq(state)]
        for measure,filename,ylabel,scale in [
            ("savings_pct_0h_cost","storage_objective_savings","Operating objective savings vs. no storage (%)",1),
            ("curtailment_rate_without_storage_pct","no_storage_curtailment","No-storage curtailment / available renewable (%)",1),
            ("firm_displacement_mwh","firm_energy_displacement","Firm energy displaced by storage (GWh)",1/1000),
        ]:
            fig,ax=plt.subplots(figsize=(7,4.2))
            for year in YEARS:
                sub=selected[selected.demand_model_year.eq(year)].sort_values("renewable_peak_ratio")
                if len(sub)!=3:raise ValueError("Missing series for "+state)
                ax.plot(sub.renewable_peak_ratio,sub[measure]*scale,"-o",label=str(year))
            ax.set_xticks(RATIOS)
            ax.set_xticklabels(["0.9×","1.5×","2.0×"])
            ax.set_xlabel("Hypothetical renewable nameplate / state peak demand")
            ax.set_ylabel(ylabel)
            ax.set_title(f"{state}: source weather 2012, assumed 4h battery" if measure!="curtailment_rate_without_storage_pct"
                         else f"{state}: source weather 2012, no battery")
            ax.legend(title="Demand year")
            ax.grid(alpha=.2)
            fig.tight_layout()
            fig.savefig(out/f"paper_s_{state}_{filename}_2012_weather.png",dpi=220)
            fig.savefig(out/f"paper_s_{state}_{filename}_2012_weather.pdf")
            plt.close(fig)

    report={
        "status":"COUNTY_144_LP_PRESENTATION_DIAGNOSTICS_VERIFIED",
        "source_lp_run":42966023512,"source_paired_rows":len(df),
        "hour_approximation_comparison_pairs":len(sensitivity),
        "figure_count":len(STATES)*3,
        "battery_capex_included":False,
        "source_weather_hourly_energy_source_certified":False,
        "real_grid_dispatch":False,
        "max_hour_approximation_savings_difference_pp":float(
           sensitivity.end_minus_trap_absolute_pp.max()),
    }
    (out/"paper_s_reeds2022_144_lp_figure_manifest.json").write_text(
        json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--paired-csv",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    diagnostics(a.paired_csv,a.out)

if __name__=="__main__":
    main()
