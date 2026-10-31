"""One-hour solver smoke using a real NARIS directional interface rating.

Demand, generator costs and capacities are SYNTHETIC. This tests whether the
real published interface rating binds in PyPSA, not historical grid dispatch.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import pypsa

def solve_one_interface(source:Path)->dict:
    original=pypsa.Network(source)
    if len(original.links)==0: raise ValueError("No NARIS interfaces")
    chosen=original.links.sort_values("p_nom",ascending=False).iloc[0]
    a,b=str(chosen.bus0),str(chosen.bus1)
    rating=float(chosen.p_nom)
    if rating<=0: raise ValueError("Invalid interface rating")
    n=pypsa.Network()
    n.set_snapshots(["2024-01-01T00:00"])
    n.add("Bus",a)
    n.add("Bus",b)
    n.add("Link","naris_interface",bus0=a,bus1=b,p_nom=rating,
          p_min_pu=0,p_max_pu=1,efficiency=1)
    demand=rating*1.5
    n.add("Load","hypothetical_load",bus=b,p_set=demand)
    n.add("Generator","hypothetical_remote_supply",bus=a,p_nom=demand,marginal_cost=1)
    n.add("Generator","hypothetical_local_backup",bus=b,p_nom=demand,marginal_cost=100)
    status,condition=n.optimize(solver_name="highs")
    if status!="ok" or condition!="optimal": raise ValueError(f"Solver failed: {status}/{condition}")
    transfer=float(n.links_t.p0.loc[n.snapshots[0],"naris_interface"])
    backup=float(n.generators_t.p.loc[n.snapshots[0],"hypothetical_local_backup"])
    tol=max(1e-3,rating*1e-5)
    if abs(transfer-rating)>tol or abs(backup-(demand-rating))>tol:
        raise ValueError("Expected NARIS capacity-constrained dispatch not observed")
    return {"source_interface":f"{a} -> {b}","published_directional_rating_mw":rating,
            "synthetic_demand_mw":demand,"optimized_link_transfer_mw":transfer,
            "optimized_local_backup_mw":backup,"solver_status":status,
            "source_network_buses":len(original.buses),
            "source_network_links":len(original.links),
            "test_scope":"one extracted published NARIS interface; all generation and load hypothetical",
            "full_network_solved":False,"historical_calibration":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--network",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    args=p.parse_args()
    result=solve_one_interface(args.network)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
