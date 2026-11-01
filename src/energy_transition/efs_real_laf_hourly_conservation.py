"""Independently reconcile EFS local-hour to real-LAF zonal pilot outputs.

No UTC synchronization or power-system optimization is implied.
"""
import argparse
import json
import numpy as np
import pandas as pd
import pypsa
from pathlib import Path

STATES={"AZ":"Arizona","CO":"Colorado","ID":"Idaho","MT":"Montana","NM":"New Mexico","UT":"Utah","WY":"Wyoming"}

def audit(network, source, zonal):
    n=pypsa.Network(str(network))
    bus=n.buses
    actual={s:float(pd.to_numeric(g.LAF_state,errors="coerce").sum()) for s,g in bus.groupby("state")}
    src=pd.read_csv(source,compression="gzip")
    src["state"]=src["state"].map(STATES)
    src=src.dropna(subset=["state"])
    z=pd.read_csv(zonal,compression="gzip")
    if z.empty or src.empty: raise ValueError("Empty pilot input")
    source_keys=set(map(tuple,src[["year","state","local_hour_id"]].itertuples(index=False,name=None)))
    result_keys=set(map(tuple,z[["year","state","local_hour_id"]].drop_duplicates().itertuples(index=False,name=None)))
    if source_keys != result_keys: raise ValueError(f"Local-hour coverage differs: {len(source_keys)} source, {len(result_keys)} allocated")
    if not np.isfinite(z.allocated_mw).all() or (z.allocated_mw<0).any(): raise ValueError("Invalid zonal MW")
    a=z.groupby(["year","state","local_hour_id"]).allocated_mw.sum()
    b=src.set_index(["year","state","local_hour_id"]).load_mw
    expected=b*b.index.get_level_values("state").map(actual)
    deviation=(a.reindex(expected.index)-expected).abs()
    if deviation.isna().any() or not np.allclose(a.reindex(expected.index),expected,rtol=1e-9,atol=1e-5):
        raise ValueError(f"Hourly load conservation failed, max MW error={deviation.max()}")
    return {"source_state_hours":len(src),"audited_state_hours":len(a),"zonal_rows":len(z),
            "maximum_absolute_hourly_mass_error_mw":float(deviation.max()),
            "state_laf_sums":{s:actual[s] for s in sorted(STATES.values())},
            "hourly_mass_conservation_verified":True,
            "utc_snapshot_alignment_verified":False,
            "full_western_network_optimized":False}

def main():
    p=argparse.ArgumentParser()
    for k in ("network","source","zonal","out"):p.add_argument("--"+k,required=True,type=Path)
    a=p.parse_args()
    result=audit(a.network,a.source,a.zonal)
    a.out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
