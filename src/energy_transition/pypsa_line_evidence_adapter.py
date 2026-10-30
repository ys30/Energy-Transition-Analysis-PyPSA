"""Build explicit PyPSA AC Line objects only from screened source-evidence inputs.

This adapter does not certify source authenticity or physical bus-equivalence:
BA-level buses are aggregates. Use for sensitivity experiments only.
"""
from __future__ import annotations
import pandas as pd
from .transmission_evidence_gate import screen_transmission_inputs


def add_screened_ba_lines(network, lines: pd.DataFrame, bas=("CISO","BPAT")):
    screening=screen_transmission_inputs(lines,bas=bas)
    if not screening["ready"]:
        raise ValueError("No screened transmission inputs: refuse invented interconnection")
    if any(ba not in network.buses.index for ba in bas):
        raise ValueError("Expected BA buses missing from PyPSA network")
    # PyPSA Line.x represents series reactance in ohms, not per-unit.
    # Require voltage and physical reactance inputs rather than copying x_pu.
    needed={"reactance_ohm","resistance_ohm","nominal_kv","evidence_status"}
    if needed-set(lines.columns):
        raise ValueError("AC line requires sourced ohm parameters, voltage and evidence status")
    data=lines.copy()
    for col in ("reactance_ohm","resistance_ohm","nominal_kv"):
        data[col]=pd.to_numeric(data[col],errors="coerce")
        if data[col].isna().any() or not data[col].map(lambda x: x==x and abs(x)!=float("inf")).all():
            raise ValueError(f"Invalid {col}")
    if data.reactance_ohm.le(0).any() or data.resistance_ohm.lt(0).any() or data.nominal_kv.le(0).any():
        raise ValueError("Invalid AC line impedance or voltage")
    if not data.evidence_status.eq("independently_verified").all():
        raise ValueError("All branches must have independently verified physical parameters")
    # Validate every branch endpoint, not just the first line touching each BA.
    for _, row in data.iterrows():
        for ba in (row.from_ba, row.to_ba):
            if ba not in network.buses.index:
                raise ValueError(f"Unknown line endpoint: {ba}")
            voltage = pd.to_numeric(pd.Series([network.buses.loc[ba, "v_nom"]]),
                                    errors="coerce").iloc[0]
            if pd.isna(voltage) or not (float(voltage) > 0):
                raise ValueError(f"Missing nominal bus voltage for {ba}")
            if abs(float(voltage) - float(row.nominal_kv)) > 1e-6:
                raise ValueError(f"Line voltage incompatible with bus {ba}")
    for i,row in data.reset_index(drop=True).iterrows():
        network.add("Line",f"evidence_line_{i}",bus0=row.from_ba,bus1=row.to_ba,
                    r=float(row.resistance_ohm),x=float(row.reactance_ohm),
                    s_nom=float(row.capacity_mw))
    return screening
