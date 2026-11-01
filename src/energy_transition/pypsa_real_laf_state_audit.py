"""Audit upstream-provided actual LAF_state on a built PyPSA-USA NetCDF.

Never renormalize: partial-state sums and source provenance matter.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pypsa


def audit(path: Path, out: Path):
    n=pypsa.Network(str(path))
    b=n.buses
    required={"LAF_state","state","reeds_zone"}
    if not required.issubset(b.columns): raise ValueError("Missing built-network LAF or geography")
    laf=pd.to_numeric(b["LAF_state"],errors="coerce")
    bad=int((~np.isfinite(laf)).sum())
    bad_mask=~np.isfinite(laf)
    missing_by_state={str(k):int(v) for k,v in bad_mask.groupby(b["state"]).sum().items() if v}
    missing_by_zone={str(k):int(v) for k,v in bad_mask.groupby(b["reeds_zone"]).sum().items() if v}
    negative=int((laf.dropna()<0).sum())
    per_state=laf.groupby(b["state"]).agg(["count","sum","min","max"])
    per_zone=laf.groupby([b["state"],b["reeds_zone"]]).sum()
    result={
      "source":"LAF_state embedded in pinned upstream-built elec_base_network.nc",
      "buses":len(b),"invalid_laf_values":bad,"negative_laf_values":negative,
      "nonzero_laf_buses":int((laf.fillna(0)>0).sum()),
      "missing_laf_by_state":missing_by_state,
      "missing_laf_by_zone":missing_by_zone,
      "laf_complete_for_all_buses":bad==0,
      "state_totals":{str(k):{"count":int(v["count"]),"sum":float(v["sum"]),"min":float(v["min"]),"max":float(v["max"])} for k,v in per_state.to_dict("index").items()},
      "state_zone_laf_sums":[{"state":str(s),"reeds_zone":str(z),"sum_laf":float(val)} for (s,z),val in per_zone.items()],
      "reeds_zone_count":int(b.reeds_zone.nunique()),
      "original_laf_state_unchanged":True,
      "allocation_provenance_review_required":True,
      "hourly_efs_allocated":False
    }
    # Missing upstream LAFs require separate investigation; do not coerce to zero.
    # Audit remains executable and explicitly records that load allocation is blocked.
    if negative: raise ValueError(f"Negative LAF data: {negative}")
    # Admit only fully observed, nonnegative state-level LAFs that do not over-allocate.
    # These are candidate source weights, not independently certified geographic truth.
    state_admission = {}
    for state, metrics in per_state.iterrows():
        missing = missing_by_state.get(str(state), 0)
        total = float(metrics["sum"])
        reasons = []
        if missing: reasons.append(f"{missing} missing bus LAF values")
        if total > 1.0001: reasons.append(f"state weight sum exceeds 1: {total}")
        if total <= 0: reasons.append("no positive state LAF mass")
        state_admission[str(state)] = {"preliminary_numerical_gate":not reasons, "blockers":reasons,
                                      "state_laf_sum":total, "bus_laf_missing":missing}
    result["per_state_admission"] = state_admission
    result["empirical_load_allocation_admitted"]=False
    result["independent_upstream_geography_certified"]=False
    result["state_sums_exceed_one"]=[str(k) for k,v in per_state["sum"].items() if v>1.0001]
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="state_zone_laf_sums"},indent=2))
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--network",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();audit(a.network,a.out)
