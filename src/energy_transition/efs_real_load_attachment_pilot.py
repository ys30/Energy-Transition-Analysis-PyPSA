"""Build an explicitly LOCAL-HOUR-labelled PyPSA load-only pilot.

This is a demand attachment proof, not a UTC-aligned or solved network.
"""
import argparse
import json
from pathlib import Path
import pandas as pd
import pypsa


def attach(base: Path, zonal: Path, out: Path, year: int):
    n=pypsa.Network(str(base))
    z=pd.read_csv(zonal,compression="gzip")
    z=z[z.year==year]
    if z.empty: raise ValueError("No selected EFS year")
    if z.local_hour_id.nunique()!=8760: raise ValueError("Incomplete local hour IDs")
    # Snapshot labels are synthetic ordinal timestamps; no UTC identity claimed.
    n.set_snapshots(pd.date_range(f"{year}-01-01",periods=8760,freq="h"))
    for (state,zone),series in z.groupby(["state","reeds_zone"]):
        buses=n.buses.index[(n.buses.state==state)&(n.buses.reeds_zone==zone)]
        if len(buses)==0: raise ValueError(f"Missing real bus for {state}/{zone}")
        # Dedicated zonal load bus: choose a real existing bus, do not split by counts.
        target=buses[0]
        vals=series.set_index("local_hour_id").allocated_mw.reindex(range(1,8761))
        if vals.isna().any(): raise ValueError(f"Missing local hour {state}/{zone}")
        n.add("Load",f"EFS_{year}_{zone}_{state}",bus=target,p_set=vals.to_numpy())
    out.parent.mkdir(parents=True,exist_ok=True)
    n.export_to_netcdf(str(out))
    report={"year":year,"loads_attached":len(n.loads),"snapshots":len(n.snapshots),
            "load_allocation_scope":"seven-state real LAF zonal pilot",
            "one_real_bus_per_zone":True,
            "ordinal_local_hour_only":True,
            "timezone_aligned":False,"optimized":False,
            "load_mwh":float(n.loads_t.p_set.sum().sum())}
    print(json.dumps(report,indent=2))
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--network",type=Path,required=True)
    p.add_argument("--zonal",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--year",type=int,default=2030)
    a=p.parse_args()
    attach(a.network,a.zonal,a.out,a.year)
