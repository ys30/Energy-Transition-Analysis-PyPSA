"""Audit annual EIA-923 generation against PyPSA modelled generation.

Input is an explicitly normalized plant-month EIA-923 CSV. EIA-923 data are
plant-level, not BA-level: an independently documented same-year plant-to-BA
crosswalk is mandatory. No state-to-BA inference or annual-hourly conflation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def compare_generation(
    eia923: pd.DataFrame,
    crosswalk: pd.DataFrame,
    model_metrics: dict,
    *,
    year: int,
    bas: tuple[str, ...],
    min_mapped_generation_fraction: float = 0.95,
):
    """Compare annual observed EIA-923 net generation (MWh) with modeled MWh.

    Normalized EIA-923 fields: plant_id, report_year, month (1-12),
    fuel, net_generation_mwh. Crosswalk: plant_id, ba_code, mapping_year.
    Fuel codes must be harmonized before comparing carriers.
    """
    needed = {"plant_id", "report_year", "month", "fuel", "net_generation_mwh"}
    needed_x = {"plant_id", "ba_code", "mapping_year"}
    if needed - set(eia923):
        raise ValueError(f"Missing EIA-923 columns: {sorted(needed - set(eia923))}")
    if needed_x - set(crosswalk):
        raise ValueError(f"Missing crosswalk columns: {sorted(needed_x - set(crosswalk))}")
    if not bas or len(bas) != len(set(bas)):
        raise ValueError("BA subset must be nonempty and unique")
    observed, x = eia923.copy(), crosswalk.copy()
    for d in (observed, x):
        d["plant_id"] = d.plant_id.astype("string").str.strip().str.replace(r"\.0$", "", regex=True)
    observed["report_year"] = pd.to_numeric(observed.report_year, errors="raise")
    observed["month"] = pd.to_numeric(observed.month, errors="raise")
    x["mapping_year"] = pd.to_numeric(x.mapping_year, errors="raise")
    if observed.empty or x.empty:
        raise ValueError("EIA-923 observations and crosswalk must not be empty")
    if not observed.report_year.eq(year).all() or not x.mapping_year.eq(year).all():
        raise ValueError("EIA-923 generation and BA crosswalk must match analysis year")
    if not observed.month.between(1, 12).all():
        raise ValueError("Invalid EIA-923 month")
    if observed.plant_id.isna().any() or observed.plant_id.eq("").fillna(True).any():
        raise ValueError("EIA-923 missing plant IDs")
    if x.plant_id.isna().any() or x.plant_id.eq("").fillna(True).any():
        raise ValueError("Crosswalk missing plant IDs")
    if x.duplicated("plant_id").any():
        raise ValueError("Ambiguous duplicate plant-to-BA assignments")
    if x.ba_code.isna().any() or x.ba_code.eq("").fillna(True).any():
        raise ValueError("Crosswalk contains missing BA")
    if observed.fuel.isna().any():
        raise ValueError("Missing EIA-923 fuel")
    if observed.duplicated(["plant_id", "report_year", "month", "fuel"]).any():
        raise ValueError("Duplicate normalized EIA-923 plant-month-fuel rows")
    observed["net_generation_mwh"] = pd.to_numeric(observed.net_generation_mwh, errors="raise")
    if not observed.net_generation_mwh.map(lambda v: bool(pd.notna(v) and abs(v) != float("inf"))).all():
        raise ValueError("Invalid EIA-923 generation")
    # Negative EIA-923 net generation can occur (e.g., station service).
    # Preserve it rather than clipping to zero or changing its sign.
    joined = observed.merge(x[["plant_id", "ba_code"]], how="left",
                            on="plant_id", validate="many_to_one", indicator=True)
    target = joined.loc[joined.ba_code.isin(bas)].copy()
    if target.empty:
        raise ValueError("No EIA-923 plant generation mapped to selected BAs")
    mapped = target.loc[target._merge.eq("both")].copy()
    # The national EIA-923 file necessarily contains plants outside the
    # western EIA-860 crosswalk. Do not treat them as BA mapping failures,
    # but do not claim full selected-BA coverage either: their BA is unknown.
    # Explicitly report unmapped national generation as an unresolved pool.
    unmapped = joined.loc[joined._merge.eq("left_only")]
    unmapped_abs = float(unmapped.net_generation_mwh.abs().sum())
    mapped_abs = float(joined.loc[joined._merge.eq("both"), "net_generation_mwh"].abs().sum())
    coverage = mapped_abs / (mapped_abs + unmapped_abs) if mapped_abs + unmapped_abs else 0
    # This is a national plant-ID match rate, NOT BA-specific coverage.
    # It cannot be used to certify the completeness of selected BA totals.
    observed_by_fuel = mapped.groupby("fuel").net_generation_mwh.sum().to_dict()
    modeled = model_metrics.get("dispatch_mwh_by_carrier")
    if not isinstance(modeled, dict) or not modeled:
        raise ValueError("Missing model dispatch_mwh_by_carrier")
    # EIA-923 primary fuel codes are not the same as PyPSA carrier labels.
    # The caller must normalize fuel to the model's carrier names.
    # Retain observed-only fuels in the audit, but never compare them with
    # a fictitious zero-MWh PyPSA carrier.
    observed_only = {k: float(v) for k, v in observed_by_fuel.items()
                     if k not in modeled}
    comparable = sorted(set(observed_by_fuel) & set(modeled))
    if not comparable:
        raise ValueError("No common observed/model carriers; cannot validate generation")
    rows = []
    for carrier in comparable:
        obs = float(observed_by_fuel.get(carrier, 0))
        pred = float(modeled.get(carrier, 0))
        rows.append({
            "year": year, "carrier": carrier,
            "observed_eia923_net_generation_mwh": obs,
            "modeled_pypsa_dispatch_mwh": pred,
            "model_minus_observed_mwh": pred - obs,
            "relative_error_if_nonzero": (pred - obs) / abs(obs) if obs else None,
        })
    audit = {
        "year": year, "bas": list(bas),
        "observed_source": "EIA-923 plant-month net generation, normalized",
        "crosswalk_source": "same-year EIA-860 reported plant BA code",
        "national_plant_id_match_fraction_abs_not_ba_coverage": coverage,
        "unmapped_national_generation_abs_mwh": unmapped_abs,
        "unmapped_national_plant_count": int(unmapped.plant_id.nunique()),
        "selected_ba_completeness": "unverified; unmapped national plants may include selected BAs",
        "negative_net_generation_rows": int(observed.net_generation_mwh.lt(0).sum()),
        "observed_only_fuels_excluded_from_comparison_mwh": observed_only,
        "observed_only_fuels_net_generation_mwh": float(sum(observed_only.values())),
        "modeled_only_carriers_not_comparable": sorted(set(modeled) - set(observed_by_fuel)),
        "comparison_carriers": comparable,
        "comparison_scope": "Only fuel categories common to both datasets; omitted fuels are not modeled as zero.",
        "interpretation": "Diagnostic comparison only; no parameter fitting or hourly validation.",
    }
    return pd.DataFrame(rows), audit


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--eia923", type=Path, required=True)
    p.add_argument("--crosswalk", type=Path, required=True)
    p.add_argument("--metrics", type=Path, required=True)
    p.add_argument("--year", type=int, required=True)
    p.add_argument("--bas", nargs="+", required=True)
    p.add_argument("--output", type=Path, default=Path("outputs/eia923_validation"))
    a = p.parse_args()
    eia = pd.read_csv(a.eia923, dtype={"plant_id": "string"})
    x = pd.read_csv(a.crosswalk, dtype={"plant_id": "string"})
    # The EIA-860 extractor publishes plant_id/ba_code without a year column.
    # The year is supplied by the verified year-specific filename, not guessed.
    if "mapping_year" not in x:
        expected_name = f"plant_ba_crosswalk_{a.year}.csv"
        if a.crosswalk.name != expected_name:
            raise ValueError(
                f"Yearless BA crosswalk requires official extractor filename {expected_name}"
            )
        x["mapping_year"] = a.year
    metrics = json.loads(a.metrics.read_text())
    comparison, audit = compare_generation(eia, x, metrics, year=a.year, bas=tuple(a.bas))
    a.output.mkdir(parents=True, exist_ok=True)
    comparison.to_csv(a.output / f"eia923_vs_pypsa_{a.year}.csv", index=False)
    (a.output / f"eia923_validation_manifest_{a.year}.json").write_text(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
