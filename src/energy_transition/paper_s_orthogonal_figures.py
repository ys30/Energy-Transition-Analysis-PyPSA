"""Reproducible Figures S11/S12 from verified orthogonal LP one-axis contrasts."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SHAPES=("flat_50pct","ordinal24_wave_A","ordinal24_wave_B")
POWERS=(.125,.25,.5)
ENERGIES=(.5,1.,2.)

def verify(cases,contrasts):
    req={"source_shape_group","synthetic_supply_shape","battery_power_peak_ratio",
         "battery_energy_peak_hours","storage_discharge_to_load_mwh"}
    needed={"source_shape_group","synthetic_supply_shape","axis","held_constant",
            "from_level","to_level","added_discharge_mwh"}
    if not req.issubset(cases) or not needed.issubset(contrasts):
        raise ValueError("Missing original source-derived factorial columns")
    if len(cases)!=189 or len(contrasts)!=252:
        raise ValueError("Incomplete 189-LP / 252-contrast source population")
    if set(cases.source_shape_group)!=set(range(1,8)) or set(cases.synthetic_supply_shape)!=set(SHAPES):
        raise ValueError("Unexpected source-demand group population")
    if cases.duplicated(["source_shape_group","synthetic_supply_shape",
                         "battery_power_peak_ratio","battery_energy_peak_hours"]).any():
        raise ValueError("Duplicate source factorial cell")
    for record in contrasts.itertuples(index=False):
        g=cases[(cases.source_shape_group==record.source_shape_group)&
                (cases.synthetic_supply_shape==record.synthetic_supply_shape)]
        if record.axis=="energy_at_fixed_power":
            a=g[(g.battery_power_peak_ratio==record.held_constant)&
                (g.battery_energy_peak_hours==record.from_level)]
            b=g[(g.battery_power_peak_ratio==record.held_constant)&
                (g.battery_energy_peak_hours==record.to_level)]
        elif record.axis=="power_at_fixed_energy":
            a=g[(g.battery_energy_peak_hours==record.held_constant)&
                (g.battery_power_peak_ratio==record.from_level)]
            b=g[(g.battery_energy_peak_hours==record.held_constant)&
                (g.battery_power_peak_ratio==record.to_level)]
        else:raise ValueError("Unexpected comparison axis")
        if len(a)!=1 or len(b)!=1:raise ValueError("Missing unique source pair")
        actual=float(b.storage_discharge_to_load_mwh.iloc[0]-a.storage_discharge_to_load_mwh.iloc[0])
        if not np.isclose(actual,record.added_discharge_mwh,rtol=1e-9,atol=.001):
            raise ValueError("Contrasts do not reconcile to original LP grid")
    return contrasts.copy()

def generate(cases,contrasts,out):
    data=verify(cases,contrasts)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    produced=[]
    for axis,basename,title,label in (
        ("energy_at_fixed_power","Figure_S11_fixed_MW_increment_MWh",
         "Figure S11: increasing MWh at fixed MW","Power/peak"),
        ("power_at_fixed_energy","Figure_S12_fixed_MWh_increment_MW",
         "Figure S12: increasing MW at fixed MWh","Energy/peak-hour")
    ):
        d=data[data.axis==axis].copy()
        d["positive"]=d.added_discharge_mwh>1e-3
        counts=(d.groupby(["synthetic_supply_shape","held_constant","from_level","to_level"],
                          as_index=False).positive.sum())
        steps=sorted(set(zip(counts.from_level,counts.to_level)))
        hold=sorted(counts.held_constant.unique())
        names={"flat_50pct":"Flat","ordinal24_wave_A":"Wave A","ordinal24_wave_B":"Wave B"}
        ticks=[f"{names[shape]}\\n{label} {h:g}" for shape in SHAPES for h in hold]
        fig,ax=plt.subplots(figsize=(12.2,5.3))
        positions=np.arange(len(ticks))
        for idx,(before,after) in enumerate(steps):
            vals=[int(counts[(counts.synthetic_supply_shape==shape)&
                (counts.held_constant==h)&(counts.from_level==before)&
                (counts.to_level==after)].positive.iloc[0]) for shape in SHAPES for h in hold]
            bars=ax.bar(positions+(idx-.5)*.34,vals,width=.32,label=f"{before:g} to {after:g}")
            ax.bar_label(bars,padding=2,fontsize=8)
        ax.set_xticks(positions,[t.replace("\\n","\n") for t in ticks])
        ax.set_yticks(range(8));ax.set_ylim(0,8)
        ax.set_ylabel("Demand-shape groups with increased annual discharge (of 7)")
        ax.set_title(title);ax.grid(axis="y",alpha=.2);ax.set_axisbelow(True)
        ax.legend(frameon=False,title="One-axis increment")
        fig.text(.5,.01,"EFS source-ordinal load + synthetic resource shapes. No physical UTC, battery CAPEX or Western OPF.",ha="center",fontsize=8)
        fig.tight_layout(rect=[0,.05,1,1])
        for ext in (".png",".svg"):
            name=basename+ext
            fig.savefig(out/name,dpi=210,bbox_inches="tight")
            produced.append(name)
        plt.close(fig)
    report={"status":"SOURCE_189_LP_252_AXIS_CONTRAST_FIGURE_AUDIT_PASS",
            "source_LP_cases":189,"reconciled_one_axis_contrasts":252,
            "files":produced,"source_clock_utc_verified":False,
            "actual_renewable_supply":False,"battery_capex_included":False}
    (out/"Figures_S11_S12_manifest.json").write_text(json.dumps(report,indent=2)+"\n")
    return report

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--cases",type=Path,required=True)
    a.add_argument("--contrasts",type=Path,required=True)
    a.add_argument("--out-dir",type=Path,required=True)
    x=a.parse_args()
    report=generate(pd.read_csv(x.cases),pd.read_csv(x.contrasts),x.out_dir)
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
