"""Reproducible source-ordinal run lengths and storage utilization from archived LP traces."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

KEY=["planning_year","state","reeds_zone","synthetic_supply_shape","battery_duration_h"]
SHAPES={"flat_50pct","ordinal24_wave_A","ordinal24_wave_B"}
DURATIONS={0,4,8}

def run_lengths(mask):
    a=np.asarray(mask,dtype=np.int8)
    changes=np.diff(np.r_[0,a,0])
    return np.flatnonzero(changes==-1)-np.flatnonzero(changes==1)

def summarize(hourly,original):
    if len(hourly)!=9*8760 or len(original)!=9:raise ValueError("Expected nine full-year cases")
    if hourly.duplicated(KEY+["local_hour_id"]).any():raise ValueError("Duplicate hour")
    if set(hourly.synthetic_supply_shape)!=SHAPES or set(hourly.battery_duration_h)!=DURATIONS:
        raise ValueError("Missing supply shape or duration")
    if hourly[KEY[:3]].drop_duplicates().shape[0]!=1:raise ValueError("Not a unique zone/year")
    rows=[]
    for k,g in hourly.groupby(KEY):
        g=g.sort_values("local_hour_id")
        if not np.array_equal(g.local_hour_id,np.arange(1,8761)):
            raise ValueError("Missing or misordered source hours")
        x=original.copy()
        for name,val in zip(KEY,k):x=x[x[name]==val]
        if len(x)!=1:raise ValueError("Missing original verified case")
        x=x.iloc[0]
        cols=["renewable_direct_mwh","storage_charge_input_mwh","storage_discharge_to_load_mwh",
              "unused_renewable_mwh","firm_generation_mwh","demand_mwh","renewable_available_mwh",
              "soc_start_mwh","soc_end_mwh","surplus_pre_dispatch_mwh","deficit_pre_dispatch_mwh"]
        if not np.isfinite(g[cols].to_numpy(dtype=float)).all():raise ValueError("Nonfinite trace")
        if not np.allclose(g.renewable_direct_mwh+g.storage_charge_input_mwh+g.unused_renewable_mwh,
                           g.renewable_available_mwh,rtol=0,atol=1e-5):raise ValueError("Resource mismatch")
        if not np.allclose(g.renewable_direct_mwh+g.storage_discharge_to_load_mwh+g.firm_generation_mwh,
                           g.demand_mwh,rtol=0,atol=1e-5):raise ValueError("Demand mismatch")
        if not np.allclose(g.soc_end_mwh-g.soc_start_mwh,
                           np.sqrt(.9)*g.storage_charge_input_mwh-
                           g.storage_discharge_to_load_mwh/np.sqrt(.9),rtol=0,atol=1e-5):
            raise ValueError("SOC mismatch")
        if abs(float(g.soc_end_mwh.iloc[-1]))>1e-5:raise ValueError("Non-cyclic storage")
        for column,actual in {
            "charging_hours":int((g.storage_charge_input_mwh>1e-7).sum()),
            "discharging_hours":int((g.storage_discharge_to_load_mwh>1e-7).sum()),
            "soc_at_capacity_hours":int(g.soc_at_energy_limit.sum()),
            "charge_power_limit_hours":int(g.charge_at_power_limit.sum()),
            "discharge_power_limit_hours":int(g.discharge_at_power_limit.sum())
        }.items():
            if actual!=int(x[column]):raise ValueError("Original annual activity count mismatch")
        sur=run_lengths(g.surplus_pre_dispatch_mwh>1e-7)
        deficit=run_lengths(g.deficit_pre_dispatch_mwh>1e-7)
        cap=float(x.battery_capacity_mwh)
        discharged=float(g.storage_discharge_to_load_mwh.sum())
        row=dict(zip(KEY,k))
        for label,v in (("surplus",sur),("deficit",deficit)):
            row[label+"_run_count"]=len(v)
            row[label+"_run_mean_hours"]=float(v.mean()) if len(v) else 0.
            row[label+"_run_p90_hours"]=float(np.percentile(v,90)) if len(v) else 0.
            row[label+"_run_max_hours"]=int(v.max()) if len(v) else 0
        row.update({"charge_gwh":float(g.storage_charge_input_mwh.sum())/1000,
                    "discharge_gwh":discharged/1000,
                    "mean_soc_fraction":float(g.soc_end_mwh.mean())/cap if cap>0 else 0.,
                    "soc_nonempty_hours":int((g.soc_end_mwh>1e-7).sum()),
                    "soc_above_half_capacity_hours":int((g.soc_end_mwh>=cap*.5-1e-7).sum()) if cap>0 else 0,
                    "equivalent_full_cycles":discharged/(cap*np.sqrt(.9)) if cap>0 else 0,
                    "annual_variable_objective_usd":float(x.annual_toy_cost_usd)})
        rows.append(row)
    out=pd.DataFrame(rows).sort_values(KEY).reset_index(drop=True)
    for shape,g in out.groupby("synthetic_supply_shape"):
        for col in ("surplus_run_count","surplus_run_mean_hours","deficit_run_count","deficit_run_mean_hours"):
            if not np.allclose(g[col],g[col].iloc[0]):raise ValueError("Battery changes pre-dispatch opportunity")
    return out

def main():
    p=argparse.ArgumentParser()
    for n in ("hourly","original","out_dir"):p.add_argument("--"+n.replace("_","-"),type=Path,required=True)
    a=p.parse_args()
    frame=summarize(pd.read_csv(a.hourly,compression="infer"),pd.read_csv(a.original))
    a.out_dir.mkdir(parents=True,exist_ok=True)
    frame.to_csv(a.out_dir/"paper_s_p28_temporal_mechanism.csv",index=False,float_format="%.12g")
    report={"status":"PAPER_S_HOURLY_TEMPORAL_DIAGNOSTIC_PASS","cases":9,
            "hourly_rows":78840,"hour_axis":"source LocalHourID ordinal, not certified UTC",
            "real_resource_data":False,"western_opf":False,
            "interpretation":"single-zone synthetic supply and solver-dependent dispatch"}
    (a.out_dir/"paper_s_p28_temporal_mechanism_manifest.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
