"""Constrained 6-bus / 5-real-line Western PyPSA dispatch demonstration.

Actual line geometry/electrical inputs and EFS bus demand; generation and
supply costs are illustrative, never interpreted as observed Western assets.
"""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
import pypsa

def solve(path,out,hours=24):
 src=pypsa.Network(str(path))
 target="2074132"
 line_ids=["100242","100243","100244","100245","100246"]
 lines=src.lines.loc[line_ids]
 buses=set(lines.bus0)|set(lines.bus1)
 if target not in buses or len(buses)!=6: raise ValueError("Expected actual six-bus network differs")
 if len(lines)!=5: raise ValueError("Expected five actual lines")
 sub=pypsa.Network()
 sub.set_snapshots(src.snapshots[:hours])
 for b in sorted(buses):
  sub.add("Bus",str(b),v_nom=float(src.buses.at[b,"v_nom"]))
 for lid,r in lines.iterrows():
  if not (float(r.x)>0 and float(r.s_nom)>=100): raise ValueError("Invalid actual line")
  sub.add("Line",str(lid),bus0=str(r.bus0),bus1=str(r.bus1),
          r=float(r.r),x=float(r.x),s_nom=float(r.s_nom))
 load_ids=src.loads.index[src.loads.bus==target]
 load=src.loads_t.p_set.loc[src.snapshots[:hours],load_ids].sum(axis=1)
 if load.isna().any() or (load<=0).any():raise ValueError("Invalid EFS real load")
 sub.add("Load","actual_efs",bus=target,p_set=load.to_numpy())
 peak=float(load.max())
 remote=next(b for b in sorted(buses) if b!=target)
 sub.add("Generator","illustrative_remote",bus=remote,p_nom=peak*3,marginal_cost=10)
 sub.add("Generator","illustrative_local",bus=target,p_nom=peak*3,marginal_cost=100)
 status,condition=sub.optimize(solver_name="highs")
 if (status,condition)!=("ok","optimal"):raise RuntimeError(f"Solver {status}/{condition}")
 actual=float(sub.loads_t.p_set.to_numpy().sum())
 output=float(sub.generators_t.p.to_numpy().sum())
 if abs(actual-output)>max(0.01,actual*1e-8):raise ValueError("Power balance failed")
 max_ratio=float((sub.lines_t.p0.abs()/sub.lines.s_nom).max().max())
 if max_ratio>1.000001:raise ValueError("Thermal line limit violated")
 utilization=(sub.lines_t.p0.abs()/sub.lines.s_nom)
 congested=utilization.columns[(utilization>=0.999999).any(axis=0)].tolist()
 line_peak={str(k):float(utilization[k].max()) for k in utilization.columns}
 # Expose topology, line flow and generator placement for diagnosing unused branches.
 adjacency={str(b):[] for b in buses}
 for lid,r in lines.iterrows():
  u,v=str(r.bus0),str(r.bus1)
  adjacency[u].append({"neighbor":v,"line_id":str(lid)})
  adjacency[v].append({"neighbor":u,"line_id":str(lid)})
 seen={target}
 queue=[target]
 while queue:
  node=queue.pop(0)
  for item in adjacency[node]:
   nxt=item["neighbor"]
   if nxt not in seen:
    seen.add(nxt)
    queue.append(nxt)
 if seen!=set(map(str,buses)):
  raise ValueError("Selected original-line six-bus topology is disconnected")
 line_flow_peak_mw={str(k):float(sub.lines_t.p0[k].abs().max()) for k in sub.lines.index}
 generator_energy_mwh={str(k):float(sub.generators_t.p[k].sum()) for k in sub.generators.index}
 unused_line_ids=[k for k,v in line_flow_peak_mw.items() if v<1e-7]
 if not congested:raise ValueError("No thermal limit binding in pilot")
 result={"planning_year":int(src.snapshots[0].year),
         "binding_line_ids":[str(k) for k in congested],
         "maximum_utilization_by_line":line_peak,
         "binding_line_count":len(congested),
         "selected_topology_connected":True,
         "line_adjacency":adjacency,
         "line_peak_abs_flow_mw":line_flow_peak_mw,
         "unused_line_ids":unused_line_ids,
         "generator_bus_assignments":{"illustrative_remote":remote,"illustrative_local":target},
         "generator_energy_mwh":generator_energy_mwh,
         "thermal_binding_verified":True,
         "buses":len(buses),"real_lines":len(lines),"hours":hours,
         "actual_efs_mwh":actual,"dispatched_mwh":output,
         "max_line_thermal_utilization":max_ratio,
         "solver_status":status,"solver_condition":condition,
         "illustrative_cost_usd":float(sub.objective),
         "real_line_parameters":True,"generation_illustrative":True,
         "full_western_optimized":False,"timezone_aligned":False}
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result,indent=2))
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--network",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args();solve(a.network,a.out)
