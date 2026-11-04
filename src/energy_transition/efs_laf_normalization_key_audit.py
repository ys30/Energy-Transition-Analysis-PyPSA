"""Audit divergence between base-network LAF origin and ReEDS demand keys.

Upstream build_base_network.py divides load_weight by a national
'full_state' total, then drops full_state and later assigns reeds_state.
Consequently a Western subset's reeds_state sum is not a valid test of
the original normalization key. This auditor never alters weights.
"""
from __future__ import annotations
import pandas as pd
import numpy as np


_STATE_CODES = {
    "Arizona": "AZ", "California": "CA", "Colorado": "CO",
    "Idaho": "ID", "Montana": "MT", "Nevada": "NV",
    "New Mexico": "NM", "Oregon": "OR", "Texas": "TX",
    "Utah": "UT", "Washington": "WA", "Wyoming": "WY",
}
def normalize_state_label(value: str) -> str:
    """Normalize known source state names/codes, reject unknowns."""
    name = str(value).strip()
    if name in _STATE_CODES:
        return _STATE_CODES[name]
    if name in _STATE_CODES.values():
        return name
    raise ValueError(f"Unrecognized native state label: {name!r}")


def audit_laf_key_semantics(buses: pd.DataFrame) -> dict:
    required={"reeds_state","state","reeds_zone","LAF_state"}
    missing=sorted(required-set(buses.columns))
    if missing:
        raise ValueError(f"Source network missing fields: {missing}")
    frame=buses[list(required)].copy()
    frame["laf_numeric"]=pd.to_numeric(frame["LAF_state"],errors="coerce")
    frame["valid_laf"]=np.isfinite(frame["laf_numeric"].to_numpy(dtype=float)) & frame["laf_numeric"].ge(0)
    # Expose categorical nonagreement without assuming which key is correct.
    if frame[["reeds_state","state"]].isna().any().any():
        raise ValueError("Missing state labels cannot be used for key comparison")
    frame["normalized_native_state"] = frame["state"].map(normalize_state_label)
    frame["normalized_reeds_state"] = frame["reeds_state"].map(normalize_state_label)
    frame["key_match"] = frame["normalized_native_state"].eq(frame["normalized_reeds_state"])
    by_state=[]
    for state, group in frame.groupby("reeds_state",dropna=False,sort=True):
        observed=group.loc[group["valid_laf"],"laf_numeric"]
        by_state.append({
            "reeds_state":str(state),
            "source_bus_count":int(len(group)),
            "valid_laf_count":int(group["valid_laf"].sum()),
            "missing_laf_count":int(group["laf_numeric"].isna().sum()),
            "observed_laf_sum":float(observed.sum()),
            "state_label_disagreement_count":int((~group["key_match"]).sum()),
            "raw_laf_sum_is_full_state_normalization_proof":False,
        })
    pairs=(frame.groupby(["normalized_native_state","normalized_reeds_state"],dropna=False)
           .size().reset_index(name="bus_count"))
    mismatches=pairs[pairs["normalized_native_state"]!=pairs["normalized_reeds_state"]]
    # Quantify observed allocation mass for each native-to-ReEDS crossing.
    # Never infer absent factors as zero, and never use raw mass as a
    # fully reconciled EFS demand transfer without original full_state data.
    mismatch_rows = frame.loc[~frame["key_match"]].copy()
    crossing_mass = []
    for (native, reeds), group in mismatch_rows.groupby(
        ["normalized_native_state", "normalized_reeds_state"], sort=True
    ):
        good = group.loc[group["valid_laf"], "laf_numeric"]
        crossing_mass.append({
            "native_state": str(native),
            "reeds_state": str(reeds),
            "bus_count": int(len(group)),
            "valid_laf_bus_count": int(group["valid_laf"].sum()),
            "missing_laf_bus_count": int(group["laf_numeric"].isna().sum()),
            "observed_laf_mass": float(good.sum()),
            "original_full_state_mass_reconciled": False,
        })
    by_origin = []
    for state, group in frame.groupby("normalized_native_state", sort=True):
        good = group.loc[group["valid_laf"], "laf_numeric"]
        crossing = group.loc[~group["key_match"] & group["valid_laf"], "laf_numeric"]
        by_origin.append({
            "native_state": str(state),
            "source_bus_count": int(len(group)),
            "missing_laf_bus_count": int(group["laf_numeric"].isna().sum()),
            "observed_laf_sum": float(good.sum()),
            "observed_crossing_laf_mass": float(crossing.sum()),
            "is_full_state_denominator_verified": False,
        })
    return {
        "source_bus_count":int(len(frame)),
        "raw_laf_origin_grouping":"full_state (removed from upstream exported bus attributes)",
        "demand_assignment_grouping":"reeds_state (after membership/county assignments)",
        "state_label_agreement_is_not_original_full_state_agreement":True,
        "state_vs_reeds_state_disagreement_buses":int((~frame["key_match"]).sum()),
        "state_reeds_state_mismatch_examples":[
            {"state":str(r.normalized_native_state),"reeds_state":str(r.normalized_reeds_state),
             "bus_count":int(r.bus_count)}
            for r in mismatches.head(25).itertuples(index=False)
        ],
        "observed_laf_by_reeds_state":by_state,
        "cross_state_observed_laf_mass": crossing_mass,
        "observed_laf_by_native_state": by_origin,
        "original_full_state_grouping_reconstructible_from_this_network":False,
        "renormalization_performed":False,
        "source_derived_load_weight_verified":False,
        "historical_demand_admitted":False,
        "note":"Native state vs ReEDS state is a diagnostic proxy, not the dropped full_state field. Matching strings are insufficient evidence of source geographic scope.",
    }
