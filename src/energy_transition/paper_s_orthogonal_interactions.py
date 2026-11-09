"""Source-backed MW/MWh interaction audit on accepted 189 orthogonal LP cases.

For each adjacent 2x2 rectangle:
interaction = [cost reduction from more MWh at high MW]
            - [cost reduction from more MWh at low MW].
Positive: complementary benefits in the illustrative variable objective;
negative: diminishing energy benefit at higher power.
Not a dual certificate, causal effect for real grids, or investment payoff.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

POWERS=(.125,.25,.5)
ENERGIES=(.5,1.,2.)
SUPPLY=("flat_50pct","ordinal24_wave_A","ordinal24_wave_B")
MEASURES=("objective_illustrative_variable_usd","firm_generation_mwh","unused_renewable_mwh",
          "storage_discharge_to_load_mwh")

def audit(frame: pd.DataFrame) -> pd.DataFrame:
    keys=["source_shape_group","synthetic_supply_shape",
          "battery_power_peak_ratio","battery_energy_peak_hours"]
    needed=set(keys+list(MEASURES)+["state","reeds_zone","solver_status",
                                  "source_hours","storage_terminal_soc_mwh"])
    if not needed.issubset(frame):
        raise ValueError("Missing original archive-derived LP columns")
    if len(frame)!=189 or frame.duplicated(keys).any():
        raise ValueError("Expected unique complete 189-case orthogonal source LP grid")
    if set(frame.source_shape_group)!=set(range(1,8)) or set(frame.synthetic_supply_shape)!=set(SUPPLY):
        raise ValueError("Incomplete source groups or synthetic supply profiles")
    if not frame.solver_status.eq("optimal").all() or not frame.source_hours.eq(8760).all():
        raise ValueError("Original LP feasibility or hourly source scope mismatch")
    if frame.storage_terminal_soc_mwh.abs().max()>1e-5:
        raise ValueError("Non-cyclic baseline source LP")
    values=frame[list(MEASURES)].to_numpy(dtype=float)
    if not np.isfinite(values).all() or (values<-1e-5).any():
        raise ValueError("Nonfinite or negative original LP metric")
    rows=[]
    for (group,shape),part in frame.groupby(["source_shape_group","synthetic_supply_shape"]):
        if len(part)!=9 or set(part.battery_power_peak_ratio)!=set(POWERS) or set(part.battery_energy_peak_hours)!=set(ENERGIES):
            raise ValueError("Missing source shape 3-by-3 factorial cells")
        if len(part[["state","reeds_zone"]].drop_duplicates())!=1:
            raise ValueError("Source-demand representative changed within group")
        a=part.set_index(["battery_power_peak_ratio","battery_energy_peak_hours"])
        # Relax only numerical solver noise (0.1 USD absolute); do not demand
        # nonnegative discharge at every corner, as degenerate LP solutions may differ.
        for col in ("objective_illustrative_variable_usd",):
            for p in POWERS:
                for el,eh in zip(ENERGIES[:-1],ENERGIES[1:]):
                    if a.loc[(p,eh),col]>a.loc[(p,el),col]+.1:
                        raise ValueError("More MWh increases optimum LP objective")
            for e in ENERGIES:
                for pl,ph in zip(POWERS[:-1],POWERS[1:]):
                    if a.loc[(ph,e),col]>a.loc[(pl,e),col]+.1:
                        raise ValueError("More MW increases optimum LP objective")
        baseline=float(a.loc[(.25,1.),"objective_illustrative_variable_usd"])
        if baseline<=0:raise ValueError("Cannot normalize against nonpositive baseline objective")
        for pl,ph in zip(POWERS[:-1],POWERS[1:]):
            for el,eh in zip(ENERGIES[:-1],ENERGIES[1:]):
                ll=a.loc[(pl,el)]
                lh=a.loc[(pl,eh)]
                hl=a.loc[(ph,el)]
                hh=a.loc[(ph,eh)]
                # Benefit of expanding MWh separately at low/high fixed power:
                b_low=ll.objective_illustrative_variable_usd-lh.objective_illustrative_variable_usd
                b_high=hl.objective_illustrative_variable_usd-hh.objective_illustrative_variable_usd
                interaction=float(b_high-b_low)
                # Mechanistic accounting identity: C=5*(available-unused)+90*firm
                # for each fixed supply/zone. Reconcile the cross difference.
                avoided_firm_high=hl.firm_generation_mwh-hh.firm_generation_mwh
                avoided_firm_low=ll.firm_generation_mwh-lh.firm_generation_mwh
                avoided_unused_high=hl.unused_renewable_mwh-hh.unused_renewable_mwh
                avoided_unused_low=ll.unused_renewable_mwh-lh.unused_renewable_mwh
                expected=90*(avoided_firm_high-avoided_firm_low)-5*(avoided_unused_high-avoided_unused_low)
                if not np.isclose(interaction,expected,rtol=1e-8,atol=.1):
                    raise ValueError("Interaction cost component identity mismatch")
                rows.append({"source_shape_group":int(group),"state":ll.state,
                             "reeds_zone":ll.reeds_zone,"synthetic_supply_shape":shape,
                             "low_power_peak_ratio":pl,"high_power_peak_ratio":ph,
                             "low_energy_peak_hours":el,"high_energy_peak_hours":eh,
                             "energy_benefit_low_power_usd":float(b_low),
                             "energy_benefit_high_power_usd":float(b_high),
                             "mw_mwh_objective_interaction_usd":interaction,
                             "mw_mwh_interaction_pct_of_baseline_cost":100*interaction/baseline,
                             "interaction_avoided_firm_component_usd":90*(avoided_firm_high-avoided_firm_low),
                             "interaction_avoided_unused_component_usd":-5*(avoided_unused_high-avoided_unused_low),
                             "interaction_positive_over_one_usd":bool(interaction>1),
                             "interaction_negative_below_minus_one_usd":bool(interaction<-1)})
    result=pd.DataFrame(rows).sort_values(["source_shape_group","synthetic_supply_shape",
                                            "low_power_peak_ratio","low_energy_peak_hours"]).reset_index(drop=True)
    if len(result)!=84 or result.duplicated(["source_shape_group","synthetic_supply_shape",
                                                "low_power_peak_ratio","low_energy_peak_hours"]).any():
        raise ValueError("Expected 84 unique adjacent interaction rectangles")
    return result

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-csv",type=Path,required=True)
    parser.add_argument("--out-dir",type=Path,required=True)
    args=parser.parse_args()
    source=pd.read_csv(args.source_csv)
    result=audit(source)
    args.out_dir.mkdir(parents=True,exist_ok=True)
    result.to_csv(args.out_dir/"paper_s_84_orthogonal_interactions.csv",index=False,float_format="%.12g")
    counts=(result.groupby("synthetic_supply_shape")
            .agg(positive_interactions=("interaction_positive_over_one_usd","sum"),
                 negative_interactions=("interaction_negative_below_minus_one_usd","sum"),
                 median_pct_baseline=("mw_mwh_interaction_pct_of_baseline_cost","median"),
                 largest_pct_baseline=("mw_mwh_interaction_pct_of_baseline_cost","max"))
            .reset_index())
    counts.to_csv(args.out_dir/"paper_s_interaction_signs_by_supply.csv",index=False)
    summary={"status":"PAPER_S_ORTHOGONAL_MW_MWH_84_INTERACTIONS_RECONCILED",
             "source_cases":189,"adjacent_two_by_two_rectangles":84,
             "source_demand_shape_groups":7,"synthetic_supply_profiles":3,
             "interpretation":"positive interaction = higher MWh benefit at higher fixed MW",
             "interaction_is_real_causal_estimate":False,"contains_battery_capex":False,
             "source_clock_verified_utc":False}
    (args.out_dir/"paper_s_interaction_manifest.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(counts.to_string(index=False))
    print(json.dumps(summary,indent=2))

if __name__=="__main__":main()
