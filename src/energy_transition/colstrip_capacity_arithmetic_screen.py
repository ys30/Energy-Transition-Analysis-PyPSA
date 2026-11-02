"""Scenario-only capacity screen; NOT an AC/DC power-flow or dispatch solution."""
import argparse,csv,json
from pathlib import Path
import pypsa

INJECTIONS={"CWE_only":207.9,"CW3_only":100.0,"both_nameplate":307.9}
def run(folder):
    records=[]
    for path in sorted(folder.glob("SCENARIO_ONLY_S*_X*.nc")):
        n=pypsa.Network(str(path))
        tf=n.transformers.loc["SCENARIO_ONLY_colstrip_500_to_345"]
        cap=float(tf.s_nom)
        for label,mw in INJECTIONS.items():
            # 1.0 power factor, MW/MVA arithmetic only. Does not test thermal flow,
            # voltages, stability, losses, actual dispatch or physical assets.
            records.append({"scenario":path.stem,"injection_case":label,
                "hypothetical_active_mw":mw,"hypothetical_transformer_mva":cap,
                "nameplate_ratio_at_pf1":mw/cap,
                "nameplate_under_rating_at_pf1":mw<=cap,
                "powerflow_solved":False,"empirical_injection_verified":False})
    if len(records)!=21:raise ValueError(f"Expected 7 scenarios x 3 cases, got {len(records)}")
    dest=folder/"SCENARIO_ONLY_capacity_arithmetic_screen.csv"
    with dest.open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)
    result={"scenarios":7,"nameplate_cases":3,"checks":len(records),
        "cases_exceeding_rating_at_pf1":sum(not x["nameplate_under_rating_at_pf1"] for x in records),
        "ac_or_dc_powerflow_executed":False,"real_generator_bus_ties_verified":0}
    (folder/"SCENARIO_ONLY_capacity_arithmetic_screen.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--folder",type=Path,required=True)
    run(p.parse_args().folder)
