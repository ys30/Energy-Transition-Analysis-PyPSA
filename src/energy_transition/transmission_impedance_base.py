"""Independent numeric consistency check for imported branch impedance units.

This checks units, not the provenance, network aggregation, or authenticity of a
historical WECC physical case. z_base_ohm = nominal_kv**2 / base_mva.
"""
from __future__ import annotations
import numpy as np
import pandas as pd


def check_reactance_base(frame: pd.DataFrame, *, tolerance: float = 0.02) -> dict:
    required={"reactance_pu","reactance_ohm","nominal_kv","base_mva"}
    missing=required-set(frame.columns)
    if missing:
        raise ValueError(f"Missing impedance-base fields: {sorted(missing)}")
    if frame.empty:
        raise ValueError("Cannot check impedance base for empty branch case")
    if not (0 <= tolerance < 1):
        raise ValueError("Tolerance must be within [0, 1)")
    values=frame[list(sorted(required))].apply(pd.to_numeric,errors="coerce")
    if not np.isfinite(values.to_numpy(dtype=float)).all() or (values<=0).any().any():
        raise ValueError("Reactance, voltage and base MVA must all be finite and positive")
    implied=values["reactance_ohm"]*values["base_mva"]/values["nominal_kv"].pow(2)
    relative=((implied-values["reactance_pu"]).abs()/values["reactance_pu"])
    return {
        "ready":bool((relative<=tolerance).all()),
        "branch_rows":int(len(frame)),
        "max_relative_difference":float(relative.max()),
        "tolerance":float(tolerance),
        "definition":"X_pu = X_ohm * base_mva / nominal_kv**2",
        "scope":"Unit-consistency only; historical source authenticity and BA-equivalent electrical validity unverified",
    }
