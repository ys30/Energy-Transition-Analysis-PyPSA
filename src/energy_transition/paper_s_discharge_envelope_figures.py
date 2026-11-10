"""Figure S17: annual discharge envelope width as fraction of original discharge.

Shows stability of delivered energy, not SOC occupancy or pointwise trace
stability, for 8 archived source-backed explicitly cost-capped configurations.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SUPPLY={"flat_50pct":"Flat","ordinal24_wave_A":"Wave A",
        "ordinal24_wave_B":"Wave B"}
KEY=["source_shape_group","state","reeds_zone","synthetic_supply_shape",
     "battery_power_peak_ratio","battery_energy_peak_hours"]

def validate(a):
    required=set(KEY+["baseline","min","max","width_mwh"])
    if not required.issubset(a):raise ValueError("Missing archived original discharge bounds")
    if len(a)!=8 or set(a.source_shape_group)!={1,7} or a.duplicated(KEY).any():
        raise ValueError("Expected eight source-archived discharge configurations")
    v=a[["baseline","min","max","width_mwh"]].to_numpy(dtype=float)
    if not np.isfinite(v).all() or (v[:,0]<=0).any() or (v[:,1]<-1e-4).any():
        raise ValueError("Invalid or nonfinite source discharge")
    if not np.allclose(v[:,2]-v[:,1],v[:,3],atol=.0002,rtol=1e-9):
        raise ValueError("Original discharge envelope width does not reconcile")
    if (v[:,1]>v[:,0]+.02).any() or (v[:,0]>v[:,2]+.02).any():
        raise ValueError("Original optimum discharge lies outside envelope")
    keys=set(zip(a.source_shape_group,a.synthetic_supply_shape,
                 a.battery_power_peak_ratio,a.battery_energy_peak_hours))
    expected={(g,s,p,e) for g in (1,7)
              for s,p,e in (("flat_50pct",.25,1.),("ordinal24_wave_A",.125,.5),
                            ("ordinal24_wave_A",.25,1.),("ordinal24_wave_B",.25,1.))}
    if keys!=expected:raise ValueError("Source capacity/supply probe identities changed")
    x=a.copy()
    x["relative_discharge_span_pct"]=100*x.width_mwh/x.baseline
    x["label"]=x.apply(lambda r:("Arizona" if r.source_shape_group==1 else "Wyoming")+
        " · "+SUPPLY[r.synthetic_supply_shape]+
        (" (P 12.5%)" if r.synthetic_supply_shape=="ordinal24_wave_A" and
            r.battery_power_peak_ratio==.125 else ""),axis=1)
    return x.sort_values(KEY).reset_index(drop=True)

def render(a,out):
    x=validate(a);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    fig,ax=plt.subplots(figsize=(11,5.1))
    yy=np.arange(len(x))[::-1]
    colors=["#3975a3" if g==1 else "#d39340" for g in x.source_shape_group]
    ax.barh(yy,x.relative_discharge_span_pct,color=colors,height=.62)
    for y,v in zip(yy,x.relative_discharge_span_pct):
        ax.text(v+.00055,y,f"{v:.5f}%",va="center",fontsize=9)
    ax.set_yticks(yy,x.label)
    ax.set_xlim(0,max(.036,float(x.relative_discharge_span_pct.max())*1.22))
    ax.set_xlabel("Discharge min–max interval as % of archived baseline annual discharge")
    ax.set_title("Figure S17 | Near-optimal annual delivered-energy envelope (2030)")
    ax.grid(axis="x",alpha=.19);ax.set_axisbelow(True)
    fig.text(.5,.014,"Original EFS ordinal demand + synthetic supply; cost cap = max($0.05, 1e-9 × C*). Not pointwise bounds, actual renewables or CAPEX.",
             ha="center",fontsize=8)
    fig.tight_layout(rect=[0,.05,1,1])
    for ext in (".png",".svg"):
        fig.savefig(out/("Figure_S17_discharge_envelope_relative_width"+ext),
                    dpi=230,bbox_inches="tight")
    plt.close(fig)
    x.to_csv(out/"paper_s_eight_discharge_relative_envelopes.csv",index=False)
    meta={"status":"PAPER_S_S17_SOURCE_ARCHIVED_8_DISCHARGE_ENVELOPES",
          "source_LP_solutions":24,"intervals":8,
          "statement":"cost-capped annual discharged energy, not SOC occupancy",
          "pointwise_hourly_traces_bounded":False,"actual_renewable_data":False}
    (out/"Figure_S17_manifest.json").write_text(json.dumps(meta,indent=2)+"\n")
    return meta

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--out-dir",required=True,type=Path)
    x=p.parse_args()
    print(json.dumps(render(pd.read_csv(x.source),x.out_dir),indent=2))
if __name__=="__main__":main()
