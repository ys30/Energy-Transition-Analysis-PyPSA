"""Audit divergence between base-network LAF origin and ReEDS demand keys.

Upstream build_base_network.py divides load_weight by a national
'full_state' total, then drops full_state and later assigns reeds_state.
Consequently a Western subset's reeds_state sum is not a valid test of
the original normalization key. This auditor never alters weights.
"""
from __future__ import annotations
import pandas as pd
import numpy as np


def audit_laf_key_semantics(buses: pd.DataFrame) -> dict:
    required={"reeds_state","state","reeds_zone","LAF_state"}
    missing=sorted(required-set(buses.columns))
    if missing:
        raise ValueError(f"Source network missing fields: {missing}")
    frame=buses[list(required)].copy()
    frame["laf_numeric"]=pd.to_numeric(frame["LAF_state"],errors="coerce")
    frame["valid_laf"]=np.isfinite(frame["laf_numeric"].to_numpy(dtype=float)) & frame["laf_numeric"].ge(0)
    # Expose categorical nonagreement without assuming which key is correct.
    labels=frame[["reeds_state","state"]].astype("string").apply(lambda c:c.str.strip())
    matched=labels.notna().all(axis=1) & labels["reeds_state"].eq(labels["state"])
    frame["key_match"]=matched.fillna(False)
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
    pairs=(frame.groupby(["state","reeds_state"],dropna=False)
           .size().reset_index(name="bus_count"))
    mismatches=pairs[pairs["state"].astype("string")!=pairs["reeds_state"].astype("string")]
    return {
        "source_bus_count":int(len(frame)),
        "raw_laf_origin_grouping":"full_state (removed from upstream exported bus attributes)",
        "demand_assignment_grouping":"reeds_state (after membership/county assignments)",
        "state_label_agreement_is_not_original_full_state_agreement":True,
        "state_vs_reeds_state_disagreement_buses":int((~frame["key_match"]).sum()),
        "state_reeds_state_mismatch_examples":[
            {"state":str(r.state),"reeds_state":str(r.reeds_state),
             "bus_count":int(r.bus_count)}
            for r in mismatches.head(25).itertuples(index=False)
        ],
        "observed_laf_by_reeds_state":by_state,
        "original_full_state_grouping_reconstructible_from_this_network":False,
        "renormalization_performed":False,
        "source_derived_load_weight_verified":False,
        "historical_demand_admitted":False,
        "note":"Native state vs ReEDS state is a diagnostic proxy, not the dropped full_state field. Matching strings are insufficient evidence of source geographic scope.",
    }
