"""Six-hour, 10-bus dispatch on a radial subtree of synthetic PyPSA-USA.

Source-model bus IDs and line electrical parameters are retained. Capacity
ratings, generators, renewables and demand are synthetic scenario assumptions.
This is NOT physical Palo Verde dispatch or a real Western system OPF.
"""
import argparse
import json
from collections import deque
from pathlib import Path

import numpy as np
import pandas as pd
import pypsa


def select_source_tree(source, anchor="2040841", target_buses=10):
    buses=source.buses
    if anchor not in buses.index:
        raise ValueError("Source anchor bus absent")
    if target_buses < 2:
        raise ValueError("At least two buses required")
    voltage=float(buses.loc[anchor,"v_nom"])
    lines=source.lines.copy()
    lines["r_numeric"]=pd.to_numeric(lines.r,errors="coerce")
    lines["x_numeric"]=pd.to_numeric(lines.x,errors="coerce")
    lines=lines.loc[lines.r_numeric.ge(0)&lines.x_numeric.gt(0)].sort_index()
    adjacency={str(k):[] for k in buses.index}
    for key,branch in lines.iterrows():
        a,b=str(branch.bus0),str(branch.bus1)
        if a not in adjacency or b not in adjacency or a==b:
            continue
        if abs(float(buses.loc[a,"v_nom"])-voltage)>0.01 or abs(float(buses.loc[b,"v_nom"])-voltage)>0.01:
            continue
        adjacency[a].append((str(key),b))
        adjacency[b].append((str(key),a))
    seen={anchor}
    queue=deque([anchor])
    chosen=[]
    while queue and len(seen)<target_buses:
        current=queue.popleft()
        for key,other in sorted(adjacency[current]):
            if other in seen:
                continue
            seen.add(other)
            queue.append(other)
            chosen.append((key,current,other))
            if len(seen)==target_buses:
                break
    if len(seen)!=target_buses or len(chosen)!=target_buses-1:
        raise ValueError(f"Source-model same-voltage component only supplied {len(seen)} of {target_buses} requested buses")
    return [anchor]+[v for _,_,v in chosen],chosen,lines,voltage


def experiment(network_path:Path,out:Path,anchor="2040841",target_buses=10,
               ratings=(60.0,120.0)):
    source=pypsa.Network(str(network_path))
    ids,tree,lines,voltage=select_source_tree(source,anchor,target_buses)
    if not ratings or any(not np.isfinite(k) or k<=0 for k in ratings):
        raise ValueError("Synthetic line capacity ratings must be positive finite values")
    hours=pd.date_range("2024-01-01",periods=6,freq="h")
    leaves=ids[1:]
    profiles=np.array([0.72,0.89,1.0,1.15,0.96,0.83])
    demand=pd.DataFrame({bus:(32+5*(i%5))*profiles for i,bus in enumerate(leaves)},index=hours)
    solar_pu=pd.Series([0.,0.15,0.55,0.9,0.48,0.1],index=hours)
    metrics=[]
    for rating in ratings:
        model=pypsa.Network()
        model.set_snapshots(hours)
        for bus in ids:
            model.add("Bus",bus,v_nom=voltage)
        for edge_id,_,_ in tree:
            edge=lines.loc[edge_id]
            model.add("Line",f"source_{edge_id}",bus0=str(edge.bus0),bus1=str(edge.bus1),
                      r=float(edge.r_numeric),x=float(edge.x_numeric),s_nom=float(rating))
        model.add("Generator","central_synthetic",bus=anchor,p_nom=1000,marginal_cost=20)
        solar_bus=leaves[0]
        model.add("Generator","renewable_synthetic",bus=solar_bus,p_nom=125,
                  marginal_cost=0,p_max_pu=solar_pu)
        for i,bus in enumerate(leaves):
            model.add("Generator",f"backup_{i}",bus=bus,p_nom=250,marginal_cost=100)
            model.add("Load",f"load_{i}",bus=bus,p_set=demand[bus])
        status,condition=model.optimize(solver_name="highs")
        if (status,condition)!=("ok","optimal"):
            raise RuntimeError(f"Synthetic 10-bus solve failed: {status}/{condition}")
        if len(model.lines)!=target_buses-1:
            raise AssertionError("The source topology must be an acyclic tree")
        total_cost=0.0
        rows=[]
        for t in hours:
            dispatch=model.generators_t.p.loc[t].astype(float)
            total_load=float(demand.loc[t].sum())
            generator_total=float(dispatch.sum())
            if abs(generator_total-total_load)>0.1:
                raise AssertionError("System-wide generator/load balance failed")
            if (dispatch < -0.1).any():
                raise AssertionError("Negative generator dispatch")
            renewable=float(dispatch["renewable_synthetic"])
            renewable_avail=125*float(solar_pu.loc[t])
            if renewable>renewable_avail+0.1 or renewable < -0.1:
                raise AssertionError("Renewable capacity/availability constraint violated")
            flow=model.lines_t.p0.loc[t].astype(float)
            if (flow.abs()>float(rating)+0.1).any():
                raise AssertionError("Source topology line rating exceeded")
            backup=float(dispatch[[f"backup_{i}" for i in range(len(leaves))]].sum())
            central=float(dispatch["central_synthetic"])
            cost=20*central+100*backup
            total_cost+=cost
            rows.append({
                "hour":str(t),"synthetic_demand_mw":total_load,"central_mw":central,
                "renewable_mw":renewable,"renewable_available_mw":renewable_avail,
                "renewable_curtailed_mw":max(0,renewable_avail-renewable),
                "backup_mw":backup,"line_max_abs_flow_mw":float(flow.abs().max()),
                "binding_lines_count":int(((float(rating)-flow.abs()).abs()<=0.15).sum()),
                "generator_load_balance_residual_mw":generator_total-total_load})
        if abs(total_cost-float(model.objective))>0.5:
            raise AssertionError("Dispatch-reconstructed objective differs from optimizer")
        metrics.append({"hypothetical_line_rating_mw":float(rating),
                        "total_synthetic_cost_units":float(model.objective),
                        "total_backup_mwh":sum(x["backup_mw"] for x in rows),
                        "total_renewable_mwh":sum(x["renewable_mw"] for x in rows),
                        "total_curtailment_mwh":sum(x["renewable_curtailed_mw"] for x in rows),
                        "snapshots":rows})
    if any(a["total_synthetic_cost_units"]>b["total_synthetic_cost_units"]+0.5
           for a,b in zip(metrics[1:],metrics[:-1])):
        raise AssertionError("Increased line capacity worsened optimal synthetic objective")
    result={
        "synthetic_western_source_topology":True,
        "actual_facility_electrical_connectivity_verified":False,
        "real_western_opf_executed":False,
        "source_model_bus_count":len(ids),
        "source_model_bus_ids":ids,
        "source_model_line_count":len(tree),
        "source_model_line_ids":[key for key,_,_ in tree],
        "source_model_line_parameters":[
            {"line_id":key,"bus0":str(lines.loc[key,"bus0"]),"bus1":str(lines.loc[key,"bus1"]),
             "r_ohm":float(lines.loc[key,"r_numeric"]),"x_ohm":float(lines.loc[key,"x_numeric"])}
            for key,_,_ in tree],
        "hour_count":len(hours),
        "experimental_input_status":"synthetic hourly demand, solar availability, line ratings, dispatch costs and backup generators",
        "hypothetical_scenarios":metrics,
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({
        "source_model_bus_count":result["source_model_bus_count"],
        "source_model_line_count":result["source_model_line_count"],
        "source_model_line_ids":result["source_model_line_ids"],
        "hour_count":result["hour_count"],
        "hypothetical_scenarios":[{k:v for k,v in m.items() if k!="snapshots"} for m in metrics],
        "real_western_opf_executed":False},indent=2))
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--network",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--anchor",default="2040841")
    p.add_argument("--buses",type=int,default=10)
    x=p.parse_args()
    experiment(x.network,x.out,x.anchor,x.buses)


if __name__=="__main__":
    main()
