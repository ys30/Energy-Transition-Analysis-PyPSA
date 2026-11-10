"""Paper S manuscript Figure 1 candidate: provenance and admissible model workflow.

A *schema and source-audit grounded schematic*, not an observed spatial map.
The numeric group counts are locked to the accepted EFS source-shape audit.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib import rcParams

YEARS=(2030,2040,2050)
ZONES_PER_YEAR=20
NONZERO_ZONES=19
ZERO_ZONES=1
UNIQUE_WITHIN_YEAR_SHAPES=7
HOURS_PER_SOURCE_YEAR=8760
SYNTHETIC_SUPPLY=("flat_50pct","ordinal24_wave_A","ordinal24_wave_B")
DURATIONS=(0,4,8)
ORIGINAL_CASES=20*3*3*3
ORTHOGONAL_CASES=7*3*3*3
FACTOR_P=(.125,.25,.5)
FACTOR_E=(.5,1.,2.)

def verify_design():
    if (ORIGINAL_CASES!=540 or ORTHOGONAL_CASES!=189 or
        NONZERO_ZONES+ZERO_ZONES!=ZONES_PER_YEAR or
        UNIQUE_WITHIN_YEAR_SHAPES!=7 or HOURS_PER_SOURCE_YEAR!=8760):
        raise ValueError("Original archive-grounded schematic counts changed")
    if len(SYNTHETIC_SUPPLY)!=3 or len(FACTOR_P)!=3 or len(FACTOR_E)!=3:
        raise ValueError("Original factor definitions changed")
    return dict(
      source="Original EFS/LAF hourly projected demand",
      accepted_normalized_shape_audit_run=42464270811,
      accepted_original_LP_run=42107237659,
      accepted_orthogonal_LP_run=42674534963,
      source_years=list(YEARS),
      source_zones_per_year=ZONES_PER_YEAR,
      nonzero_zones_per_year=NONZERO_ZONES,
      zero_zones_per_year=ZERO_ZONES,
      distinct_peak_normalized_nonzero_shapes_per_year=UNIQUE_WITHIN_YEAR_SHAPES,
      cross_year_normalized_shape_identity_verified=False,
      source_hour_count_per_year=HOURS_PER_SOURCE_YEAR,
      source_hour_certified_utc=False,
      resource_profiles_observed=False,
      resource_profiles=list(SYNTHETIC_SUPPLY),
      historical_duration_hours=list(DURATIONS),
      baseline_full_year_LP_cases=ORIGINAL_CASES,
      orthogonal_independent_P_E_LP_cases=ORTHOGONAL_CASES,
      battery_power_to_peak_ratios=list(FACTOR_P),
      battery_energy_to_peak_hour_ratios=list(FACTOR_E),
      interzonal_transmission_model_included=False,
      storage_capex_included=False,
      western_network_OPF=False,
      original_objective="5*(renewable_direct_MWh + renewable_charge_input_MWh) + 90*firm_MWh",
      original_initial_and_terminal_SOC_zero=True,
      assumed_round_trip_efficiency=.9)

def _node(ax,xy,width,height,title,body,face="#f5f7fa",edge="#a6b5c9"):
    x,y=xy
    patch=FancyBboxPatch((x,y),width,height,boxstyle="round,pad=0.018,rounding_size=0.018",
                         linewidth=1.1,edgecolor=edge,facecolor=face)
    ax.add_patch(patch)
    ax.text(x+.025,y+height-.045,title,fontsize=12,weight="bold",va="top",color="#1e334b")
    ax.text(x+.025,y+height-.103,body,fontsize=9.3,va="top",
            color="#25384a",linespacing=1.5)
def _arrow(ax,start,end):
    ax.add_patch(FancyArrowPatch(start,end,arrowstyle="-|>",mutation_scale=15,
                    linewidth=1.5,color="#72849a",connectionstyle="arc3,rad=0.0"))

def render(out_dir):
    v=verify_design()
    out=Path(out_dir)
    out.mkdir(parents=True,exist_ok=True)
    fig,ax=plt.subplots(figsize=(13.5,8.5))
    ax.set_xlim(0,1);ax.set_ylim(0,1);ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.text(.035,.955,"Figure 1 | From original projected demand to synthetic storage experiments",
            weight="bold",fontsize=17,color="#18334e")
    ax.text(.035,.913,"Data provenance, factor controls, and limits of inference",
            fontsize=11,color="#64748b")

    _node(ax,(.035,.657),.28,.205,"A  ORIGINAL INPUT",
          "EFS/LAF zonal projected demand\n2030, 2040, 2050\n20 zones/year × 8,760 source hours\nSource hour IDs are not certified UTC",
          face="#edf3fc",edge="#91afd2")
    _node(ax,(.355,.657),.285,.205,"B  SHAPE AUDIT",
          "19 nonzero + 1 zero-load zone/year\n7 distinct normalized nonzero shapes\nwithin EACH projection year\nNot 20 independent temporal replicates",
          face="#edf3fc",edge="#91afd2")
    _node(ax,(.68,.657),.282,.205,"C  ASSUMED SUPPLY",
          "Flat 50% • ordinal Wave A • Wave B\nSynthetic and equal annual mean\nNo observed solar/wind time series\nNo validated physical weather alignment",
          face="#fff6e9",edge="#ddb984")
    _arrow(ax,(.317,.76),(.351,.76));_arrow(ax,(.642,.76),(.675,.76))

    _node(ax,(.035,.34),.435,.215,"D  ORIGINAL STORAGE FACTORIAL",
          "20 zones × 3 planning years × 3 synthetic shapes × 3 durations\n540 annual HiGHS LPs; duration 0 / 4 / 8 h\nBattery power = 25% of original zone peak MW\nEnergy capacity = rated power × assumed duration",
          face="#eff7f2",edge="#92b9a1")
    _node(ax,(.53,.34),.432,.215,"E  INDEPENDENT POWER / ENERGY",
          "7 demand-shape representatives × 3 supply shapes × 3 P × 3 E\n189 annual HiGHS LPs, 2030 only\nP = 12.5%, 25%, 50% of peak MW\nE = 0.5, 1.0, 2.0 peak-MW-hour equivalents",
          face="#eff7f2",edge="#92b9a1")
    _arrow(ax,(.23,.652),(.23,.562))
    _arrow(ax,(.8,.652),(.8,.562))

    _node(ax,(.035,.103),.927,.145,"F  WHAT THE LP DOES — AND DOES NOT IDENTIFY",
          "Illustrative operating objective: $5/MWh for renewable direct use + charge input; $90/MWh for firm supply.\n90% assumed battery round-trip efficiency; zero initial/terminal SOC. Each zone operates separately.\nNo actual Western transmission OPF, observed renewables, storage CAPEX, degradation, or reliability certification.",
          face="#f8f8fa",edge="#b0b0bc")
    _arrow(ax,(.245,.336),(.245,.254))
    _arrow(ax,(.75,.336),(.75,.254))
    fig.text(.5,.032,"Source: accepted EFS shape audit #42464270811; original LP #42107237659; independent P/E LP #42674534963.",
        fontsize=8.2,ha="center",color="#66768a")
    fig.subplots_adjust(left=.02,right=.98,top=.98,bottom=.04)
    for ext in ("png","svg"):
        fig.savefig(out/f"Paper_S_proposed_main_Figure_1_source_workflow.{ext}",dpi=250,bbox_inches="tight")
    plt.close(fig)
    (out/"Paper_S_Figure_1_source_manifest.json").write_text(json.dumps(v,indent=2)+"\n")
    return v

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out-dir",type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(render(a.out_dir),indent=2))
if __name__=="__main__":main()
