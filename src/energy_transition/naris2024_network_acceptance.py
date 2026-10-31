"""Validate exported source-backed NARIS zonal topology, no dispatch claims."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pypsa

def audit(path):
    n=pypsa.Network(path)
    if len(n.buses)==0 or len(n.links)==0: raise ValueError("Empty source-backed network")
    if len(n.lines): raise ValueError("NARIS zonal interfaces must not be AC Lines")
    if not n.links.bus0.isin(n.buses.index).all() or not n.links.bus1.isin(n.buses.index).all():
        raise ValueError("Link endpoint missing")
    if (n.links.bus0==n.links.bus1).any(): raise ValueError("Self-interface")
    capacities=n.links.p_nom.to_numpy(dtype=float)
    if not np.isfinite(capacities).all() or (capacities<=0).any(): raise ValueError("Invalid directional capacity")
    if not np.allclose(n.links.efficiency.to_numpy(dtype=float),1): raise ValueError("Unexpected efficiency")
    return {"bus_count":len(n.buses),"directed_link_count":len(n.links),
            "ac_line_count":len(n.lines),"capacity_mw_total_directional":float(capacities.sum()),
            "min_link_rating_mw":float(capacities.min()),"max_link_rating_mw":float(capacities.max()),
            "network_solved":False,"historical_calibrated":False,
            "status":"source_backed_zonal_topology_verified_not_operational_dispatch"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--network",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    a=p.parse_args()
    result=audit(a.network)
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
