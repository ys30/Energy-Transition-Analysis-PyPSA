"""Ordinal-hour supply-shape sensitivity on verified EFS zone demand.

These are synthetic 24-ordinal periodicity probes, NOT observed wind, solar,
UTC time, real diurnal cycles, network dispatch, or future generation forecasts.
Every profile is constrained to equal annual available MWh for each zone.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

YEARS=(2030,2040,2050)
HOURS=8760
MULTIPLIERS=(0.3,0.6,0.9)
PROFILES=("flat_50pct","ordinal24_wave_A","ordinal24_wave_B")
RENEWABLE_COST=5.0
FIRM_COST=90.0
FIRM_PEAK_MULTIPLIER=1.2


def profile(hour_ids: np.ndarray, kind: str) -> np.ndarray:
    h=np.asarray(hour_ids, dtype=float)
    if not np.isfinite(h).all():
        raise ValueError("Invalid hour IDs for profile")
    if kind=="flat_50pct":
        cf=np.full(len(h),0.5)
    elif kind=="ordinal24_wave_A":
        cf=0.5+0.35*np.cos(2*np.pi*(h-1)/24)
    elif kind=="ordinal24_wave_B":
        cf=0.5-0.35*np.cos(2*np.pi*(h-1)/24)
    else:
        raise ValueError("Unknown synthetic profile")
    if np.any(cf<0) or np.any(cf>1):
        raise ValueError("Invalid synthetic capacity-factor bounds")
    return cf


def evaluate(source: pd.DataFrame, years=YEARS, hours=HOURS,
             multipliers=MULTIPLIERS, profiles=PROFILES):
    req={"year","state","reeds_zone","local_hour_id","allocated_mw"}
    if not req.issubset(source.columns):
        raise ValueError("Missing EFS zonal source columns")
    d=source.copy()
    if d[list(req)].isna().any().any():
        raise ValueError("Missing EFS zonal values")
    if d.duplicated(["year","state","reeds_zone","local_hour_id"]).any():
        raise ValueError("Duplicate source zone-hour")
    if set(d.year)!=set(years):
        raise ValueError("Year population mismatch")
    v=pd.to_numeric(d.allocated_mw,errors="coerce").to_numpy(dtype=float)
    if not np.isfinite(v).all() or (v<0).any():
        raise ValueError("Invalid EFS source MW")
    annual_rows=[]
    shape_rows=[]
    if len(set(profiles))!=len(profiles):
        raise ValueError("Duplicate profile scenarios")
    for year in years:
        subset=d[d.year==year]
        groups=[]
        for (state,zone),group in subset.groupby(["state","reeds_zone"]):
            group=group.sort_values("local_hour_id")
            ids=group.local_hour_id.to_numpy()
            if (len(ids)!=hours or
                not np.array_equal(ids,np.arange(1,hours+1))):
                raise ValueError(f"Incomplete ordinal hours: {year}/{state}/{zone}")
            groups.append((str(state),str(zone),group.allocated_mw.to_numpy(dtype=float)))
        if not groups:
            raise ValueError("Missing EFS demand zones")
        demand_mwh=sum(float(x.sum()) for _,_,x in groups)
        hours_index=np.arange(1,hours+1)
        factors={p:profile(hours_index,p) for p in profiles}
        for p,f in factors.items():
            if abs(float(f.mean())-0.5)>1e-12:
                raise ValueError(f"{p}: not equal mean 50% availability")
            shape_rows.append({
                "planning_year":int(year),
                "synthetic_supply_shape":p,
                "mean_assumed_capacity_factor":float(f.mean()),
                "minimum_assumed_capacity_factor":float(f.min()),
                "maximum_assumed_capacity_factor":float(f.max()),
                "first_ordinal_capacity_factor":float(f[0]),
                "ordinal_12_capacity_factor":float(f[min(11,hours-1)]),
            })
        for mult in multipliers:
            if not 0<=mult<=1:
                raise ValueError("Unsupported renewable capacity scenario")
            identical_available=None
            for p,f in factors.items():
                delivered=curtailed=firm=available=cost=0.0
                for _,_,demand in groups:
                    peak=float(demand.max())
                    renew_cap=peak*mult
                    avail=renew_cap*f
                    gen=np.minimum(avail,demand)
                    backup=demand-gen
                    if np.any(backup>peak*FIRM_PEAK_MULTIPLIER+1e-9):
                        raise ValueError("Firm capacity insufficient")
                    delivered+=float(gen.sum())
                    curtailed+=float((avail-gen).sum())
                    firm+=float(backup.sum())
                    available+=float(avail.sum())
                    cost+=float(gen.sum()*RENEWABLE_COST+backup.sum()*FIRM_COST)
                if not np.isclose(delivered+firm,demand_mwh,atol=0.01,rtol=1e-11):
                    raise ValueError("Supply conservation failed")
                if not np.isclose(delivered+curtailed,available,atol=0.01,rtol=1e-11):
                    raise ValueError("Renewable availability conservation failed")
                if identical_available is None:
                    identical_available=available
                elif not np.isclose(available,identical_available,atol=0.01,rtol=1e-11):
                    raise ValueError("Profiles change annual available supply")
                annual_rows.append({
                    "planning_year":int(year),"renewable_peak_ratio":float(mult),
                    "synthetic_supply_shape":p,
                    "zonal_systems":len(groups),"ordinal_hours_per_zone":hours,
                    "source_demand_mwh":demand_mwh,
                    "available_renewable_mwh":available,
                    "delivered_renewable_mwh":delivered,
                    "model_unused_renewable_mwh":curtailed,
                    "assumed_firm_generation_mwh":firm,
                    "illustrative_renewable_share":delivered/demand_mwh if demand_mwh>0 else 0.,
                    "illustrative_variable_cost_usd":cost,
                })
    result={
        "status":"ILLUSTRATIVE_EQUAL_ENERGY_SUPPLY_SHAPE_SENSITIVITY",
        "years":list(years),
        "ordinal_hours_per_zone":hours,
        "renewable_nameplate_to_zonal_demand_peak_ratios":list(multipliers),
        "synthetic_supply_shapes":list(profiles),
        "source_demand_is_archived_efs":True,
        "renewable_profiles_are_observed":False,
        "source_LocalHourID_is_physical_UTC_verified":False,
        "real_plant_capacity_and_cost_verified":False,
        "interzonal_transfer_modeled":False,
        "battery_storage_modeled":False,
        "physical_Western_OPF_admitted":False,
        "method":"Synthetic flat 0.5 vs ordinal-periodic 0.5 ± 0.35 cos(2π(h-1)/24); equal annual mean 0.5; zone-local firm backup at 1.2 times peak; costs renewable $5/MWh and backup $90/MWh.",
        "note":"Ordinal-24 oscillation is a mathematical probe, NOT a physical local time, daily solar shape or historical renewable generation profile."
    }
    return annual_rows,shape_rows,result


def main():
    p=argparse.ArgumentParser()
    for name in ("zonal","out-csv","out-shapes","out-json"):
        p.add_argument("--"+name,required=True,type=Path)
    a=p.parse_args()
    raw=a.zonal.read_bytes()
    data=pd.read_csv(a.zonal,compression="infer")
    rows,shapes,meta=evaluate(data)
    meta["source_zonal_sha256"]=hashlib.sha256(raw).hexdigest()
    for path in (a.out_csv,a.out_shapes,a.out_json):
        path.parent.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(rows).to_csv(a.out_csv,index=False)
    pd.DataFrame(shapes).to_csv(a.out_shapes,index=False)
    a.out_json.write_text(json.dumps(meta,indent=2)+"\n")
    print(json.dumps({"scenario_rows":len(rows),"shape_rows":len(shapes),**meta},indent=2))


if __name__=="__main__":
    main()
