"""Compare qualified EIA-923 BA/fuel generation with solved 2024 PyPSA dispatch.

Observed source rows are only EIA-923 Page 1 fully reconciled records.
No model fitting, no rescaling of source data, no implied EIA-930 equivalence.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

FUEL_TECH = {
 "NG":"gas","BFG":"gas","OG":"gas","PG":"gas",
 "BIT":"coal","SUB":"coal","LIG":"coal","WC":"coal","RC":"coal",
 "NUC":"nuclear","WAT":"hydro","WND":"wind",
 "SUN":"solar","GEO":"geothermal","MWH":"storage",
 "DFO":"oil","RFO":"oil","KER":"oil","JF":"oil",
 "WDS":"biomass","WDL":"biomass","BLQ":"biomass","LFG":"biomass","MSW":"biomass",
}
def compare(qualified, network):
    q=qualified.copy()
    required={"ba_code","fuel","qualified_annual_mwh","source_rows","qualified_rows","withheld_reported_annual_mwh"}
    if required-set(q):raise ValueError("EIA-923 qualification columns missing")
    q["tech"]=q.fuel.map(FUEL_TECH).fillna("unmapped_"+q.fuel.astype(str))
    if q.duplicated(["ba_code","fuel"]).any():raise ValueError("Duplicate BA/fuel qualified records")
    bytech=q.groupby(["ba_code","tech"],as_index=False).agg(
        eia923_qualified_mwh=("qualified_annual_mwh","sum"),
        withheld_reported_mwh=("withheld_reported_annual_mwh","sum"),
        source_rows=("source_rows","sum"),qualified_rows=("qualified_rows","sum"))
    records=[]
    weight=network.snapshot_weightings.generators
    dispatch=network.generators_t.p
    if not dispatch.index.equals(weight.index):
        raise ValueError("Generator dispatch snapshots and generator weights must match exactly")
    if not weight.index.is_unique or weight.isna().any() or not pd.to_numeric(weight, errors="coerce").notna().all():
        raise ValueError("Generator weights must be unique, finite and nonmissing")
    import numpy as np
    if not np.isfinite(weight.to_numpy(dtype=float)).all() or (weight <= 0).any():
        raise ValueError("Generator weights must be finite and strictly positive")
    if not dispatch.index.is_unique or not np.isfinite(dispatch.to_numpy(dtype=float)).all():
        raise ValueError("Generator dispatch must have unique snapshots and finite values")
    for name,row in network.generators.iterrows():
        ba=str(row.bus)
        # Refuse to silently misclassify a generator whose name does not
        # encode the expected BA prefix. No heuristic fuel assignment.
        if not str(name).startswith(ba + "_"):
            raise ValueError(f"Generator {name!r} lacks expected BA prefix {ba!r}")
        tech=str(name)[len(ba) + 1:]
        if tech=="unserved":continue
        if tech not in ("gas","coal","nuclear","hydro","wind","solar"):continue
        if name not in dispatch.columns:
            raise ValueError(f"Missing dispatch series for generator {name}")
        generation=float((dispatch[name]*weight).sum())
        records.append({"ba_code":ba,"tech":tech,"pypsa_dispatch_mwh":generation})
    # A network with no supported thermal/renewable generators still has a
    # meaningful observed-only comparison; do not crash on an empty groupby.
    if records:
        model=pd.DataFrame(records).groupby(["ba_code","tech"],as_index=False).pypsa_dispatch_mwh.sum()
    else:
        model=pd.DataFrame(columns=["ba_code","tech","pypsa_dispatch_mwh"])
    joined=bytech.merge(model,on=["ba_code","tech"],how="outer",indicator=True)
    joined["comparison_status"]=joined["_merge"].map({"both":"both_sources","left_only":"observed_only","right_only":"model_only"}).astype(str)
    joined=joined.drop(columns="_merge")
    comparable=joined.comparison_status.eq("both_sources")
    joined["model_minus_qualified_observed_mwh"]=(joined.pypsa_dispatch_mwh-joined.eia923_qualified_mwh).where(comparable)
    joined["relative_difference_vs_qualified_observed"]=(joined.model_minus_qualified_observed_mwh/joined.eia923_qualified_mwh).where(comparable & joined.eia923_qualified_mwh.gt(0))
    joined["full_source_row_coverage"]=joined.qualified_rows.eq(joined.source_rows)
    # Signed net generation is valid source evidence, but an annual percentage
    # discrepancy only has a stable denominator for strictly positive observed MWh.
    joined["absolute_difference_mwh"] = joined.model_minus_qualified_observed_mwh.abs()
    joined["absolute_percentage_difference"] = (
        joined["relative_difference_vs_qualified_observed"].abs()
        .where(comparable & joined.eia923_qualified_mwh.gt(0))
    )
    joined["benchmark_evidence_status"] = "unmatched_source_boundary"
    joined.loc[comparable, "benchmark_evidence_status"] = "partial_source_coverage"
    joined.loc[comparable & joined.full_source_row_coverage, "benchmark_evidence_status"] = "qualified_annual_comparison"
    joined.loc[comparable & joined.eia923_qualified_mwh.le(0), "benchmark_evidence_status"] = "nonpositive_net_generation"
    joined["validated_hourly_calibration"] = False
    joined["interpretation"]="Descriptive benchmark, not calibrated model accuracy; incomplete EIA-923 rows and BA boundary mismatches limit inference"
    return joined.sort_values(["ba_code","tech"])


def summarize_comparison(joined):
    """BA-level descriptive coverage, never an hourly model-accuracy score."""
    required = {"ba_code", "comparison_status", "benchmark_evidence_status",
                "eia923_qualified_mwh", "pypsa_dispatch_mwh"}
    if required - set(joined):
        raise ValueError("Annual comparison columns missing")
    rows = []
    for ba, part in joined.groupby("ba_code", dropna=False):
        comparable = part.comparison_status.eq("both_sources")
        qualified = part.benchmark_evidence_status.eq("qualified_annual_comparison")
        rows.append({
            "ba_code": ba,
            "technology_rows": int(len(part)),
            "matched_technology_rows": int(comparable.sum()),
            "qualified_annual_comparison_rows": int(qualified.sum()),
            "observed_only_rows": int(part.comparison_status.eq("observed_only").sum()),
            "model_only_rows": int(part.comparison_status.eq("model_only").sum()),
            "partial_coverage_rows": int(part.benchmark_evidence_status.eq("partial_source_coverage").sum()),
            "nonpositive_generation_rows": int(part.benchmark_evidence_status.eq("nonpositive_net_generation").sum()),
            "matched_qualified_eia923_mwh": float(part.loc[qualified, "eia923_qualified_mwh"].sum()),
            "matched_pypsa_mwh": float(part.loc[qualified, "pypsa_dispatch_mwh"].sum()),
            "validated_hourly_calibration": False,
        })
    return pd.DataFrame(rows, columns=[
        "ba_code", "technology_rows", "matched_technology_rows",
        "qualified_annual_comparison_rows", "observed_only_rows",
        "model_only_rows", "partial_coverage_rows",
        "nonpositive_generation_rows", "matched_qualified_eia923_mwh",
        "matched_pypsa_mwh", "validated_hourly_calibration",
    ])


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--qualification",type=Path,required=True)
    p.add_argument("--network",type=Path,required=True)
    p.add_argument("--output",type=Path,default=Path("outputs/ba_calibration"))
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    import pypsa
    network=pypsa.Network(a.network)
    joined=compare(pd.read_csv(a.qualification),network)
    joined.to_csv(a.output/"eia923_vs_pypsa_2024.csv",index=False)
    summarize_comparison(joined).to_csv(a.output/"ba_comparison_coverage_2024.csv", index=False)
    manifest={"period":2024,"observed":"EIA-923 Page 1 annual qualified BA/fuel rows",
      "model":"2024 two-BA representative-hour PyPSA dispatch with assumed costs and availability",
      "limits":["EIA-923 reported BA may include plant reporting boundaries different from EIA-930 balancing operations.",
                "EIA-923 unqualified annual rows withheld; resulting sum is a subset, not full observed BA output.",
                "No numeric model accuracy metric should be interpreted as validated until reporting boundaries and excluded fuel groups are reconciled."]}
    (a.output/"comparison_provenance.json").write_text(json.dumps(manifest,indent=2))
    print(joined[["ba_code","tech","comparison_status","eia923_qualified_mwh","pypsa_dispatch_mwh"]].to_string(index=False))
if __name__=="__main__":main()
