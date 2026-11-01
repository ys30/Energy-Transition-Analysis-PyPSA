"""Reimport real EFS load-bearing NetCDF and check original zonal MWh."""
import argparse,json
from pathlib import Path
import pandas as pd
import numpy as np
import pypsa

def validate(network,zonal,year):
    n=pypsa.Network(str(network))
    z=pd.read_csv(zonal,compression="gzip")
    z=z[z.year==year]
    if len(n.snapshots)!=8760 or n.loads.empty: raise ValueError("Missing 8760h loads")
    if n.loads_t.p_set.isna().any().any():raise ValueError("NaN load")
    actual=float(n.loads_t.p_set.to_numpy().sum())
    expected=float(z.allocated_mw.sum())
    if not np.isclose(actual,expected,rtol=1e-10,atol=0.01):
        raise ValueError(f"Energy loss: {actual} versus {expected}")
    if set(n.loads.bus)-set(n.buses.index): raise ValueError("Missing bus references")
    return {"year":year,"load_components":len(n.loads),"snapshots":len(n.snapshots),
            "expected_source_zonal_mwh":expected,"reloaded_network_mwh":actual,
            "absolute_mwh_error":abs(actual-expected),"verified_netCDF_roundtrip":True,
            "timezone_aligned":False,"full_grid_solve":False}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--network",type=Path,required=True)
    p.add_argument("--zonal",type=Path,required=True)
    p.add_argument("--year",type=int,default=2030)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    r=validate(a.network,a.zonal,a.year)
    a.out.write_text(json.dumps(r,indent=2)+"\n");print(json.dumps(r,indent=2))
