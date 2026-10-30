"""Normalize the official EIA-923 monthly generation-and-fuel workbook.

Uses Schedule 3 monthly generation columns (Netgen January...December).
Source must be a user-supplied official EIA-923 XLSX; no fabricated observations.
Unknown energy-source codes are rejected, not silently discarded.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
import pandas as pd

FUEL = {
    "NG": "gas", "BFG": "gas", "OG": "gas",
    "WND": "wind", "SUN": "solar", "WAT": "hydro", "NUC": "nuclear",
    "BIT": "coal", "SUB": "coal", "LIG": "coal", "WC": "coal",
    "DFO": "oil", "RFO": "oil", "JF": "oil", "KER": "oil",
    "GEO": "geothermal",
    # Additional EIA-reported sources are preserved as separately labeled
    # categories. These are observational categories, not modeled PyPSA fuels.
    "AB": "biomass", "BLQ": "biomass", "LFG": "biomass",
    "MSB": "biomass", "MSN": "waste", "OBG": "biomass",
    "OBL": "biomass", "OBS": "biomass", "SLW": "waste",
    "WDL": "biomass", "WDS": "biomass",
    "PC": "coal", "RC": "coal", "SGC": "coal",
    "PG": "oil", "PUR": "oil", "TDF": "waste",
    "WH": "other", "WO": "oil", "OTH": "other",
    "MWH": "storage",
}
MONTHS = ["january", "february", "march", "april", "may", "june",
          "july", "august", "september", "october", "november", "december"]


def normalize_schedule3(frame: pd.DataFrame, year: int, *, allow_incomplete=False):
    cols = {re.sub(r"\s+", " ", str(c)).strip().lower(): c for c in frame.columns}
    plant = next((v for k, v in cols.items() if k in ("plant id", "plant code", "plant id number")), None)
    fuel = next((v for k, v in cols.items() if ("reported fuel type code" in k or k == "energy source")), None)
    if not plant or not fuel:
        raise ValueError("Cannot identify official EIA-923 Plant Id and Reported Fuel Type Code")
    month_columns = {}
    for month in MONTHS:
        matches = [v for k, v in cols.items()
                   if k.startswith("netgen") and month in k]
        if len(matches) != 1:
            raise ValueError(f"Missing or ambiguous EIA-923 Netgen {month} column")
        month_columns[month] = matches[0]
    wide = frame[[plant, fuel, *month_columns.values()]].copy()
    wide.columns = ["plant_id", "fuel_code", *MONTHS]
    wide["plant_id"] = wide.plant_id.astype("string").str.strip().str.replace(r"\.0$", "", regex=True)
    wide["fuel_code"] = wide.fuel_code.astype("string").str.strip().str.upper()
    wide = wide.loc[wide.plant_id.notna() & wide.plant_id.ne("")].copy()
    if wide.empty:
        raise ValueError("No EIA-923 plant records")
    wide["source_row_id"] = range(len(wide))
    long = wide.melt(id_vars=["source_row_id", "plant_id", "fuel_code"], value_vars=MONTHS,
                     var_name="month_name", value_name="net_generation_mwh")
    long["month"] = long.month_name.map({m: i + 1 for i, m in enumerate(MONTHS)})
    long["fuel"] = long.fuel_code.map(FUEL)
    raw = long.net_generation_mwh.astype("string").str.strip()
    # Official spreadsheets can contain "." or other nondisclosure codes.
    # Preserve an audit; never reinterpret such cells as zero.
    numeric = pd.to_numeric(raw, errors="coerce")
    invalid = raw.notna() & raw.ne("") & numeric.isna()
    if invalid.any() and not allow_incomplete:
        tokens = raw.loc[invalid].value_counts().head(20).to_dict()
        examples = long.loc[invalid, ["plant_id", "fuel_code", "month_name"]].head(15).copy()
        examples["raw_value"] = raw.loc[invalid].head(15).tolist()
        raise ValueError(
            f"Non-numeric EIA-923 Netgen cells: {int(invalid.sum())}; "
            f"top tokens: {tokens}; examples: {examples.to_dict(orient='records')}"
        )
    unknown = long.fuel.isna() & numeric.notna() & numeric.ne(0)
    if unknown.any() and not allow_incomplete:
        codes = sorted(long.loc[unknown, "fuel_code"].dropna().unique())
        raise ValueError(f"Unmapped EIA-923 fuel codes with generation: {codes}")
    long["net_generation_mwh"] = numeric
    if allow_incomplete:
        long.attrs["unmapped_fuel_cells"] = long.loc[long.fuel.isna(),
            ["source_row_id", "plant_id", "fuel_code", "month", "net_generation_mwh"]].copy()
    # Missing monthly values are not zeros. Reject incomplete nonempty
    # plant/fuel records rather than biasing annual totals downward.
    missing = long.net_generation_mwh.isna()
    if missing.any() and not allow_incomplete:
        raise ValueError(f"Missing EIA-923 monthly net generation: {int(missing.sum())} cells")
    if allow_incomplete:
        # Preserve missing-cell tokens and every numeric month discarded with
        # an incomplete source row; downstream annual totals are partial.
        excluded_audit = long.loc[missing, ["source_row_id", "plant_id", "fuel_code", "month", "net_generation_mwh"]].copy()
        excluded_audit["original_cell_text"] = raw.loc[missing].tolist()
        long.attrs["excluded_cells"] = excluded_audit
        complete_ids = long.groupby("source_row_id").net_generation_mwh.transform(lambda x: x.notna().all())
        dropped_numeric = long.loc[~complete_ids & ~missing,
            ["source_row_id", "plant_id", "fuel_code", "month", "net_generation_mwh"]].copy()
        long.attrs["excluded_numeric_cells"] = dropped_numeric
        long = long.loc[complete_ids].copy()
    excluded_cells = long.attrs.get("excluded_cells")
    unmapped_fuel_cells = long.attrs.get("unmapped_fuel_cells")
    excluded_numeric_cells = long.attrs.get("excluded_numeric_cells")
    long = long.dropna(subset=["fuel"])
    if long.empty:
        raise ValueError("No usable EIA-923 plant-month generation after missing-value and fuel-code exclusions")
    long["report_year"] = year
    result = long[["plant_id", "report_year", "month", "fuel", "net_generation_mwh"]].groupby(
        ["plant_id", "report_year", "month", "fuel"], as_index=False
    ).net_generation_mwh.sum()
    if allow_incomplete:
        result.attrs["excluded_cells"] = excluded_cells
        result.attrs["unmapped_fuel_cells"] = unmapped_fuel_cells
        result.attrs["excluded_numeric_cells"] = excluded_numeric_cells
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--xlsx", type=Path, required=True)
    p.add_argument("--year", type=int, required=True)
    p.add_argument("--sheet", default="Page 1 Generation and Fuel Data")
    p.add_argument("--allow-incomplete", action="store_true", help="Exclude entire incomplete source rows and publish excluded cell audit")
    p.add_argument("--output", type=Path, default=Path("outputs/eia923"))
    a = p.parse_args()
    book = pd.ExcelFile(a.xlsx)
    result = None
    inspected = {}
    selected_sheet = None
    # EIA changes worksheet titles and number of metadata rows between releases.
    sheets = ([a.sheet] if a.sheet in book.sheet_names else []) + [
        name for name in book.sheet_names if name != a.sheet
        and ("generation" in name.lower() or "page 1" in name.lower())
    ]
    if not sheets:
        sheets = list(book.sheet_names)
    for sheet in sheets:
        inspected[sheet] = []
        # EIA workbooks can contain short notes or cover sheets. Read only
        # the first 12 rows once, and never request a header beyond EOF.
        preview = pd.read_excel(book, sheet_name=sheet, header=None, nrows=12)
        for header in range(len(preview)):
            # Inspect headers only; the full EIA-923 sheet is large.
            labels = [str(v).strip() if pd.notna(v) else ""
                      for v in preview.iloc[header].tolist()]
            columns = {re.sub(r"\s+", " ", label).lower() for label in labels}
            inspected[sheet].append({"header_row_zero_based": header,
                                      "first_columns": labels[:30]})
            has_plant = bool(columns & {"plant id", "plant code", "plant id number"})
            has_fuel = any("reported fuel type code" in c or c == "energy source" for c in columns)
            has_netgen = any(c.startswith("netgen") for c in columns)
            if not (has_plant and has_fuel and has_netgen):
                continue
            # Identified header: preserve any subsequent data-quality exception.
            frame = pd.read_excel(book, sheet_name=sheet, header=header)
            result = normalize_schedule3(frame, a.year, allow_incomplete=a.allow_incomplete)
            selected_sheet = sheet
            break
        if result is not None:
            break
    if result is None:
        a.output.mkdir(parents=True, exist_ok=True)
        diagnostic = {"year": a.year, "workbook_sheets": book.sheet_names,
                      "inspected_headers": inspected,
                      "error": "No recognized EIA-923 Schedule 3 header; do not fabricate generation"}
        (a.output / f"eia923_schema_diagnostic_{a.year}.json").write_text(
            json.dumps(diagnostic, indent=2))
        raise ValueError("EIA-923 workbook schema not recognized; "
                         f"see eia923_schema_diagnostic_{a.year}.json")
    a.output.mkdir(parents=True, exist_ok=True)
    excluded = result.attrs.get("excluded_cells")
    unmapped = result.attrs.get("unmapped_fuel_cells")
    excluded_numeric = result.attrs.get("excluded_numeric_cells")
    if a.allow_incomplete:
        excluded.to_csv(a.output / f"eia923_excluded_monthly_cells_{a.year}.csv", index=False)
        unmapped.to_csv(a.output / f"eia923_unmapped_fuel_cells_{a.year}.csv", index=False)
        excluded_numeric.to_csv(a.output / f"eia923_excluded_numeric_cells_{a.year}.csv", index=False)
    result.to_csv(a.output / f"eia923_normalized_{a.year}.csv", index=False)
    (a.output / f"eia923_source_{a.year}.json").write_text(json.dumps({
        "year": a.year, "input_file": a.xlsx.name, "sheet": selected_sheet,
        "observations": len(result), "units": "net generation MWh",
        "strict_source_record_exclusion": a.allow_incomplete,
        "excluded_monthly_cells": len(excluded) if excluded is not None else 0,
        "excluded_source_rows": int(excluded.source_row_id.nunique()) if excluded is not None else 0,
        "excluded_valid_numeric_cells": len(excluded_numeric) if excluded_numeric is not None else 0,
        "excluded_valid_numeric_net_generation_mwh": float(excluded_numeric.net_generation_mwh.sum()) if excluded_numeric is not None else 0,
        "excluded_valid_numeric_abs_generation_mwh": float(excluded_numeric.net_generation_mwh.abs().sum()) if excluded_numeric is not None else 0,
        "unmapped_fuel_cells": len(unmapped) if unmapped is not None else 0,
        "unmapped_fuel_net_generation_mwh": float(unmapped.net_generation_mwh.sum()) if unmapped is not None else 0,
        "unmapped_fuel_abs_generation_mwh": float(unmapped.net_generation_mwh.abs().sum()) if unmapped is not None else 0,
        "included_net_generation_mwh": float(result.net_generation_mwh.sum()),
        "included_abs_generation_mwh": float(result.net_generation_mwh.abs().sum()),
        "coverage_caveat": "Missing-value generation is unknown; exclusion and unmapped-fuel audits can overlap and must not be added without deduplication.",
        "selected_fuel_coverage": "unmapped official source codes withheld and audited; extended observed-only fuel groups do not imply PyPSA carrier support",
        "warning": "Normalized official plant-month data; not automatically verified against EIA-930 BA totals."
    }, indent=2))


if __name__ == "__main__":
    main()
