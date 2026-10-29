"""Transparent forward capacity-expansion sensitivity built on official EIA-860 BA capacity.

Four INDEPENDENT planning-year linear optimizations, not a coupled PyPSA
multi-investment-period model. Demand growth, new-build costs and resource
availability are assumptions; observed EIA-930 load shape provides baseline.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd
from .ba_historical_dispatch import ba_capacities, SOLVABLE
from .eia930_west import fetch_eia_demand, representative_hours
from .solar_availability import solar_daylight_profile
from .wind_availability import wind_sensitivity_profile

PERIODS=(2025,2030,2035,2040)
NEW_BUILD={"gas":(90000,65,1.0,0.4),"wind":(120000,2,0.35,0.0),
           "solar":(80000,2,0.26,0.0)}
SCENARIOS={
    "reference":{"growth":0.012,"co2_cap_fraction":None},
    "high_electrification":{"growth":0.025,"co2_cap_fraction":None},
    "carbon_cap_50pct":{"growth":0.012,"co2_cap_fraction":0.5},
}

def prepare(period, scenario, caps, observed):
    """Build one annual planning LP; each of 288 representative hours weighted by days."""
    import pypsa
    opts=SCENARIOS[scenario]
    n=pypsa.Network()
    reps={}
    for ba,frame in observed.groupby("respondent"):
        reps[ba]=representative_hours(frame,2024)
    bas=sorted(reps)
    base=reps[bas[0]]
    n.set_snapshots(pd.DatetimeIndex(base.snapshot))
    n.snapshot_weightings.loc[:,["objective","generators","stores"]]=base.weight_h.to_numpy()[:,None]
    for carrier in ("gas","coal","nuclear","hydro","wind","solar"):
        n.add("Carrier",carrier,co2_emissions=NEW_BUILD.get(carrier,(0,0,0,0))[3])
    n.carriers.loc["coal","co2_emissions"]=0.9
    pv = solar_daylight_profile(n.snapshots)
    wind = wind_sensitivity_profile(n.snapshots, base.weight_h.to_numpy())
    for ba in bas:
        n.add("Bus",ba)
        load=reps[ba].value.to_numpy() * ((1+opts["growth"])**(period-2024))
        n.add("Load",f"{ba}_load",bus=ba,p_set=load)
        for (b,tech),mw in caps.items():
            if b!=ba:continue
            cost, avail=SOLVABLE[tech]
            n.add("Generator",f"{ba}_{tech}_existing",bus=ba,carrier=tech,
                  p_nom=float(mw),marginal_cost=cost,p_max_pu=pv if tech=="solar" else wind if tech=="wind" else avail)
        for tech,(capital,marginal,avail,_) in NEW_BUILD.items():
            n.add("Generator",f"{ba}_{tech}_new",bus=ba,carrier=tech,
                  p_nom_extendable=True,capital_cost=capital,marginal_cost=marginal,
                  p_max_pu=pv if tech=="solar" else avail)
        n.add("Generator",f"{ba}_unserved",bus=ba,p_nom=1e7,marginal_cost=10000)
    return n,base

def annual_emissions_tco2(network, weights):
    """Operational emissions from solved generator dispatch, assuming carrier factors."""
    p = network.generators_t.p
    factor = network.generators.carrier.map(network.carriers.co2_emissions).fillna(0.0)
    return float((p.mul(factor, axis=1).sum(axis=1).to_numpy() * weights).sum())


def run(output,year_baseline=2024,bas=("CISO","BPAT")):
    output.mkdir(parents=True,exist_ok=True)
    caps,_=ba_capacities(year_baseline,list(bas))
    observed=fetch_eia_demand(year_baseline,list(bas))
    rows=[]
    dispatch_rows=[]
    reference_emissions={}
    # Solve reference first so each CO2 budget is defined by the same-year
    # unconstrained, model-based baseline rather than an invented historical value.
    for scenario in SCENARIOS:
        for year in PERIODS:
            n,reps=prepare(year,scenario,caps,observed)
            cap_fraction=SCENARIOS[scenario]["co2_cap_fraction"]
            cap_tco2=None
            if cap_fraction is not None:
                baseline=reference_emissions.get(year)
                if baseline is None:
                    raise RuntimeError(f"Missing unconstrained reference for {year}")
                cap_tco2=baseline*cap_fraction
                n.add("GlobalConstraint", "operational_co2_budget",
                      type="primary_energy", carrier_attribute="co2_emissions",
                      sense="<=", constant=cap_tco2)
            status,termination=n.optimize(solver_name="highs")
            if (status,termination)!=("ok","optimal"):
                raise RuntimeError(f"Optimization failure {scenario}/{year}: {status}, {termination}")
            new=n.generators.loc[n.generators.p_nom_extendable,"p_nom_opt"]
            load_mwh=float((n.loads_t.p_set.sum(axis=1).to_numpy()*reps.weight_h).sum())
            unserved=sum(float((n.generators_t.p[k].to_numpy()*reps.weight_h).sum()) for k in n.generators.index if k.endswith("_unserved"))
            annual_co2 = annual_emissions_tco2(n, reps.weight_h.to_numpy())
            if scenario=="reference":
                reference_emissions[year]=annual_co2
            if cap_tco2 is not None and annual_co2>cap_tco2+max(0.001,abs(cap_tco2)*1e-5):
                raise RuntimeError(f"CO2 constraint violated for {scenario}/{year}: {annual_co2} > {cap_tco2}")
            for generator, series in n.generators_t.p.items():
                dispatch_rows.append({
                    "scenario":scenario,"planning_year":year,
                    "generator":generator,"carrier":n.generators.loc[generator,"carrier"],
                    "annual_dispatch_mwh":float((series.to_numpy()*reps.weight_h.to_numpy()).sum())
                })
            rows.append({"scenario":scenario,"planning_year":year,
                "operational_emissions_tco2_assumed":annual_co2,
                "co2_cap_tco2":cap_tco2,
                "co2_budget_binding_ratio":annual_co2/cap_tco2 if cap_tco2 else None,
                "observed_baseline":year_baseline,"assumed_growth":SCENARIOS[scenario]["growth"],
                "load_mwh":load_mwh,"unserved_mwh":unserved,"objective_assumed_usd":float(n.objective),
                **{f"new_{tech}_mw":float(new.filter(like="_"+tech+"_new").sum()) for tech in NEW_BUILD},
                "solver_status":termination})
    pd.DataFrame(rows).to_csv(output/"scenario_summary.csv",index=False)
    pd.DataFrame(dispatch_rows).to_csv(output/"generator_annual_dispatch.csv",index=False)
    (output/"assumptions.json").write_text(json.dumps({
       "source_eia860_year":year_baseline,"source_eia930_year":year_baseline,"planning_years":PERIODS,
       "scenarios":SCENARIOS,"new_build_parameters_capital_usd_per_mw_year_marginal_usd_per_mwh_availability_and_tco2_per_mwh":NEW_BUILD,
       "solar_profile":"Illustrative local-time daylight envelope, NOT observed solar irradiance; zero at local night, approximately 0.26 mean.",
       "wind_profile":"Illustrative weighted seasonal/diurnal wind sensitivity with 0.35 annual mean; NOT measured wind resource.",
       "warning":"Each year solved independently, no chronological transmission or storage, 50% carbon cap is enforced relative to each planning year’s unconstrained reference model emissions; this is NOT an empirically calibrated carbon budget. Emissions are operational model estimates using assumed factors, not observed EIA generation or emissions. Not a forecast or integrated multi-period investment solution."
    },indent=2))
    return rows

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,default=Path("outputs/planning_sensitivity"))
    a=p.parse_args()
    print(json.dumps(run(a.output),indent=2))
if __name__=="__main__":main()
