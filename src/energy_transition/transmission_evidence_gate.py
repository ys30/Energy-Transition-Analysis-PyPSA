"""Evidence gate before introducing physical CISO/BPAT transmission links.

EIA-930 net interchange measurements are not line ratings or branch topology.
Require independently sourced, finite and explicitly rated infrastructure inputs.
"""
from __future__ import annotations
import pandas as pd
import numpy as np


def screen_transmission_inputs(lines: pd.DataFrame, bas=("CISO", "BPAT")) -> dict:
    required={"from_ba","to_ba","capacity_mw","reactance_pu","source_url","source_year"}
    if required-set(lines.columns):
        raise ValueError(f"Missing required transmission evidence: {sorted(required-set(lines.columns))}")
    if lines.empty:
        return {"ready":False,"accepted_edges":0,
                "reason":"no_verified_transmission_edges"}
    data=lines.copy()
    if data[["from_ba","to_ba"]].isna().any().any():
        raise ValueError("Null BA endpoints")
    if (~data.from_ba.isin(bas)).any() or (~data.to_ba.isin(bas)).any():
        raise ValueError("Transmission edge outside selected BA scope")
    if data.from_ba.eq(data.to_ba).any():
        raise ValueError("Self-loop is not inter-BA transmission")
    undirected=data.apply(lambda r:tuple(sorted((r.from_ba,r.to_ba))),axis=1)
    if undirected.duplicated().any():
        raise ValueError("Duplicate undirected BA corridor; aggregate only with source evidence")
    for col in ("capacity_mw","reactance_pu","source_year"):
        data[col]=pd.to_numeric(data[col],errors="coerce")
        if not np.isfinite(data[col].to_numpy(dtype=float)).all():
            raise ValueError(f"Nonfinite or missing {col}")
    if data.capacity_mw.le(0).any() or data.reactance_pu.le(0).any():
        raise ValueError("Positive independently verified rating and reactance are required")
    if data.source_year.lt(2000).any() or data.source_year.gt(2100).any():
        raise ValueError("Implausible source year")
    if data.source_url.isna().any() or (~data.source_url.astype(str).str.startswith(("https://","http://"))).any():
        raise ValueError("Traceable transmission evidence URLs required")
    return {"ready":True,"accepted_edges":len(data),
            "reason":"sourced_ratings_and_reactances_present_not_yet_grid_calibrated",
            "warning":"EIA-930 interchange must not be substituted for physical Line or Link capacity."}
