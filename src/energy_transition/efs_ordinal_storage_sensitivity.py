"""Ordinal-only EFS renewable surplus → illustrative battery energy-shifting screen.

Real input: staged EFS/LAF demand for 7 states, 20 zones, 3 years.
All renewable supply and storage are hypothetical. No UTC, weather data,
actual generator POI, transmission, investment or physical Western OPF.
Storage starts empty; no invented energy at the horizon boundary.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

YEARS=(2030,2040,2050)
HOURS=8760
SHAPES=("flat_50pct","ordinal24_wave_A","ordinal24_wave_B")
DURATIONS=(0,4,8)
NAMEPLATE_TO_PEAK=0.9
BATTERY_POWER_TO_PEAK=0.25
ROUND_TRIP_EFFICIENCY=0.9
RENEWABLE_COST=5.0
FIRM_COST=90.0

def shape_cf(hour_ids, shape):
    h=np.asarray(hour_ids,dtype=float)
    if shape=="flat_50pct":
        return np.full(h.shape,0.5)
    if shape=="ordinal24_wave_A":
        return 0.5+0.35*np.cos(2*np.pi*(h-1)/24)
    if shape=="ordinal24_wave_B":
        return 0.5-0.35*np.cos(2*np.pi*(h-1)/24)
    raise ValueError("Unknown synthetic supply shape")


def dispatch_zone(demand, cf, duration, *, nameplate_ratio=NAMEPLATE_TO_PEAK,
                  storage_power_ratio=BATTERY_POWER_TO_PEAK,
                  rte=ROUND_TRIP_EFFICIENCY):
    demand=np.asarray(demand,dtype=float)
    cf=np.asarray(cf,dtype=float)
    if len(demand)==0 or len(demand)!=len(cf):
        raise ValueError("Missing or inconsistent source hours")
    if not (np.isfinite(demand).all() and np.isfinite(cf).all()) or (demand<0).any() or (cf<0).any() or (cf>1).any():
        raise ValueError("Invalid source load or renewable availability")
    if duration<0 or storage_power_ratio<0 or not 0<rte<=1 or nameplate_ratio<0:
        raise ValueError("Invalid storage or renewable assumptions")
    peak=float(demand.max())
    available=peak*nameplate_ratio*cf
    p_storage=storage_power_ratio*peak if duration else 0.
    capacity=p_storage*duration
    eff=math.sqrt(rte)
    soc=0.
    renewable_direct=0.
    charged=0.
    discharged=0.
    curtailed=0.
    firm=0.
    max_soc=0.
    for load, avail in zip(demand,available):
        direct=min(load,avail)
        renewable_direct+=direct
        excess=avail-direct
        deficit=load-direct
        if excess>0 and capacity>0:
            # Charge drawn from current unused renewable output; SOC stores after conversion.
            charge=min(excess,p_storage,(capacity-soc)/eff)
            soc+=charge*eff
            charged+=charge
            curtailed+=excess-charge
        elif deficit>0 and soc>0 and capacity>0:
            delivered=min(deficit,p_storage,soc*eff)
            soc-=delivered/eff
            discharged+=delivered
            firm+=deficit-delivered
        else:
            curtailed+=excess
            firm+=deficit
        if soc<-1e-7 or soc>capacity+1e-7:
            raise ValueError("Battery state bound failure")
        soc=max(0.,min(capacity,soc))
        max_soc=max(max_soc,soc)
    renewable=float(renewable_direct)
    source_demand=float(demand.sum())
    renewable_supply=float(available.sum())
    # Stored terminal energy cannot be counted as supplied/curtailed or secretly discarded.
    if not np.isclose(renewable+discharged+firm,source_demand,atol=0.01,rtol=1e-11):
        raise ValueError("Demand mass balance failed")
    if not np.isclose(renewable+charged+curtailed,renewable_supply,atol=0.01,rtol=1e-11):
        raise ValueError("Renewable availability mass balance failed")
    if not np.isclose(charged*eff-discharged/eff,soc,atol=0.01,rtol=1e-11):
        raise ValueError("Battery SOC energy balance failed")
    return {
        "demand_mwh":source_demand,"available_renewable_mwh":renewable_supply,
        "renewable_direct_mwh":renewable,"storage_charge_mwh":charged,
        "storage_discharge_to_load_mwh":discharged,
        "firm_generation_mwh":firm,"unused_renewable_mwh":curtailed,
        "storage_terminal_soc_mwh":soc,"storage_peak_soc_mwh":max_soc,
        "storage_power_mw":p_storage,"storage_energy_capacity_mwh":capacity,
    }


def evaluate(data, years=YEARS, hours=HOURS, shapes=SHAPES, durations=DURATIONS):
    expected={"year","state","reeds_zone","local_hour_id","allocated_mw"}
    if not expected.issubset(data):
        raise ValueError("Missing source EFS columns")
    source=data.copy()
    if source[list(expected)].isna().any().any():
        raise ValueError("Missing source EFS values")
    if source.duplicated(["year","state","reeds_zone","local_hour_id"]).any():
        raise ValueError("Duplicate source zone/hour")
    if set(source.year)!=set(years):
        raise ValueError("Planning year population mismatch")
    demand_values=pd.to_numeric(source.allocated_mw,errors="coerce").to_numpy(dtype=float)
    if not np.isfinite(demand_values).all() or (demand_values<0).any():
        raise ValueError("Nonfinite/negative EFS demand")
    rows=[]
    for year in years:
        groups=[]
        for (state,zone),frame in source[source.year==year].groupby(["state","reeds_zone"]):
            f=frame.sort_values("local_hour_id")
            ids=f.local_hour_id.to_numpy()
            if not np.array_equal(ids,np.arange(1,hours+1)):
                raise ValueError(f"Missing or invalid hourly source keys {year}/{state}/{zone}")
            groups.append(f.allocated_mw.to_numpy(dtype=float))
        if not groups:
            raise ValueError(f"No source zones in year {year}")
        hours_index=np.arange(1,hours+1)
        for shape in shapes:
            factors=shape_cf(hours_index,shape)
            if abs(float(factors.mean())-.5)>1e-12:
                raise ValueError("Unequal annual mean renewable availability")
            for duration in durations:
                totals={}
                for demand in groups:
                    r=dispatch_zone(demand,factors,duration)
                    for key,value in r.items():
                        totals[key]=totals.get(key,0.)+value
                if totals["firm_generation_mwh"]<0 or totals["unused_renewable_mwh"]<0:
                    raise ValueError("Negative physical accounting outputs")
                load=totals["demand_mwh"]
                rows.append({
                    "planning_year":int(year),"synthetic_supply_shape":shape,
                    "battery_duration_hours":int(duration),
                    "zone_count":int(len(groups)),"ordinal_hours_per_zone":int(hours),
                    "hypothetical_renewable_nameplate_to_zone_peak":NAMEPLATE_TO_PEAK,
                    "hypothetical_battery_power_to_zone_peak":BATTERY_POWER_TO_PEAK if duration else 0.,
                    "hypothetical_round_trip_efficiency":ROUND_TRIP_EFFICIENCY,
                    **totals,
                    "renewable_supply_to_load_mwh":totals["renewable_direct_mwh"]+totals["storage_discharge_to_load_mwh"],
                    "renewable_share_to_load":(totals["renewable_direct_mwh"]+totals["storage_discharge_to_load_mwh"])/load if load>0 else 0.,
                    "illustrative_variable_cost_usd":RENEWABLE_COST*(
                        totals["renewable_direct_mwh"]+totals["storage_charge_mwh"]
                    )+FIRM_COST*totals["firm_generation_mwh"],
                })
    return rows,{
        "status":"ILLUSTRATIVE_EFS_ORDINAL_BATTERY_SURPLUS_SHIFTING",
        "planning_years":list(years),"ordinal_hours_per_zone":int(hours),
        "synthetic_supply_profiles":list(shapes),"assumed_battery_durations_hours":list(durations),
        "battery_initial_soc_mwh":0.,
        "battery_terminal_soc_is_recorded_not_assumed_zero":True,
        "assumed_battery_power_per_zone_peak":BATTERY_POWER_TO_PEAK,
        "assumed_battery_roundtrip_efficiency":ROUND_TRIP_EFFICIENCY,
        "assumed_renewable_nameplate_per_zone_peak":NAMEPLATE_TO_PEAK,
        "assumed_renewable_mean_capacity_factor":0.5,
        "battery_operation":"greedy charge only from hypothetical renewable surplus, discharge only to offset firm shortage",
        "battery_losses_included":True,
        "battery_capex_and_degradation_included":False,
        "actual_renewable_data_used":False,
        "source_hour_physical_utc_verified":False,
        "interzonal_power_transfers_modeled":False,
        "real_generator_bus_admitted":False,
        "Western_OPF_admitted":False,
        "note":"Source EFS load is real, but synthetic ordinal shapes and storage do not represent actual solar, wind, daily timing, equipment or grid curtailment."
    }


def main():
    p=argparse.ArgumentParser()
    for name in ("zonal","out-csv","out-json"):
        p.add_argument("--"+name,required=True,type=Path)
    args=p.parse_args()
    rows,meta=evaluate(pd.read_csv(args.zonal,compression="infer"))
    meta["source_csv_sha256"]=hashlib.sha256(args.zonal.read_bytes()).hexdigest()
    for path in (args.out_csv,args.out_json):
        path.parent.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(rows).to_csv(args.out_csv,index=False)
    args.out_json.write_text(json.dumps(meta,indent=2)+"\n")
    print(json.dumps({"scenario_count":len(rows),**meta},indent=2))
if __name__=="__main__":
    main()
