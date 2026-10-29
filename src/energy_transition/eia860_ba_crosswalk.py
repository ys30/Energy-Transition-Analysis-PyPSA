"""Join audited EIA-860 generator records to an explicit plant-to-BA crosswalk.

No state-to-BA inference is permitted. The analyst-supplied mapping must
document its source and year, and unmapped plants are reported, not silently
assigned to a neighboring balancing authority.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

FUEL_GROUPS = {
    "NG": "gas", "WND": "wind", "SUN": "solar", "WAT": "hydro",
    "NUC": "nuclear", "BIT": "coal", "SUB": "coal", "LIG": "coal",
    "DFO": "oil", "RFO": "oil", "GEO": "geothermal",
}


def map_generators_to_bas(
    generators: pd.DataFrame,
    crosswalk: pd.DataFrame,
    year: int,
    bas: tuple[str, ...],
    *,
    min_mapped_capacity_fraction: float = 0.95,
):
    """Return BA-fuel capacity, unmatched generators, and a QC manifest.

    Generators: plant_id, generator_id, capacity_mw, fuel, report_year,
    optional status and id_qc/capacity_qc.
    Crosswalk: plant_id, balancing_authority, mapping_year, source.
    Crosswalk mappings are year-specific; never extrapolate across years.
    """
    required_g = {"plant_id", "generator_id", "capacity_mw", "fuel", "report_year"}
    required_x = {"plant_id", "balancing_authority", "mapping_year", "source"}
    if required_g - set(generators.columns):
        raise ValueError(f"Missing generator columns: {sorted(required_g-set(generators.columns))}")
    if required_x - set(crosswalk.columns):
        raise ValueError(f"Missing crosswalk columns: {sorted(required_x-set(crosswalk.columns))}")
    if not bas or len(bas) != len(set(bas)):
        raise ValueError("BA list must be nonempty and unique")
    g, x = generators.copy(), crosswalk.copy()
    for frame in (g, x):
        frame["plant_id"] = frame["plant_id"].astype("string").str.strip().str.replace(r"\.0$", "", regex=True)
    g["generator_id"] = g.generator_id.astype("string").str.strip()
    if g[["plant_id", "generator_id"]].isna().any().any():
        raise ValueError("Generator IDs missing")
    if g.duplicated(["plant_id", "generator_id"]).any():
        raise ValueError("Duplicate generator IDs")
    g["report_year"] = pd.to_numeric(g.report_year, errors="raise")
    x["mapping_year"] = pd.to_numeric(x.mapping_year, errors="raise")
    if not g.report_year.eq(year).all() or not x.mapping_year.eq(year).all():
        raise ValueError("Crosswalk and generator report years must match exactly")
    if x.plant_id.isna().any() or x.plant_id.eq("").fillna(True).any():
        raise ValueError("Crosswalk contains empty plant IDs")
    if x.duplicated("plant_id").any():
        raise ValueError("Ambiguous plant-to-BA mapping: duplicate plant IDs")
    if x.balancing_authority.isna().any() or x.source.isna().any():
        raise ValueError("Missing crosswalk BA or source provenance")
    if x.source.astype("string").str.strip().eq("").fillna(True).any():
        raise ValueError("Blank crosswalk source provenance")
    if not x.balancing_authority.isin(bas).all():
        raise ValueError("Crosswalk contains BAs outside the explicitly requested subset")
    g["capacity_mw"] = pd.to_numeric(g.capacity_mw, errors="raise")
    if g.capacity_mw.isna().any() or (g.capacity_mw < 0).any():
        raise ValueError("Invalid generator capacity")
    if "status" in g:
        g = g.loc[g.status.astype("string").str.strip().str.upper().eq("OP")].copy()
    for flag in ("id_qc", "capacity_qc"):
        if flag in g and not g[flag].eq("valid").all():
            raise ValueError(f"Input contains invalid {flag} rows; clean and audit first")
    if g.empty:
        raise ValueError("No valid operating generators")
    joined = g.merge(x, on="plant_id", how="left", validate="many_to_one", indicator=True)
    matched = joined.loc[joined._merge.eq("both")].copy()
    unmatched = joined.loc[joined._merge.ne("both")].copy()
    total_mw = float(joined.capacity_mw.sum())
    matched_mw = float(matched.capacity_mw.sum())
    fraction = matched_mw / total_mw if total_mw else 0.0
    if fraction < min_mapped_capacity_fraction:
        raise ValueError(
            f"BA mapping coverage {fraction:.2%} below {min_mapped_capacity_fraction:.2%}; "
            f"unmapped capacity={total_mw-matched_mw:.2f} MW"
        )
    matched["technology"] = matched.fuel.map(FUEL_GROUPS).fillna("other")
    grouped = matched.groupby(["balancing_authority", "technology"], as_index=False).agg(
        nameplate_mw=("capacity_mw", "sum"), generator_count=("generator_id", "size")
    )
    audit = {
        "year": year,
        "requested_bas": list(bas),
        "mapping_method": "explicit year-specific plant crosswalk; no state inference",
        "generator_rows": len(joined),
        "mapped_generator_rows": len(matched),
        "unmapped_generator_rows": len(unmatched),
        "total_operating_nameplate_mw": total_mw,
        "mapped_nameplate_mw": matched_mw,
        "mapped_capacity_fraction": fraction,
        "threshold": min_mapped_capacity_fraction,
        "evidence_boundary": "nameplate MW, not dependable capacity or observed dispatch",
    }
    return grouped, unmatched, audit


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--generators", type=Path, required=True)
    p.add_argument("--crosswalk", type=Path, required=True)
    p.add_argument("--year", type=int, required=True)
    p.add_argument("--bas", nargs="+", required=True)
    p.add_argument("--output", type=Path, default=Path("outputs/eia860_ba"))
    args = p.parse_args()
    g = pd.read_csv(args.generators, dtype={"plant_id": str, "generator_id": str})
    x = pd.read_csv(args.crosswalk, dtype={"plant_id": str})
    grouped, unmatched, audit = map_generators_to_bas(g, x, args.year, tuple(args.bas))
    args.output.mkdir(parents=True, exist_ok=True)
    grouped.to_csv(args.output / f"ba_operating_nameplate_{args.year}.csv", index=False)
    unmatched.to_csv(args.output / f"unmapped_generators_{args.year}.csv", index=False)
    (args.output / f"ba_crosswalk_audit_{args.year}.json").write_text(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
