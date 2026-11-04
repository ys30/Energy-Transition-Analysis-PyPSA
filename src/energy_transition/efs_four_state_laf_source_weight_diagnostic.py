"""Diagnose whether archived missing LAFs correspond to source load-weight gaps.

Read-only. The presence of load_weight/Pd on a bus, or absence of these
fields, never authorizes zero imputation or geographic renormalization.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

STATES={"California","Nevada","Oregon","Washington"}


def audit_blocked_states(buses: pd.DataFrame) -> dict:
    needed={"state","reeds_state","reeds_zone","LAF_state"}
    missing=sorted(needed-set(buses.columns))
    if missing:
        raise ValueError(f"Missing required bus fields: {missing}")
    x=buses.loc[buses["state"].isin(STATES)].copy()
    if set(x["state"])!=STATES:
        raise ValueError("All four blocked source states must be present")
    laf=pd.to_numeric(x["LAF_state"],errors="coerce")
    if (laf.dropna()<0).any() or not np.isfinite(laf.dropna()).all():
        raise ValueError("Invalid non-missing source LAF")
    x["numeric_laf"]=laf
    x["missing_laf"]=laf.isna()
    x["positive_laf"]=laf.gt(0).fillna(False)
    has_weight="load_weight" in x.columns
    has_pd="Pd" in x.columns
    if has_weight:
        weight=pd.to_numeric(x["load_weight"],errors="coerce")
        x["weight_valid"]=np.isfinite(weight.to_numpy(dtype=float)) & weight.ge(0)
        x["weight_positive"]=weight.gt(0).fillna(False)
        x["weight_missing"]=weight.isna()
        x["weight_nonfinite"]=~np.isfinite(weight.to_numpy(dtype=float))
        x["weight_value"]=weight
    records=[]
    for state,g in x.groupby("state",sort=True):
        mg=g[g["missing_laf"]]
        observed=float(g.loc[~g["missing_laf"],"numeric_laf"].sum())
        d={"state":str(state),"source_bus_count":int(len(g)),
           "missing_laf_count":int(len(mg)),
           "observed_laf_mass":observed,
           "positive_laf_bus_count":int(g["positive_laf"].sum()),
           "native_reeds_state_difference_count":int(
               (g["reeds_state"].astype(str).str.strip()!=
                {"California":"CA","Nevada":"NV","Oregon":"OR","Washington":"WA"}[state]).sum()),
           "laf_numerical_gate_passed":bool(len(mg)==0 and 0<observed<=1.0001)}
        if has_weight:
            d.update({
                "load_weight_attribute_present":True,
                "missing_laf_with_positive_load_weight":int(mg["weight_positive"].sum()),
                "missing_laf_with_zero_load_weight":int(
                    (mg["weight_valid"] & ~mg["weight_positive"]).sum()),
                "missing_laf_with_invalid_or_absent_load_weight":int(
                    (~mg["weight_valid"]).sum()),
                "missing_laf_weight_sum_valid_only":float(
                    mg.loc[mg["weight_valid"],"weight_value"].sum()),
                "all_state_valid_weight_sum":float(
                    g.loc[g["weight_valid"],"weight_value"].sum()),
                "all_state_invalid_weight_count":int((~g["weight_valid"]).sum()),
            })
        else:
            d["load_weight_attribute_present"]=False
        if has_pd:
            raw_pd=pd.to_numeric(g["Pd"],errors="coerce")
            missing_pd=pd.to_numeric(mg["Pd"],errors="coerce")
            d.update({
                "Pd_attribute_present":True,
                "Pd_missing_or_nonfinite_on_missing_laf":int(
                    (~np.isfinite(missing_pd.to_numpy(dtype=float))).sum()),
                "Pd_positive_on_missing_laf":int(
                    (missing_pd.gt(0) & np.isfinite(missing_pd.to_numpy(dtype=float))).sum()),
                "Pd_zero_on_missing_laf":int(
                    (missing_pd.eq(0) & np.isfinite(missing_pd.to_numpy(dtype=float))).sum()),
                "Pd_negative_on_missing_laf":int(
                    (missing_pd.lt(0) & np.isfinite(missing_pd.to_numpy(dtype=float))).sum()),
                "Pd_sum_missing_laf_finite_only":float(
                    missing_pd[np.isfinite(missing_pd.to_numpy(dtype=float))].sum()),
                "Pd_sum_all_state_finite_only":float(
                    raw_pd[np.isfinite(raw_pd.to_numpy(dtype=float))].sum()),
                "Pd_is_verified_EFS_allocation_weight":False,
            })
        else:
            d["Pd_attribute_present"]=False
        records.append(d)
    return {
        "source_bus_count":int(len(x)),
        "source_states_audited":sorted(STATES),
        "blocked_state_diagnostics":records,
        "source_bus_load_weight_present":has_weight,
        "source_bus_Pd_present":has_pd,
        "zero_weight_implies_zero_future_demand":False,
        "missing_laf_can_be_imputed":False,
        "original_full_state_denominator_recovered":False,
        "all_four_states_empirically_admitted":False,
        "note":"Source bus weight inventory only; even zero weights do not prove independently audited regional allocation or fix state-to-ReEDS mismatch.",
    }


def main():
    import pypsa
    p=argparse.ArgumentParser()
    p.add_argument("--network",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    n=pypsa.Network(str(a.network))
    r=audit_blocked_states(n.buses)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(r,indent=2))

if __name__=="__main__":
    main()
