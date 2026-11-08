"""Figure S9: relative 4h-to-8h battery discharge increment for seven source-shape groups.

Source is the accepted 21-row cross-shape, original-archive verified LP synthesis.
This is not an economic or physically calibrated Western grid performance measure.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SUPPLY={"flat_50pct":"Flat 50%","ordinal24_wave_A":"Synthetic wave A",
        "ordinal24_wave_B":"Synthetic wave B"}

def validate(df):
    required={"source_shape_group","state","reeds_zone","synthetic_supply_shape",
              "discharged_4h_gwh","discharged_8h_gwh","incremental_discharge_4to8h_gwh"}
    if not required.issubset(df):raise ValueError("Missing original comparison source fields")
    if len(df)!=21 or df.duplicated(["source_shape_group","synthetic_supply_shape"]).any():
        raise ValueError("Expected 21 distinct seven-group × three-shape comparisons")
    if set(df.source_shape_group)!={1,2,3,4,5,6,7} or set(df.synthetic_supply_shape)!=set(SUPPLY):
        raise ValueError("Unexpected original shape population")
    if df[["source_shape_group","state","reeds_zone"]].drop_duplicates().shape[0]!=7:
        raise ValueError("Source group representatives are not unique")
    vals=df[["discharged_4h_gwh","discharged_8h_gwh","incremental_discharge_4to8h_gwh"]].to_numpy(dtype=float)
    if not np.isfinite(vals).all() or (vals[:,:2]<0).any():
        raise ValueError("Nonfinite or negative original source discharge")
    if not np.allclose(vals[:,1]-vals[:,0],vals[:,2],atol=.00001,rtol=1e-10):
        raise ValueError("Marginal discharge incompatible with archived source totals")
    if (vals[:,0]<=0).any():
        raise ValueError("Relative increment undefined with zero 4h discharge")
    df=df.copy()
    df["additional_discharge_pct_of_4h"]=100*vals[:,2]/vals[:,0]
    return df.sort_values(["source_shape_group","synthetic_supply_shape"]).reset_index(drop=True)

def plot(df,out):
    a=validate(df)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    ids=list(range(1,8))
    labels=[]
    for i in ids:
        r=a[a.source_shape_group==i].iloc[0]
        labels.append(str(r.state))
    fig,ax=plt.subplots(figsize=(11.6,5.2))
    x=np.arange(7);w=.25
    for j,(shape,label) in enumerate(SUPPLY.items()):
        vals=a.loc[a.synthetic_supply_shape==shape].set_index("source_shape_group").loc[
            ids,"additional_discharge_pct_of_4h"].to_numpy()
        ax.bar(x+(j-1)*w,vals,width=w,label=label)
    ax.set_xticks(x,labels)
    ax.set_ylabel("Additional energy delivered at 8h vs 4h\n(% of 4h delivered energy)")
    ax.set_title("Figure S9 | Marginal storage use across seven distinct demand chronologies (2030)")
    ax.grid(axis="y",alpha=.22);ax.set_axisbelow(True)
    ax.legend(frameon=False,ncol=3,loc="upper right")
    fig.text(.5,.035,"EFS source demand + synthetic resource shapes; source ordinal hours. No battery CAPEX or real Western OPF.",
             ha="center",fontsize=8)
    fig.tight_layout(rect=[0,.055,1,1])
    for ext in (".png",".svg"):
        fig.savefig(out/("Figure_S9_2030_seven_shape_relative_increment"+ext),dpi=240,bbox_inches="tight")
    plt.close(fig)
    a.to_csv(out/"paper_s_2030_seven_shape_21_comparisons_with_relative_pct.csv",index=False)
    report={"status":"FIGURE_S9_SOURCE_ARCHIVED_21_COMPARISONS_PASS",
            "shape_groups":7,"supply_shapes":3,"source_year":2030,
            "physical_utc_certified":False,"actual_renewable_profiles":False,
            "battery_capex_included":False}
    (out/"Figure_S9_provenance_manifest.json").write_text(json.dumps(report,indent=2)+"\n")
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--comparisons",type=Path,required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(plot(pd.read_csv(a.comparisons),a.out_dir),indent=2))

if __name__=="__main__":main()
