"""Isolated, scenario-only Colstrip transformer transfer LP.

Uses the parameters of each REAL exported PyPSA scenario Network, but solves
ONLY a two-bus interface abstraction; not a Western network OPF or powerflow.
Maximize transferred wind subject to transformer MVA proxy and wind availability.
MW/MVA capacity proxy assumes unity power factor; ignores voltage/reactive flow.
"""
import argparse,csv,json
from pathlib import Path
import pypsa
from scipy.optimize import linprog

WIND={"CWE_only":207.9,"CW3_only":100.0,"both_nameplate":307.9}

def run(folder):
    records=[]
    for path in sorted(folder.glob("SCENARIO_ONLY_S*_X*.nc")):
        n=pypsa.Network(str(path))
        transformer=n.transformers.loc["SCENARIO_ONLY_colstrip_500_to_345"]
        assert transformer.bus0=="SCENARIO_ONLY_colstrip_500kV"
        assert transformer.bus1=="2077254"
        capacity=float(transformer.s_nom)
        for case,available in WIND.items():
            # Decision variables: [transferred_MW, curtailed_MW]
            # Power conservation: transfer + curtailment = available wind.
            # Apparent limit approximated as active power at PF=1.
            opt=linprog(c=[-1.0,0.0],A_eq=[[1.0,1.0]],b_eq=[available],
                        bounds=[(0.0,capacity),(0.0,available)],method="highs")
            if not opt.success:raise RuntimeError(f"{path.name}/{case}: {opt.message}")
            transfer,curtail=map(float,opt.x)
            assert abs(transfer+curtail-available)<1e-7
            records.append({"scenario":path.stem,"case":case,
              "capacity_mva_hypothetical":capacity,"available_wind_mw":available,
              "optimized_transfer_mw":round(transfer,6),
              "optimized_curtailment_mw":round(curtail,6),
              "solver": "scipy_highs_linprog",
              "optimization_scope":"isolated_two_bus_interface_only",
              "full_western_opf_solved":False,
              "reactive_power_or_ac_flow_solved":False,
              "physical_interconnection_verified":False})
    if len(records)!=21:raise AssertionError(f"Expected 21: {len(records)}")
    out=folder/"SCENARIO_ONLY_isolated_transfer_lp.csv"
    with out.open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)
    summary={"optimized_cases":len(records),
      "positive_curtailment_cases":sum(r["optimized_curtailment_mw"]>1e-6 for r in records),
      "scope":"isolated_two_bus_interface_LP_not_full_grid_OPF",
      "full_western_opf_solved":False,"real_generator_bus_ties_verified":0}
    (folder/"SCENARIO_ONLY_isolated_transfer_lp.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))
if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("--folder",type=Path,required=True)
    run(a.parse_args().folder)
