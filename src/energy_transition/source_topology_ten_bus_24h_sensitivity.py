"""24-hour synthetic Western source-tree congestion and solar sensitivity.

Topological bus/line identities and source line r/x are copied from a pinned
Breakthrough Energy synthetic source network; all loads, generator fleets,
ratings, costs, solar profiles, and times are explicitly invented scenarios.
No actual Western electric dispatch or EIA860 interconnection is inferred.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pypsa

from .source_topology_ten_bus_six_hour_opf import select_source_tree


def hourly_profile():
    hour=np.arange(24,dtype=float)
    load_multiplier=0.75+0.32*np.exp(-0.5*((hour-19)/3.0)**2)+0.13*np.exp(-0.5*((hour-9)/3.5)**2)
    solar_availability=np.clip(np.sin(np.pi*(hour-6)/12),0,1)
    return load_multiplier,solar_availability


def experiment(network_path:Path,out:Path,anchor="2040841",
               capacities=(45.0,75.0,120.0),solar_nameplates=(75.0,200.0)):
    source=pypsa.Network(str(network_path))
    ids,tree,lines,voltage=select_source_tree(source,anchor,10)
    if len(capacities)<2 or not all(np.isfinite(x) and x>0 for x in capacities):
        raise ValueError("Require at least two positive line capacity scenarios")
    if len(solar_nameplates)<2 or not all(np.isfinite(x) and x>=0 for x in solar_nameplates):
        raise ValueError("Require at least two nonnegative solar scenarios")
    if sorted(capacities)!=list(capacities) or sorted(solar_nameplates)!=list(solar_nameplates):
        raise ValueError("Scenario values must be sorted in ascending order")
    snapshots=pd.date_range("2024-01-01",periods=24,freq="h")
    load_factor,solar_factor=hourly_profile()
    leaf_buses=ids[1:]
    load=pd.DataFrame({bus:(35+6*(i%4))*load_factor for i,bus in enumerate(leaf_buses)},
                      index=snapshots)
    solar_pu=pd.Series(solar_factor,index=snapshots)
    output=[]
    for nameplate in solar_nameplates:
        for rating in capacities:
            n=pypsa.Network()
            n.set_snapshots(snapshots)
            for bus in ids:
                n.add("Bus",bus,v_nom=voltage)
            for key,_,_ in tree:
                r=lines.loc[key]
                n.add("Line",f"source_{key}",bus0=str(r.bus0),bus1=str(r.bus1),
                      r=float(r.r_numeric),x=float(r.x_numeric),s_nom=rating)
            n.add("Generator","central_supply",bus=anchor,p_nom=1500,marginal_cost=20)
            n.add("Generator","solar_supply",bus=leaf_buses[0],p_nom=nameplate,
                  p_max_pu=solar_pu,marginal_cost=0)
            for i,bus in enumerate(leaf_buses):
                n.add("Generator",f"backup_{i}",bus=bus,p_nom=250,marginal_cost=100)
                n.add("Load",f"load_{i}",bus=bus,p_set=load[bus])
            status,condition=n.optimize(solver_name="highs")
            if (status,condition)!=("ok","optimal"):
                raise RuntimeError(f"HiGHS solve failed: {status}/{condition}")
            records=[]
            line_congested_hours={str(k):0 for k,_,_ in tree}
            line_absolute_flow_mwh={str(k):0.0 for k,_,_ in tree}
            line_peak_mw={str(k):0.0 for k,_,_ in tree}
            # Locational marginal prices reflect this synthetic linear OPF only.
            prices=n.buses_t.marginal_price
            if not set(ids).issubset(prices.columns) or prices.reindex(index=snapshots,columns=ids).isna().any().any():
                raise AssertionError("Missing source-topology synthetic nodal marginal prices")
            line_price_spread_sum={str(k):0.0 for k,_,_ in tree}
            for t in snapshots:
                p=n.generators_t.p.loc[t].astype(float)
                flow0=n.lines_t.p0.loc[t].astype(float)
                flow1=n.lines_t.p1.loc[t].astype(float)
                demand=float(load.loc[t].sum())
                residual=float(p.sum()-demand)
                if abs(residual)>0.15:
                    raise AssertionError("System energy mismatch")
                bus_residuals=[]
                for bus in ids:
                    local_gens=n.generators.index[n.generators.bus.eq(bus)]
                    local_gen=float(p.loc[local_gens].sum())
                    local_load=float(load.at[t,bus]) if bus in leaf_buses else 0.0
                    withdrawal=float(flow0.loc[n.lines.index[n.lines.bus0.eq(bus)]].sum()+
                                     flow1.loc[n.lines.index[n.lines.bus1.eq(bus)]].sum())
                    bus_residuals.append(local_gen-local_load-withdrawal)
                max_nodal=max(abs(x) for x in bus_residuals)
                if max_nodal>0.15:
                    raise AssertionError("Source-topology nodal power balance failed")
                if (flow0.abs()>rating+0.15).any():
                    raise AssertionError("Hypothetical line rating exceeded")
                for key,_,_ in tree:
                    magnitude=abs(float(flow0.at[f"source_{key}"]))
                    line_absolute_flow_mwh[str(key)]+=magnitude
                    line_peak_mw[str(key)]=max(line_peak_mw[str(key)],magnitude)
                    if magnitude>=rating-0.15:
                        line_congested_hours[str(key)]+=1
                    branch=lines.loc[key]
                    spread=abs(float(prices.at[t,str(branch.bus0)])-
                               float(prices.at[t,str(branch.bus1)]))
                    if not np.isfinite(spread):
                        raise AssertionError("Non-finite synthetic nodal price spread")
                    line_price_spread_sum[str(key)]+=spread
                available=nameplate*float(solar_pu.at[t])
                solar=float(p["solar_supply"])
                if solar < -0.15 or solar>available+0.15:
                    raise AssertionError("Synthetic solar availability exceeded")
                central=float(p["central_supply"])
                backup=float(p.filter(like="backup_").sum())
                records.append({
                    "hour":int(t.hour),
                    "demand_mw":demand,
                    "central_mw":central,
                    "solar_mw":solar,
                    "backup_mw":backup,
                    "solar_available_mw":available,
                    "curtailed_solar_mw":max(0,available-solar),
                    "max_line_abs_flow_mw":float(flow0.abs().max()),
                    "congested_line_count":int((flow0.abs()>=rating-0.15).sum()),
                    "max_nodal_residual_mw":float(max_nodal),
                    "global_balance_residual_mw":residual,
                })
            objective=float(n.objective)
            reconstructed=sum(20*x["central_mw"]+100*x["backup_mw"] for x in records)
            if abs(objective-reconstructed)>max(0.5,0.00001*abs(objective)):
                raise AssertionError("Optimizer objective differs from dispatch accounting")
            if sum(line_congested_hours.values())!=sum(x["congested_line_count"] for x in records):
                raise AssertionError("Per-line and aggregate congestion counts inconsistent")
            output.append({
                "per_source_line_metrics":[
                    {"source_line_id":str(key),
                     "congested_hours":line_congested_hours[str(key)],
                     "peak_abs_flow_mw":line_peak_mw[str(key)],
                     "sum_abs_flow_mwh":line_absolute_flow_mwh[str(key)],
                     "sum_absolute_nodal_price_spread_units_per_mwh_hours":line_price_spread_sum[str(key)],
                     "hypothetical_rating_mw":float(rating)}
                    for key,_,_ in tree],
                "hypothetical_line_capacity_mw":rating,
                "hypothetical_solar_nameplate_mw":nameplate,
                "objective_synthetic_cost_units":objective,
                "daily_demand_mwh":sum(x["demand_mw"] for x in records),
                "daily_backup_mwh":sum(x["backup_mw"] for x in records),
                "daily_solar_mwh":sum(x["solar_mw"] for x in records),
                "daily_solar_curtailment_mwh":sum(x["curtailed_solar_mw"] for x in records),
                "congested_line_hours":sum(x["congested_line_count"] for x in records),
                "max_nodal_residual_mw":max(x["max_nodal_residual_mw"] for x in records),
                "hourly":records,
            })
    for solar in solar_nameplates:
        objs=[x["objective_synthetic_cost_units"] for x in output if x["hypothetical_solar_nameplate_mw"]==solar]
        if any(a<b-0.5 for a,b in zip(objs,objs[1:])):
            raise AssertionError("More transmission capacity increased optimum synthetic cost")
    for rating in capacities:
        objs=[x["objective_synthetic_cost_units"] for x in output if x["hypothetical_line_capacity_mw"]==rating]
        if any(a<b-0.5 for a,b in zip(objs,objs[1:])):
            raise AssertionError("More zero-marginal-cost solar increased optimum synthetic cost")
    result={
        "model_type":"synthetic 10-bus 24-hour DC-linearized transmission-constrained OPF",
        "source_topology":"pinned PyPSA-USA Breakthrough Energy synthetic USATestSystem",
        "source_bus_ids":ids,
        "source_line_ids":[key for key,_,_ in tree],
        "source_line_resistance_reactance_ohms":[{"id":key,"r":float(lines.loc[key,"r_numeric"]),
                 "x":float(lines.loc[key,"x_numeric"])} for key,_,_ in tree],
        "hours":24,
        "scenarios":len(output),
        "source_facility_to_generator_bus_verified":False,
        "real_western_opf_executed":False,
        "all_operational_inputs_synthetic":True,
        "hourly_cases":output,
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"source_model_buses":len(ids),"source_model_lines":len(tree),
                      "hours":24,"scenario_count":len(output),
                      "scenario_metrics":[{k:v for k,v in x.items() if k!="hourly"} for x in output],
                      "real_western_opf_executed":False},indent=2))
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--network",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--anchor",default="2040841")
    a=p.parse_args()
    experiment(a.network,a.out,a.anchor)


if __name__=="__main__":
    main()
