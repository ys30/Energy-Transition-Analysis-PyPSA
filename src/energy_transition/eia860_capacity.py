"""Download official EIA-860 annual generator inventory and audit regional capacity.

Input: EIA-860 official annual ZIP. This inventory is NOT hourly dispatch, and state
capacity must not be substituted for balancing authority capacity without a crosswalk.
"""
import argparse
import io
import json
from pathlib import Path
import urllib.request
import zipfile

import pandas as pd

URL = "https://www.eia.gov/electricity/data/eia860/archive/xls/eia860{year}.zip"
WESTERN_STATES = {"AZ", "CA", "CO", "ID", "MT", "NV", "NM", "OR", "UT", "WA", "WY"}
# Kansas, Nebraska, Texas, the Dakotas and other border states have partial WECC footprints;
# avoid including them wholesale without verified plant/grid mapping.


def read_operable_inventory(archive: bytes, year: int):
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        books = [n for n in z.namelist() if n.lower().endswith((".xlsx", ".xls"))]
        gen = [n for n in books if "3_1_generator" in n.lower() or "generator" in Path(n).name.lower()]
        if not gen:
            raise ValueError(f"Generator workbook not found. Members: {books[:30]}")
        with z.open(gen[0]) as f:
            excel = pd.ExcelFile(io.BytesIO(f.read()))
        if "Operable" not in excel.sheet_names:
            raise ValueError(f"Operable sheet not found: {excel.sheet_names}")
        # EIA-860 commonly includes one description row above actual field headers.
        candidate = None
        for header in [1, 0, 2]:
            df = pd.read_excel(excel, "Operable", header=header)
            normalized = {str(c).strip().lower(): c for c in df.columns}
            if "state" in normalized and any("nameplate capacity" in k for k in normalized):
                candidate = df
                break
        if candidate is None:
            raise ValueError("Unrecognized generator layout; manual schema audit required")
    columns = {str(c).strip().lower(): c for c in candidate.columns}
    state_col = columns["state"]
    nameplate = next(v for k,v in columns.items() if "nameplate capacity" in k)
    fuel_col = next((v for k,v in columns.items() if "energy source 1" in k or "energy source 1" == k), None)
    if fuel_col is None:
        raise ValueError("Primary fuel column not identified; cannot map technologies")
    status_col = next((v for k,v in columns.items() if k in ("status", "operational status")), None)
    plant_col = next((v for k,v in columns.items() if k in ("plant code", "plant id", "plant id number")), None)
    gen_col = next((v for k,v in columns.items() if k in ("generator id", "generator id number")), None)
    id_columns = ([plant_col] if plant_col else []) + ([gen_col] if gen_col else [])
    result = candidate[id_columns + [state_col, fuel_col, nameplate] + ([status_col] if status_col else [])].copy()
    result.columns = (["plant_id"] if plant_col else []) + (["generator_id"] if gen_col else []) + ["state", "fuel", "capacity_mw"] + (["status"] if status_col else [])
    if "plant_id" not in result or "generator_id" not in result:
        raise ValueError("Plant and generator identifiers must be retained for BA crosswalk; inspect EIA-860 workbook schema")
    if result[["plant_id", "generator_id"]].isna().any().any():
        raise ValueError("Missing plant or generator identifiers; cannot safely create geographic crosswalk")
    result["capacity_mw"] = pd.to_numeric(result.capacity_mw, errors="coerce")
    result["state"] = result.state.astype(str).str.strip().str.upper()
    result["fuel"] = result.fuel.astype(str).str.strip()
    # Retain anomalous raw rows for audit; never count unknown nameplate as zero.
    result["capacity_qc"] = "valid"
    result.loc[result.capacity_mw.isna(), "capacity_qc"] = "missing_or_nonnumeric"
    result.loc[result.capacity_mw < 0, "capacity_qc"] = "negative"
    return result.assign(report_year=year)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, default=2024)
    parser.add_argument("--output", type=Path, default=Path("outputs/eia860"))
    parser.add_argument("--local-zip", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    url = URL.format(year=args.year)
    if args.local_zip:
        raw = args.local_zip.read_bytes()
    else:
        req = urllib.request.Request(url, headers={"User-Agent": "energy-transition-research/0.2"})
        with urllib.request.urlopen(req, timeout=90) as response:
            raw = response.read()
    df = read_operable_inventory(raw, args.year)
    western = df.loc[df.state.isin(WESTERN_STATES)].copy()
    if western.empty:
        raise ValueError("No selected Western-state operable generator rows")
    western.to_csv(args.output / f"western_state_generators_raw_{args.year}.csv", index=False)
    anomalies = western.loc[western.capacity_qc.ne("valid")].copy()
    anomalies.to_csv(args.output / f"western_capacity_anomalies_{args.year}.csv", index=False)
    valid = western.loc[western.capacity_qc.eq("valid")].copy()
    if valid.empty:
        raise ValueError("No valid Western nameplate capacity rows")
    valid.to_csv(args.output / f"western_state_generators_{args.year}.csv", index=False)
    grouped = valid.groupby(["state", "fuel"], as_index=False).agg(
        generator_count=("capacity_mw", "size"), nameplate_mw=("capacity_mw", "sum"))
    grouped.to_csv(args.output / f"western_state_capacity_{args.year}.csv", index=False)
    manifest = {
        "source": url, "reported_year": args.year, "metric": "nameplate MW",
        "geography": "selected Western states, NOT WECC and NOT EIA-930 balancing authorities",
        "western_states": sorted(WESTERN_STATES),
        "capacity_mw_total_valid_rows_only": float(valid.capacity_mw.sum()),
        "raw_rows": int(len(western)), "valid_rows": int(len(valid)),
        "excluded_missing_or_negative_capacity_rows": int(len(anomalies)),
        "capacity_completeness_fraction": float(len(valid) / len(western)),
        "limitations": "Operable inventory includes standby/out-of-service categories; does not imply available capacity. EIA-930 BA load cannot be matched directly to state-based capacity. No claim of dispatch calibration."
    }
    (args.output / "provenance.json").write_text(json.dumps(manifest, indent=2))
    print(json.dumps({"rows": len(western), **manifest}, indent=2))


if __name__ == "__main__":
    main()
