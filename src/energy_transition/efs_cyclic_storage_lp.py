"""Cyclic-SOC HiGHS LP on source-backed EFS ordinal loads and synthetic supply.

Pilot: a scoped 168-hour window; NEVER inferred to be UTC or physical Western OPF.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
from .efs_ordinal_storage_sensitivity import dispatch_zone,shape_cf

SHAPES=("flat_50pct","ordinal24_wave_A","ordinal24_wave_B")
DURATIONS=(0,4,8)
ETA=np.sqrt(.9)

def solve_zone(demand,cf,duration,*,renewable_peak_ratio=.9,battery_power_peak_ratio=.25,firm_peak_ratio=1.2,return_trace=False,
               roundtrip_efficiency=.9,renewable_unit_cost=5.,firm_unit_cost=90.):
    load=np.asarray(demand,dtype=float); factors=np.asarray(cf,dtype=float)
    n=len(load)
    if n==0 or len(factors)!=n or not np.isfinite(load).all() or not np.isfinite(factors).all():
        raise ValueError("Invalid source load or supply array")
    if (load<0).any() or (factors<0).any() or (factors>1).any():raise ValueError("Invalid source load / factors")
    if duration not in DURATIONS or renewable_peak_ratio<0 or battery_power_peak_ratio<0:
        raise ValueError("Unsupported assumed capacity")
    if not (0 < roundtrip_efficiency <= 1) or not np.isfinite(roundtrip_efficiency):
        raise ValueError('Invalid roundtrip efficiency')
    if (not np.isfinite(renewable_unit_cost) or not np.isfinite(firm_unit_cost)
        or renewable_unit_cost<0 or firm_unit_cost<=renewable_unit_cost):
        raise ValueError('Invalid objective coefficients')
    eta=np.sqrt(roundtrip_efficiency)
    peak=float(load.max()); available=peak*renewable_peak_ratio*factors
    power=peak*battery_power_peak_ratio if duration else 0.;capacity=power*duration
    # Variables for each hour: r=renewable direct, c=charge, d=discharge,
    # f=firm, u=unused renewable, s=SOC. Zero initial/terminal SOC.
    objective=np.tile([renewable_unit_cost,renewable_unit_cost,0.,firm_unit_cost,0.,0.],n)
    rr=[];cc=[];vv=[]; rhs=np.zeros(3*n+1); bounds=[]
    def add(eq,t,k,v):
        rr.append(eq);cc.append(6*t+k);vv.append(v)
    for t in range(n):
        for k in (0,1,4):add(3*t,t,k,1.)
        rhs[3*t]=available[t]
        for k in (0,2,3):add(3*t+1,t,k,1.)
        rhs[3*t+1]=load[t]
        add(3*t+2,t,5,1.);add(3*t+2,t,1,-eta);add(3*t+2,t,2,1./eta)
        if t:add(3*t+2,t-1,5,-1.)
        bounds.extend([(0.,min(available[t],load[t])),(0.,power),(0.,power),
                       (0.,firm_peak_ratio*peak),(0.,None),(0.,capacity)])
    add(3*n,n-1,5,1.)
    A=coo_matrix((vv,(rr,cc)),shape=(3*n+1,6*n)).tocsr()
    sol=linprog(objective,A_eq=A,b_eq=rhs,bounds=bounds,method="highs",
                options={"primal_feasibility_tolerance":1e-8,"dual_feasibility_tolerance":1e-8})
    if not sol.success:raise RuntimeError("HiGHS cyclic storage LP: "+sol.message)
    x=sol.x.reshape(n,6);resid=float(np.abs(A@sol.x-rhs).max())
    if resid>1e-5 or abs(x[-1,5])>1e-5 or (x<-1e-6).any():
        raise ValueError("Cyclic SOC / primal feasibility gate failed")
    v=x.sum(axis=0)
    if not np.isclose(v[0]+v[2]+v[3],load.sum(),atol=1e-5,rtol=1e-10):
        raise ValueError("Demand mass conservation failed")
    if not np.isclose(v[0]+v[1]+v[4],available.sum(),atol=1e-5,rtol=1e-10):
        raise ValueError("Renewable availability conservation failed")
    summary={"solver":"HiGHS scipy.optimize.linprog","solver_status":"optimal",
            "source_hours":n,"demand_mwh":float(load.sum()),
            "renewable_available_mwh":float(available.sum()),
            "renewable_direct_mwh":float(v[0]),"storage_charge_input_mwh":float(v[1]),
            "storage_discharge_to_load_mwh":float(v[2]),"firm_generation_mwh":float(v[3]),
            "unused_renewable_mwh":float(v[4]),"storage_terminal_soc_mwh":float(x[-1,5]),
            "storage_max_soc_mwh":float(x[:,5].max()),"storage_power_mw":power,
            "storage_capacity_mwh":capacity,
            "objective_illustrative_variable_usd":float(sol.fun),
            "max_equality_residual_mwh":resid,"cyclic_SOC_0_to_0_verified":True}
    if not return_trace:
        return summary
    trace=pd.DataFrame(x,columns=["renewable_direct_mwh","storage_charge_input_mwh",
                                    "storage_discharge_to_load_mwh","firm_generation_mwh",
                                    "unused_renewable_mwh","soc_end_mwh"])
    trace.insert(0,"local_hour_id",np.arange(1,n+1))
    trace["demand_mwh"]=load
    trace["renewable_available_mwh"]=available
    trace["surplus_pre_dispatch_mwh"]=np.maximum(available-load,0.)
    trace["deficit_pre_dispatch_mwh"]=np.maximum(load-available,0.)
    soc_start=np.r_[0.,x[:-1,5]]
    trace["soc_start_mwh"]=soc_start
    trace["charge_at_power_limit"]=(power>0)&np.isclose(x[:,1],power,atol=1e-6,rtol=0)
    trace["discharge_at_power_limit"]=(power>0)&np.isclose(x[:,2],power,atol=1e-6,rtol=0)
    trace["soc_at_energy_limit"]=(capacity>0)&np.isclose(x[:,5],capacity,atol=1e-6,rtol=0)
    if not np.allclose(x[:,5]-soc_start,eta*x[:,1]-x[:,2]/eta,atol=1e-5,rtol=0):
        raise ValueError("Hourly storage SOC recursion failed")
    if not np.allclose(x[:,0]+x[:,1]+x[:,4],available,atol=1e-5,rtol=0):
        raise ValueError("Hourly renewable balance failed")
    if not np.allclose(x[:,0]+x[:,2]+x[:,3],load,atol=1e-5,rtol=0):
        raise ValueError("Hourly load balance failed")
    for key in ("renewable_direct_mwh","storage_charge_input_mwh",
                "storage_discharge_to_load_mwh","firm_generation_mwh","unused_renewable_mwh"):
        if not np.isclose(trace[key].sum(),summary[key],atol=1e-5,rtol=1e-10):
            raise ValueError("Hourly trace does not reconcile to original annual LP summary")
    return summary,trace

def evaluate_zones(source,year,hours=168,max_zones=2,zone_offset=0):
    keys=["year","state","reeds_zone","local_hour_id","allocated_mw"]
    if not set(keys).issubset(source.columns):raise ValueError("Missing EFS source columns")
    if source[keys].isna().any().any() or source.duplicated(keys[:-1]).any():
        raise ValueError("Invalid or duplicate EFS inputs")
    if hours<=0 or max_zones<=0 or zone_offset<0 or hours%24:raise ValueError("Require positive whole 24-ordinal cycles and nonnegative zone offset")
    scoped=source.loc[(source.year==year)&source.local_hour_id.between(1,hours)]
    if scoped.empty:raise ValueError("Missing year source")
    groups=[]
    for (state,zone),frame in scoped.groupby(["state","reeds_zone"]):
        f=frame.sort_values("local_hour_id")
        if not np.array_equal(f.local_hour_id.to_numpy(),np.arange(1,hours+1)):
            raise ValueError("Incomplete original LocalHourID sequence")
        d=f.allocated_mw.to_numpy(dtype=float)
        if not np.isfinite(d).all() or (d<0).any():raise ValueError("Invalid original source demand")
        groups.append((float(d.sum()),str(state),str(zone),d))
    groups.sort(key=lambda row:(-row[0],row[1],row[2]))
    source_zone_count=len(groups)
    groups=groups[zone_offset:zone_offset+max_zones]
    if not groups:raise ValueError('Selected source zone batch is empty')
    rows=[]
    for _,state,zone,load in groups:
        for shape in SHAPES:
            cf=shape_cf(np.arange(1,hours+1),shape)
            if abs(float(cf.mean())-.5)>1e-12:raise ValueError("Unequal synthetic supply mean")
            for duration in DURATIONS:
                opt=solve_zone(load,cf,duration)
                greedy=dispatch_zone(load,cf,duration)
                comparable=abs(greedy["storage_terminal_soc_mwh"])<1e-6
                greedy_cost=5*(greedy["renewable_direct_mwh"]+greedy["storage_charge_mwh"])+90*greedy["firm_generation_mwh"]
                if comparable and opt["objective_illustrative_variable_usd"]>greedy_cost+.01:
                    raise ValueError("Optimal LP exceeded a feasible cyclic greedy dispatch")
                rows.append({"planning_year":year,"state":state,"reeds_zone":zone,
                             "synthetic_supply_shape":shape,"battery_duration_h":duration,**opt,
                             "greedy_firm_generation_mwh":greedy["firm_generation_mwh"],
                             "greedy_unused_renewable_mwh":greedy["unused_renewable_mwh"],
                             "greedy_terminal_soc_mwh":greedy["storage_terminal_soc_mwh"],
                             "greedy_illustrative_cost_usd":greedy_cost,
                             "cyclic_lp_vs_greedy_cost_directly_comparable":bool(comparable),
                             "cyclic_lp_cost_minus_greedy_usd":float(opt["objective_illustrative_variable_usd"]-greedy_cost) if comparable else None})
    metadata={"status":"CYCLIC_HIGHS_ILLUSTRATIVE_ORDINAL_PILOT","planning_year":year,
              "source_ordinal_hours_per_zone":hours,
              "zone_selection":"source demand MWh descending with deterministic state/zone ties",
              "zone_offset":zone_offset,"source_total_zone_count":source_zone_count,
              "zones_tested":[{"state":s,"reeds_zone":z} for _,s,z,_ in groups],
              "hypothetical_renewable_shapes":list(SHAPES),"battery_durations_h":list(DURATIONS),
              "battery_initial_and_terminal_soc_mwh":0.,
              "greedy_comparison_requires_matching_terminal_soc":True,
              "physical_UTC_verified":False,"renewable_profiles_empirical":False,
              "real_Western_network_OPF_admitted":False}
    return rows,metadata

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zonal",type=Path,required=True)
    p.add_argument("--year",type=int,required=True,choices=(2030,2040,2050))
    p.add_argument("--hours",type=int,default=168)
    p.add_argument("--max-zones",type=int,default=2)
    p.add_argument("--zone-offset",type=int,default=0)
    p.add_argument("--out-csv",type=Path,required=True)
    p.add_argument("--out-json",type=Path,required=True)
    a=p.parse_args()
    rows,meta=evaluate_zones(pd.read_csv(a.zonal,compression="infer"),a.year,a.hours,a.max_zones,a.zone_offset)
    for path in (a.out_csv,a.out_json):path.parent.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(rows).to_csv(a.out_csv,index=False)
    a.out_json.write_text(json.dumps(meta,indent=2)+"\n")
    print(json.dumps({"cases":len(rows),**meta},indent=2))
    for r in rows:
        print(f"CYCLIC_LP_RESULT year={r['planning_year']} zone={r['reeds_zone']} shape={r['synthetic_supply_shape']} "
              f"duration={r['battery_duration_h']} firm_MWh={r['firm_generation_mwh']:.5f} "
              f"unused_MWh={r['unused_renewable_mwh']:.5f} terminal_SOC_MWh={r['storage_terminal_soc_mwh']:.8f} "
              f"greedy_terminal_SOC_MWh={r['greedy_terminal_soc_mwh']:.5f} "
              f"cost_comparable={r['cyclic_lp_vs_greedy_cost_directly_comparable']}")
if __name__=="__main__":main()
