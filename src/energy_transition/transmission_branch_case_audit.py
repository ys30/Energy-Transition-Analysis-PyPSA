"""Conservative pre-ingestion audit for independently obtained branch CSVs.

This validator checks coverage, units and provenance metadata, but cannot verify
that external source documents genuinely support the supplied physical values.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import pandas as pd
from .transmission_evidence_gate import screen_transmission_inputs


def audit_branch_case(frame: pd.DataFrame, *, case_year: int, kind: str) -> dict:
    if kind not in ("historical", "planning"):
        raise ValueError("Case kind must explicitly be historical or planning")
    if not 2000<=case_year<=2100:
        raise ValueError("Invalid source case year")
    required={"from_ba","to_ba","capacity_mw","reactance_pu",
              "reactance_ohm","resistance_ohm","nominal_kv",
              "source_url","source_year","evidence_status"}
    missing=required-set(frame.columns)
    if missing:
        raise ValueError(f"Missing physical branch fields: {sorted(missing)}")
    status=screen_transmission_inputs(frame)
    if not status["ready"]:
        return {"ready":False,"case_year":case_year,"case_kind":kind,
                "reason":"no_verified_branch_records"}
    for column in ("reactance_ohm","resistance_ohm","nominal_kv"):
        numeric=pd.to_numeric(frame[column],errors="coerce")
        if numeric.isna().any() or not numeric.map(math.isfinite).all():
            raise ValueError(f"Nonfinite {column}")
        invalid = numeric.lt(0) if column=="resistance_ohm" else numeric.le(0)
        if invalid.any():
            raise ValueError(f"Invalid {column}")
    # These fields are supplied by the same dataset and are not an independent audit.
    # Preserve the claim, but never elevate it into source authentication.
    if not frame.evidence_status.eq("independently_verified").all():
        raise ValueError("Claimed evidence status missing; independent authentication still required")
    if not pd.to_numeric(frame.source_year).eq(case_year).all():
        raise ValueError("Branch source year differs from declared case year")
    return {"ready_for_engineering_review":True,
            "claimed_evidence_status":"independently_verified_unconfirmed",
            "source_authenticity_independently_confirmed":False,
            "ready_for_pypsa_physical_calibration":False,
            "ready_for_historical_2024_calibration":False,
            "case_year":case_year,"case_kind":kind,"branch_rows":len(frame),
            "caveat":"Electrical BA aggregations and source authenticity require manual expert validation"}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--csv",type=Path,required=True)
    p.add_argument("--case-year",type=int,required=True)
    p.add_argument("--kind",choices=("historical","planning"),required=True)
    p.add_argument("--report",type=Path,required=True)
    args=p.parse_args()
    input_bytes=args.csv.read_bytes()
    output=audit_branch_case(pd.read_csv(args.csv),case_year=args.case_year,kind=args.kind)
    output["input_sha256"]=hashlib.sha256(input_bytes).hexdigest()
    output["input_filename"]=args.csv.name
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(output,indent=2)+"\n")
    print(json.dumps(output,indent=2))


if __name__=="__main__":
    main()
