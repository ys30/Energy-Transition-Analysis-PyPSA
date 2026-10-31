"""Translate empirical interchange gate outcomes into actionable, machine-readable blockers."""
from __future__ import annotations
import argparse
import json
from pathlib import Path


def summarize_gate(gate: dict) -> dict:
    decisions=gate.get("decisions",[])
    if not decisions:
        raise ValueError("No BA gate decisions supplied")
    out=[]
    for row in decisions:
        ba=row["ba_code"]
        reasons=[]
        if row["months_below_99pct_coverage"] > 0 or row["coverage_share"] < .99:
            reasons.append({"code":"temporal_coverage","next_check":"Audit missing D/NG/TI triples by UTC timestamp and source field; do not fill missing observations with zeros"})
        if row["months_over_10pct_residual"] > 0 or row["official_mae_share_of_load"] > .10:
            reasons.append({"code":"official_balance_residual","next_check":"Cross-check demand, generation and signed interchange reporting definitions against independent BA operational publications"})
        if row["interchange_calibration_eligible"] and reasons:
            raise ValueError(f"Inconsistent eligible gate result: {ba}")
        out.append({"ba_code":ba,"screening_passed":bool(row["interchange_calibration_eligible"]),
                    "physical_calibration_verified":False,"blockers":reasons,
                    "warning":"Screening alone cannot establish physical interchange or line parameters"})
    return {"policy":"Never infer transmission ratings or physical imports from failed BA screens",
            "ba_results":out}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--gate",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=summarize_gate(json.loads(a.gate.read_text()))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
