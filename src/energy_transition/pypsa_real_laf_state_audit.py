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
    negative=int((laf.dropna()<0).sum())
    per_state=laf.groupby(b["state"]).agg(["count","sum","min","max"])
    per_zone=laf.groupby([b["state"],b["reeds_zone"]]).sum()
    result={
      "source":"LAF_state embedded in pinned upstream-built elec_base_network.nc",
      "buses":len(b),"invalid_laf_values":bad,"negative_laf_values":negative,
      "nonzero_laf_buses":int((laf.fillna(0)>0).sum()),
      "state_totals":{str(k):{"count":int(v["count"]),"sum":float(v["sum"]),"min":float(v["min"]),"max":float(v["max"])} for k,v in per_state.to_dict("index").items()},
      "state_zone_laf_sums":[{"state":str(s),"reeds_zone":str(z),"sum_laf":float(val)} for (s,z),val in per_zone.items()],
      "reeds_zone_count":int(b.reeds_zone.nunique()),
      "original_laf_state_unchanged":True,
      "allocation_provenance_review_required":True,
      "hourly_efs_allocated":False
    }
    if bad or negative: raise ValueError(f"Invalid LAF data: nonfinite={bad}, negative={negative}")
    if (per_state["sum"]>1.0001).any(): raise ValueError("LAF sums exceed 1 for some state")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="state_zone_laf_sums"},indent=2))
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--network",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();audit(a.network,a.out)
