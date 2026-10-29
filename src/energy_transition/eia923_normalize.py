"""Normalize the official EIA-923 monthly generation-and-fuel workbook.

Uses Schedule 3 monthly generation columns (Netgen January...December).
Source must be a user-supplied official EIA-923 XLSX; no fabricated observations.
Unknown energy-source codes are rejected, not silently discarded.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import pandas as pd

FUEL = {
    "NG": "gas", "BFG": "gas", "OG": "gas",
    "WND": "wind", "SUN": "solar", "WAT": "hydro", "NUC": "nuclear",
    "BIT": "coal", "SUB": "coal", "LIG": "coal", "WC": "coal",
    "DFO": "oil", "RFO": "oil", "JF": "oil", "KER": "oil",
    "GEO": "geothermal",
}
MONTHS = ["january", "february", "march", "april", "may", "june",
          "july", "august", "september", "october", "november", "december"]


def normalize_schedule3(frame: pd.DataFrame, year: int):
    cols = {str(c).strip().lower(): c for c in frame.columns}
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
    long = wide.melt(id_vars=["plant_id", "fuel_code"], value_vars=MONTHS,
                     var_name="month_name", value_name="net_generation_mwh")
    long["month"] = long.month_name.map({m: i + 1 for i, m in enumerate(MONTHS)})
    long["fuel"] = long.fuel_code.map(FUEL)
    raw = long.net_generation_mwh.astype("string").str.strip()
    # Official spreadsheets can contain "." or other nondisclosure codes.
    # Preserve an audit; never reinterpret such cells as zero.
    numeric = pd.to_numeric(raw, errors="coerce")
    invalid = raw.notna() & raw.ne("") & numeric.isna()
    if invalid.any():
        raise ValueError(f"Non-numeric EIA-923 Netgen cells: {int(invalid.sum())}")
    if (long.fuel.isna() & numeric.notna() & numeric.ne(0)).any():
        codes = sorted(long.loc[long.fuel.isna() & numeric.notna() & numeric.ne(0), "fuel_code"].dropna().unique())
        raise ValueError(f"Unmapped EIA-923 fuel codes with generation: {codes}")
    long["net_generation_mwh"] = numeric
    # Missing monthly values are not zeros. Reject incomplete nonempty
    # plant/fuel records rather than biasing annual totals downward.
    missing = long.net_generation_mwh.isna()
    if missing.any():
        raise ValueError(f"Missing EIA-923 monthly net generation: {int(missing.sum())} cells")
    long = long.dropna(subset=["fuel"])
    long["report_year"] = year
    return long[["plant_id", "report_year", "month", "fuel", "net_generation_mwh"]].groupby(
        ["plant_id", "report_year", "month", "fuel"], as_index=False
    ).net_generation_mwh.sum()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--xlsx", type=Path, required=True)
    p.add_argument("--year", type=int, required=True)
    p.add_argument("--sheet", default="Page 1 Generation and Fuel Data")
    p.add_argument("--output", type=Path, default=Path("outputs/eia923"))
    a = p.parse_args()
    book = pd.ExcelFile(a.xlsx)
    result = None
    inspected = {}
    # EIA changes worksheet titles and number of metadata rows between releases.
    sheets = ([a.sheet] if a.sheet in book.sheet_names else []) + [
        name for name in book.sheet_names if name != a.sheet
        and ("generation" in name.lower() or "page 1" in name.lower())
    ]
    if not sheets:
        sheets = list(book.sheet_names)
    for sheet in sheets:
        inspected[sheet] = []
        for header in range(0, 12):
            frame = pd.read_excel(book, sheet_name=sheet, header=header)
            columns = {str(c).strip().lower() for c in frame.columns}
            inspected[sheet].append({"header_row_zero_based": header,
                                      "first_columns": list(map(str, frame.columns[:12]))})
            has_plant = bool(columns & {"plant id", "plant code", "plant id number"})
            has_fuel = any("reported fuel type code" in c or c == "energy source" for c in columns)
            has_netgen = any(c.startswith("netgen") for c in columns)
            if not (has_plant and has_fuel and has_netgen):
                continue
            # Identified header: preserve any subsequent data-quality exception.
            result = normalize_schedule3(frame, a.year)
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
    result.to_csv(a.output / f"eia923_normalized_{a.year}.csv", index=False)
    (a.output / f"eia923_source_{a.year}.json").write_text(json.dumps({
        "year": a.year, "input_file": a.xlsx.name, "sheet": a.sheet,
        "observations": len(result), "units": "net generation MWh",
        "warning": "Normalized official plant-month data; not automatically verified against EIA-930 BA totals."
    }, indent=2))


if __name__ == "__main__":
    main()
