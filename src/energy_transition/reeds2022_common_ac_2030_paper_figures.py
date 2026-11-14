"""ReEDS2022 AC-consistent 2030 paper candidate heatmaps.

Use only independently passed common AC LP archive 43058074434, never
the original heterogeneous PV DC denominator heatmap as main manuscript
material. Assumption-specific illustrations without sampling uncertainty.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

STATES=("AZ","CO","ID","WY")
RATIOS=(.9,1.5,2.0)
WIND=(.25,.5,.75)
LP_RUN=43058074434


def render(paired_csv,out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    a=pd.read_csv(paired_csv)
    if len(a)!=144 or not set(a.state)==set(STATES) or not a.solver_status.eq("optimal").all():
        raise ValueError("Unexpected common-AC 144-case archive")
    if a.duplicated(["state","renewable_peak_ratio","wind_share_installed_mw",
                     "battery_duration_h","battery_power_peak_ratio"]).any():
        raise ValueError("Duplicate AC LP scenario keys")
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    figures=[]
    for state in STATES:
        s=a[(a.state.eq(state))&(a.battery_duration_h.eq(4))&
            (a.battery_power_peak_ratio.eq(.25))]
        if len(s)!=9:raise ValueError("Missing 2030 common-AC 4h 0.25 power source cases")
        for col,slug,title,fmt in (
            ("operating_savings_usd_per_reference_year","operating_savings_musd",
             "Avoided illustrative variable cost ($ million/reference year)","%.0f"),
            ("break_even_power_only_usd_per_kw_year","power_annuity_hurdle",
             "Maximum storage power-only annuity ($/kW-year)","%.1f")
        ):
            grid=s.pivot(index="renewable_peak_ratio",columns="wind_share_installed_mw",values=col)
            if list(grid.index)!=list(RATIOS) or list(grid.columns)!=list(WIND):
                raise ValueError("Incomplete prespecified common AC scenario grid")
            vals=grid.to_numpy(dtype=float)/(1e6 if slug=="operating_savings_musd" else 1.)
            if not np.isfinite(vals).all():raise ValueError("Nonfinite heatmap")
            fig,ax=plt.subplots(figsize=(6.5,4.8),layout="constrained")
            view=ax.imshow(vals,aspect="auto",cmap="viridis")
            cb=fig.colorbar(view,ax=ax)
            cb.set_label(title)
            ax.set_xticks(range(3),[f"{v:.0%}" for v in WIND])
            ax.set_yticks(range(3),[f"{v:.1f}×" for v in RATIOS])
            ax.set_xlabel("Wind share of hypothetical common-AC nameplate")
            ax.set_ylabel("Wind + PV AC nameplate / demand peak")
            ax.set_title(f"{state} · 2030 demand / 2012 source weather · 4h battery")
            for yi in range(3):
                for xi in range(3):
                    ax.text(xi,yi,fmt%vals[yi,xi],ha="center",va="center",
                            color="white" if vals[yi,xi] < (vals.max()+vals.min())/2 else "black",
                            fontsize=9,fontweight="bold")
            fig.savefig(out/f"paper_s_2030_{state}_common_ac_{slug}.png",dpi=250)
            fig.savefig(out/f"paper_s_2030_{state}_common_ac_{slug}.pdf")
            figures.append(f"{state}/{slug}")
            plt.close(fig)
    report={
      "status":"COMMON_AC_2030_8_PUBLICATION_CANDIDATE_HEATMAPS",
      "source_AC_180_lp_run":LP_RUN,
      "source_AC_144_storage_pairs":len(a),
      "figure_count":len(figures),"figures":figures,
      "states":STATES,"source_weather_year":2012,"demand_model_year":2030,
      "wind_share_mw_basis":"MW_AC both wind and PV inverter",
      "PV_ILR":1.34,
      "storage_duration_h":4,"battery_power_peak_ratio":.25,
      "capital_cost_in_optimized_objective":False,
      "real_network_and_actual_fleet_estimate":False,
      "hour_energy_integration_publisher_certified":False,
    }
    (out/"paper_s_2030_common_ac_8_heatmaps_manifest.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--paired",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    render(a.paired,a.out)

if __name__=="__main__":
    main()
