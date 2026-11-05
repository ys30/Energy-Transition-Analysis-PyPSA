"""Full-8760-hour ordinal-only EFS demand + illustrative supply sensitivity.

This is a closed-form least-cost dispatch screening under *independent*
unconnected zones. Neither the renewable profile, costs, nor generators are
empirical. There is no UTC assumption, storage, transmission or actual OPF.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

YEARS=(2030,2040,2050)
HOURS=8760
RENEWABLE_MULTIPLIERS=(0.3,0.6,0.9)
CF_ASSUMPTION=0.5
RENEWABLE_COST=5.0
FIRM_COST=90.0
FIRM_PEAK_MULTIPLIER=1.2

def evaluate(data, *, years=YEARS, hours=HOURS, multipliers=RENEWABLE_MULTIPLIERS):
    required={"year","state","reeds_zone","local_hour_id","allocated_mw"}
    if not required.issubset(data.columns):
        raise ValueError("Missing source zonal demand columns")
    frame=data.copy()
    if frame[["year","state","reeds_zone","local_hour_id","allocated_mw"]].isna().any().any():
        raise ValueError("Missing source data")
    if frame.duplicated(["year","state","reeds_zone","local_hour_id"]).any():
        raise ValueError("Duplicate zone-hour")
    if set(frame.year)!=set(years):
        raise ValueError("Year coverage mismatch")
    vals=frame.allocated_mw.to_numpy(dtype=float)
    if not np.isfinite(vals).all() or (vals<0).any():
        raise ValueError("Invalid source MW")
    rows=[]
    for year in years:
        subset=frame.loc[frame.year==year]
        groups=list(subset.groupby(["state","reeds_zone"]))
        if not groups:
            raise ValueError("No source zones")
        base_demand=0.0
        for (_, _), g in groups:
            ordinals=g.local_hour_id.to_numpy()
            if len(g)!=hours or not np.array_equal(np.sort(ordinals),np.arange(1,hours+1)):
                raise ValueError("Missing or invalid local-hour sequence")
            base_demand+=float(g.allocated_mw.sum())
        for mult in multipliers:
            if not (0 <= mult <= 1):
                raise ValueError("Unsupported renewable nameplate scenario")
            renewable=firm=available=curtailed=cost=0.0
            for (_, _),g in groups:
                demand=g.allocated_mw.to_numpy(dtype=float)
                peak=float(demand.max())
                renewable_nameplate=mult*peak
                avail=np.full(len(demand),renewable_nameplate*CF_ASSUMPTION)
                renewable_dispatch=np.minimum(demand,avail)
                firm_dispatch=demand-renewable_dispatch
                if np.any(firm_dispatch>peak*FIRM_PEAK_MULTIPLIER+1e-9):
                    raise ValueError("Firm capacity infeasible")
                renewable+=float(renewable_dispatch.sum())
                firm+=float(firm_dispatch.sum())
                available+=float(avail.sum())
                curtailed+=float((avail-renewable_dispatch).sum())
                cost+=float(renewable_dispatch.sum()*RENEWABLE_COST+firm_dispatch.sum()*FIRM_COST)
            if not np.isclose(renewable+firm,base_demand,rtol=1e-11,atol=0.01):
                raise ValueError("Supply demand accounting mismatch")
            if not np.isclose(renewable+curtailed,available,rtol=1e-11,atol=0.01):
                raise ValueError("Renewable availability accounting mismatch")
            rows.append({
                "planning_year":int(year),
                "renewable_nameplate_to_local_zone_peak_ratio":float(mult),
                "source_ordinal_hours_per_zone":int(hours),
                "zonal_systems":int(len(groups)),
                "real_efs_pilot_demand_mwh":base_demand,
                "illustrative_renewable_available_mwh":available,
                "illustrative_renewable_dispatch_mwh":renewable,
                "illustrative_renewable_curtailment_mwh":curtailed,
                "illustrative_firm_dispatch_mwh":firm,
                "illustrative_renewable_energy_share":renewable/base_demand if base_demand else 0.,
                "illustrative_variable_cost_usd":cost,
                "unserved_mwh_under_assumed_firm_capacity":0.0,
            })
    return rows, {
        "status":"ILLUSTRATIVE_ORDINAL_ONLY_FULL_YEAR_SENSITIVITY",
        "planning_years":list(years),
        "hours_per_zone":hours,
        "scenarios":list(multipliers),
        "assumed_constant_renewable_capacity_factor":CF_ASSUMPTION,
        "assumed_firm_capacity_per_zone_peak_multiplier":FIRM_PEAK_MULTIPLIER,
        "illustrative_costs_per_mwh":{"renewable":RENEWABLE_COST,"firm":FIRM_COST},
        "supply_profiles_and_costs_empirical":False,
        "interzonal_transmission_modeled":False,
        "real_grid_or_generator_placement_verified":False,
        "utc_weather_alignment_verified":False,
        "calendar_time_based_conclusions_allowed":False,
        "physical_western_opf_admitted":False,
        "note":"Zone-independent algebraic merit order, not a PyPSA network solve or a forecast. All demand retains local_hour_id ordinals."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zonal",type=Path,required=True)
    p.add_argument("--out-csv",type=Path,required=True)
    p.add_argument("--out-json",type=Path,required=True)
    a=p.parse_args()
    data=pd.read_csv(a.zonal,compression="infer")
    rows,report=evaluate(data)
    for dest in (a.out_csv,a.out_json):
        dest.parent.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(rows).to_csv(a.out_csv,index=False)
    a.out_json.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"rows":len(rows),**report},indent=2))
if __name__=="__main__":main()
