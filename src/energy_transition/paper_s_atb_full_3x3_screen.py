"""Paper S: complete authenticated 3x3 duration-value × ATB2025 v2 hurdle screen.

The 1,080 already-solved 4-to-8h duration pairs are reused; no LPs rerun.
A threshold crossing is illustrative avoided-variable-cost screening, NOT
market profitability. Model variable costs lack verified 2023-dollar parity.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from energy_transition.paper_s_atb2025_v2_verified_results import (
    EXPECTED_SHA, VARIANTS,
)
from energy_transition.paper_s_atb_2030_storage_extension_cost import compute_costs
from energy_transition.paper_s_siting_design_grid_3x3_2880lp import (
    RATIOS, WIND_SHARES, WEATHER_YEARS, STATES, DESIGNS,
)

CASE_KEYS = ["weather_year", "state", "county_weight_scheme",
             "renewable_peak_ratio", "wind_share_ac"]
HURDLE_KEYS = ["source_variant", "scenario", "real_discount_rate"]


def screen(source_cells: pd.DataFrame, values: pd.DataFrame):
    required_source = {"source_variant", "source_sha256", "scenario",
                       "duration_h", "source_capex_cell", "source_fom_cell"}
    if not required_source.issubset(source_cells.columns):
        raise ValueError("Missing pinned ATB source cell provenance")
    if len(source_cells) != 12 or not source_cells.source_sha256.eq(EXPECTED_SHA).all():
        raise ValueError("ATB workbook source mismatch")
    if source_cells.duplicated(["source_variant", "scenario", "duration_h"]).any():
        raise ValueError("Duplicate ATB source cell")
    if set(source_cells.source_variant) != set(VARIANTS):
        raise ValueError("Missing ATB variants")
    costs = []
    for variant in VARIANTS:
        x = source_cells[source_cells.source_variant.eq(variant)]
        if len(x) != 6:
            raise ValueError("Incomplete ATB cost variant")
        for _, r in x.iterrows():
            prefix = "'Utility-Scale Battery - " + variant + "'!O"
            if not str(r.source_capex_cell).startswith(prefix) or not str(r.source_fom_cell).startswith(prefix):
                raise ValueError("ATB source cell mismatch")
        c = compute_costs(x, rates=(.04, .07, .10), lifetime_years=15)
        c["source_variant"] = variant
        costs.append(c)
    hurdles = pd.concat(costs, ignore_index=True)
    if len(hurdles) != 18 or hurdles[HURDLE_KEYS].duplicated().any():
        raise ValueError("Expected 18 unique ATB assumption records")
    target = "marginal_4to8_usd_added_kwh_year"
    if not set(CASE_KEYS + [target, "added_storage_kwh"]).issubset(values.columns):
        raise ValueError("Missing original 3x3 duration value fields")
    x = values.copy()
    if len(x) != 1080 or x[CASE_KEYS].duplicated().any():
        raise ValueError("Expected 1080 unique source duration cases")
    if not np.isfinite(x[[target, "added_storage_kwh"]].to_numpy(dtype=float)).all():
        raise ValueError("Nonfinite values")
    if (x.added_storage_kwh <= 0).any():
        raise ValueError("Nonpositive added energy")
    actual = pd.MultiIndex.from_frame(x[CASE_KEYS])
    expected = pd.MultiIndex.from_product(
        [WEATHER_YEARS, STATES, DESIGNS, RATIOS, WIND_SHARES], names=CASE_KEYS
    )
    if len(actual.difference(expected)) or len(expected.difference(actual)):
        raise ValueError("Incomplete 15-year 3x3 grid")
    x["operating_value_usd_added_kwh_year"] = x[target]
    cases = x.merge(hurdles, how="cross")
    cases["illustrative_value_minus_hurdle_usd_kwh_year"] = (
        cases.operating_value_usd_added_kwh_year -
        cases.annualized_extension_hurdle_usd_kwh_year
    )
    cases["meets_hurdle"] = cases.illustrative_value_minus_hurdle_usd_kwh_year.ge(-1e-10)
    cases["cash_flow_or_market_profit_established"] = False
    if len(cases) != 19440:
        raise ValueError("Expected precisely 19440 comparisons")
    grouped = HURDLE_KEYS + ["state", "county_weight_scheme",
                              "renewable_peak_ratio", "wind_share_ac"]
    detail = (cases.groupby(grouped, as_index=False)
              .agg(n_weather_years=("meets_hurdle", "size"),
                   n_meeting_hurdle=("meets_hurdle", "sum"),
                   median_value=("operating_value_usd_added_kwh_year", "median"),
                   min_value=("operating_value_usd_added_kwh_year", "min"),
                   max_value=("operating_value_usd_added_kwh_year", "max"),
                   hurdle=("annualized_extension_hurdle_usd_kwh_year", "first")))
    if len(detail) != 1296 or not detail.n_weather_years.eq(15).all():
        raise ValueError("Expected 18 x 4 x 2 x 9 summary cells with 15 years")
    overview = (cases.groupby(HURDLE_KEYS, as_index=False)
                .agg(total_cases=("meets_hurdle", "size"),
                     meeting_hurdle=("meets_hurdle", "sum"),
                     max_value=("operating_value_usd_added_kwh_year", "max"),
                     threshold=("annualized_extension_hurdle_usd_kwh_year", "first")))
    if len(overview) != 18 or not overview.total_cases.eq(1080).all():
        raise ValueError("18 full-grid comparisons required")
    baseline = cases[cases.renewable_peak_ratio.eq(1.5) & cases.wind_share_ac.eq(.5)]
    if len(baseline) != 2160:
        raise ValueError("Expected 120 fixed-2030 design baseline cases per ATB hurdle")
    return hurdles, cases, detail, overview


def run(source_cells, values, output):
    hurdles, cases, detail, overview = screen(source_cells, values)
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    for name, frame in [
        ("paper_s_3x3_atb_18_source_hurdles.csv", hurdles),
        ("paper_s_3x3_atb_19440_comparisons.csv.gz", cases),
        ("paper_s_3x3_atb_1296_state_design_threshold_summary.csv", detail),
        ("paper_s_3x3_atb_18_assumption_summary.csv", overview),
    ]:
        frame.to_csv(out / name, index=False,
                     compression="gzip" if name.endswith(".gz") else None)
    manifest = {
        "status": "CALCULATED_FROM_FROZEN_SOURCE_GRID_NOT_NEW_LP",
        "source_weather_years": 15, "states": 4, "siting_schemes": 2,
        "renewable_design_points": 9, "unique_4to8_lp_value_cases": 1080,
        "atb_annual_cost_assumptions": 18, "comparison_rows": 19440,
        "fixed_2030_baseline_comparison_rows": 2160,
        "fixed_2030_baseline_threshold_crossings": int(cases.loc[
            cases.renewable_peak_ratio.eq(1.5) & cases.wind_share_ac.eq(.5),
            "meets_hurdle"].sum()),
        "historical_load_0_of_120_not_same_LP_population": True,
        "total_full_grid_threshold_crossings": int(cases.meets_hurdle.sum()),
        "unique_numeric_cost_hurdles": int(hurdles.annualized_extension_hurdle_usd_kwh_year.round(9).nunique()),
        "lp_values_dollar_basis_verified_to_2023": False,
        "cash_flow_or_profit_established": False,
        "no_recalculation_of_frozen_lp": True,
        "cost_assumptions_not_independent_samples": True,
    }
    (out / "paper_s_3x3_atb_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n")
    return manifest


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source-cells", required=True, type=Path)
    p.add_argument("--duration-values", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    print(json.dumps(run(pd.read_csv(a.source_cells),
                         pd.read_csv(a.duration_values), a.out), indent=2))


if __name__ == "__main__":
    main()
