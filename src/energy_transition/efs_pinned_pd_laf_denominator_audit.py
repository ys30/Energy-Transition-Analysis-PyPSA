"""Pinned PyPSA-USA original Pd/LAF consistency evidence (read-only).

Pinned build_base_network.py (338af991...) constructs LAF_state = Pd /
sum(Pd grouped by full_state), before full_state is dropped and network
is spatially filtered. Exported 'state' is a proxy, NOT source full_state.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

PIN="338af9912addbaf038c6098fe27e1e6ef099d8aa"
FORMULA='gdf_bus["LAF_state"] = gdf_bus["Pd"] / group_sums'
GROUP='group_sums = gdf_bus.groupby("full_state")["Pd"].transform("sum")'


def audit(buses:pd.DataFrame, pinned_source:str)->dict:
    if FORMULA not in pinned_source or GROUP not in pinned_source:
        raise ValueError("Pinned upstream Pd/full_state formula not verified")
    required={"Pd","LAF_state","state","reeds_state","reeds_zone"}
    if not required.issubset(buses.columns):
        raise ValueError(f"Missing original bus source fields: {sorted(required-set(buses.columns))}")
    data=buses.copy()
    pdv=pd.to_numeric(data["Pd"],errors="coerce")
    laf=pd.to_numeric(data["LAF_state"],errors="coerce")
    pd_valid=np.isfinite(pdv.to_numpy(dtype=float)) & pdv.ge(0)
    laf_valid=np.isfinite(laf.to_numpy(dtype=float)) & laf.ge(0)
    positive=pd_valid & laf_valid & pdv.gt(0) & laf.gt(0)
    inconsistent_pd=pd_valid & pdv.gt(0) & laf_valid & laf.eq(0)
    inconsistent_laf=pd_valid & pdv.eq(0) & laf_valid & laf.gt(0)
    missing=~laf_valid
    data["_Pd"]=pdv
    data["_laf"]=laf
    data["_pos"]=positive
    data["_missing"]=missing
    data["_pd_pos_laf_zero"]=inconsistent_pd
    data["_pd_zero_laf_pos"]=inconsistent_laf
    data["_ratio"]=(data["_Pd"]/data["_laf"]).where(data["_pos"])
    # Source Pd is in hundredths on the original Breakthrough base grid.
    # The inferred denominator is clustered at cent precision for a
    # diagnostic grouping, not a substitute for the dropped full_state key.
    data["_denominator_cent"]=data["_ratio"].round(2)
    states=[]
    for state,g in data.groupby("state",sort=True):
        good=g[g["_pos"]]
        denominators=(good["_Pd"]/good["_laf"]).to_numpy(dtype=float)
        if len(denominators):
            center=float(np.median(denominators))
            max_rel=float(np.max(np.abs(denominators-center)/center))
            spread=float(np.max(denominators)-np.min(denominators))
        else:
            center=None;max_rel=None;spread=None
        absent=g[g["_missing"]]
        denominator_clusters=[]
        for denom,gg in good.groupby("_denominator_cent",sort=True):
            denominator_clusters.append({
                "inferred_denominator_Pd":float(denom),
                "positive_Pd_positive_LAF_buses":int(len(gg)),
                "observed_laf_mass":float(gg["_laf"].sum()),
                "source_Pd_sum":float(gg["_Pd"].sum()),
                "bus_examples":[str(b) for b in gg.index[:8]],
                "original_full_state_label_verified":False,
            })
        states.append({
            "native_state":str(state),
            "source_bus_count":int(len(g)),
            "positive_Pd_positive_LAF_bus_count":int(len(good)),
            "positive_Pd_zero_LAF_bus_count":int(g["_pd_pos_laf_zero"].sum()),
            "zero_Pd_positive_LAF_bus_count":int(g["_pd_zero_laf_pos"].sum()),
            "missing_LAF_bus_count":int(len(absent)),
            "missing_LAF_with_zero_Pd":int(
                (absent["_Pd"].eq(0)&np.isfinite(absent["_Pd"].to_numpy(dtype=float))).sum()),
            "missing_LAF_with_positive_Pd":int(
                (absent["_Pd"].gt(0)&np.isfinite(absent["_Pd"].to_numpy(dtype=float))).sum()),
            "inferred_full_state_denominator_median_Pd":center,
            "inferred_denominator_clusters":denominator_clusters,
            "inferred_denominator_max_relative_deviation":max_rel,
            "inferred_denominator_absolute_spread":spread,
            "native_state_is_original_full_state_verified":False,
        })
    return {
        "pinned_source_commit":PIN,
        "pinned_source_sha256":hashlib.sha256(pinned_source.encode()).hexdigest(),
        "pinned_source_formula_verified":True,
        "original_LAF_numerator":"Pd",
        "original_LAF_denominator":"national pre-filter full_state sum(Pd)",
        "source_load_weight_field_expected_in_pinned_revision":False,
        "source_bus_count":int(len(data)),
        "states":states,
        "all_missing_laf_zero_Pd":bool(
            pd_valid[missing].all() and pdv[missing].eq(0).all()),
        "original_full_state_labels_recovered":False,
        "national_denominators_independently_verified":False,
        "missing_LAF_imputed":False,
        "western_EFS_demand_admitted":False,
        "note":"Median Pd/LAF is an inferred diagnostic only. Exported native state is not necessarily the deleted original full_state denominator key.",
    }


def main():
    import pypsa
    p=argparse.ArgumentParser()
    p.add_argument("--network",type=Path,required=True)
    p.add_argument("--upstream-source",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    n=pypsa.Network(str(a.network))
    r=audit(n.buses,a.upstream_source.read_text(encoding="utf-8"))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(r,indent=2))

if __name__=="__main__":
    main()
