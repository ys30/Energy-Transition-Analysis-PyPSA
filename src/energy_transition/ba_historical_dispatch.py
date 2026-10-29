"""Historical two-BA PyPSA dispatch using observed EIA-930 load and EIA-860 capacity.

Deliberately NO transmission, storage, investment or observed renewable profiles.
Wind/solar availability and thermal costs are documented scenario assumptions.
"""
import argparse
import json
from pathlib import Path
import pandas as pd
from .eia930_west import fetch_eia_demand, representative_hours
from .eia860_capacity import read_operable_inventory, URL
from .eia860_plant_ba import extract_plant_ba
from .ba_crosswalk import join_verified_crosswalk
import urllib.request
from .eia860_technology import FUEL_TO_TECH

SOLVABLE = {"gas": (65., 1.), "coal": (40., 1.), "nuclear": (15., 1.),
            "hydro": (9., 0.45), "wind": (2., 0.35), "solar": (2., 0.26)}
# Hydro 0.45 is an assumed year-round cap, NOT observed hourly hydro availability.

def ba_capacities(year, bas):
    req=urllib.request.Request(URL.format(year=year),headers={"User-Agent":"pypsa-west-real-input-pilot/0.3"})
    with urllib.request.urlopen(req, timeout=90) as response:
        archive=response.read()
    gens=read_operable_inventory(archive,year)
    from .eia860_capacity import WESTERN_STATES
    gens=gens[gens.state.isin(WESTERN_STATES) & gens.capacity_qc.eq("valid") & gens.id_qc.eq("valid")].copy()
    plants,_=extract_plant_ba(archive)
    x=plants[plants.crosswalk_qc.eq("valid")].drop_duplicates(["plant_id","ba_code"])
    joined=join_verified_crosswalk(gens,x[["plant_id","ba_code"]])
    joined=joined[(joined.crosswalk_status=="matched") & (joined.status=="OP") & joined.ba_code.isin(bas)].copy()
    joined["tech"]=joined.fuel.map(FUEL_TO_TECH)
    if joined.empty: raise ValueError("No observed BA operating plants")
    cap=joined[joined.tech.isin(SOLVABLE)].groupby(["ba_code","tech"]).capacity_mw.sum()
    return cap,joined

def solve_year(year, demand, caps, bas, output):
    import pypsa
    output.mkdir(parents=True,exist_ok=True)
    n=pypsa.Network()
    base=None
    for ba in bas:
        rep=representative_hours(demand[demand.respondent.eq(ba)], year)
        if base is None:
            base=rep[["snapshot","weight_h"]].copy()
            n.set_snapshots(pd.DatetimeIndex(base.snapshot))
            n.snapshot_weightings.loc[:,["objective","generators","stores"]]=base.weight_h.to_numpy()[:,None]
        elif not rep.snapshot.equals(base.snapshot):
            raise ValueError("BA timestamp mismatch")
        n.add("Bus",ba)
        n.add("Load",f"load_{ba}",bus=ba,p_set=rep.value.to_numpy())
        for (zone,tech),mw in caps.items():
            if zone!=ba: continue
            cost, avail=SOLVABLE[tech]
            n.add("Generator",f"{ba}_{tech}",bus=ba,p_nom=float(mw),
                  marginal_cost=cost,p_max_pu=avail)
        n.add("Generator",f"{ba}_unserved",bus=ba,p_nom=1e7,marginal_cost=10000)
    status,condition=n.optimize(solver_name="highs")
    if (status,condition)!=("ok","optimal"):
        raise RuntimeError(f"Optimization failed: {status}/{condition}")
    p=n.generators_t.p.mul(base.weight_h.to_numpy(),axis=0).sum()
    records=[]
    for ba in bas:
        load = demand[demand.respondent.eq(ba)].value.sum()
        unserved=float(p[f"{ba}_unserved"])
        records.append({"year":year,"ba_code":ba,"observed_demand_mwh":float(load),
                        "modeled_unserved_mwh":unserved,
                        "modeled_unserved_share":unserved/float(load),
                        "actual_ba_operating_nameplate_mw_in_solvable_techs":float(sum(v for (b,t),v in caps.items() if b==ba)),
                        "solver_status":condition})
    pd.DataFrame(records).to_csv(output/"ba_metrics.csv",index=False)
    n.export_to_netcdf(output/"solved_network.nc")
    return records

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--year",type=int,default=2024)
    p.add_argument("--bas",nargs="+",default=["CISO","BPAT"])
    p.add_argument("--output",type=Path,default=Path("outputs/ba_dispatch"))
    a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=True)
    caps,joined=ba_capacities(a.year,a.bas)
    caps.rename("capacity_mw").reset_index().to_csv(a.output/"eia860_ba_input_capacity.csv",index=False)
    joined.to_csv(a.output/"eia860_generator_ba_join.csv",index=False)
    hourly=fetch_eia_demand(a.year,a.bas)
    hourly.to_csv(a.output/"eia930_hourly_load.csv",index=False)
    metrics=solve_year(a.year,hourly,caps,a.bas,a.output)
    manifest={"demand_source":"EIA-930 hourly BA load","capacity_source":URL.format(year=a.year),
              "model":"separate BA buses; NO links; fixed generators; stylized constant availability",
              "limitations":"Fuel costs and technology availability are assumptions; hydro, wind, solar and storage not physically calibrated; EIA-860 11-state selection omits some units. Deficits are not reliable adequacy estimates."}
    (a.output/"assumptions.json").write_text(json.dumps(manifest,indent=2))
    print(json.dumps(metrics,indent=2))
if __name__=="__main__":
    main()
