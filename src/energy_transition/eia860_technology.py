"""Reproducible EIA-860 fuel-code crosswalk with explicit unknown-fuel audit.

State inventory does not determine EIA-930 balancing-authority membership.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import pandas as pd

FUEL_TO_TECH = {
    "NG": "gas", "BFG": "gas", "OG": "gas", "PG": "gas", "SG": "gas",
    "BIT": "coal", "SUB": "coal", "LIG": "coal", "RC": "coal", "WC": "coal",
    "NUC": "nuclear", "WAT": "hydro", "WND": "wind",
    "SUN": "solar", "GEO": "geothermal",
    "DFO": "oil", "RFO": "oil", "JF": "oil", "KER": "oil", "PC": "oil", "WO": "oil",
    "AB": "biomass", "MSW": "biomass", "OBG": "biomass", "OBL": "biomass",
    "OBS": "biomass", "WDS": "biomass", "BLQ": "biomass", "LFG": "biomass",
    "WDL": "biomass", "SLW": "biomass",
    "WH": "waste_heat", "OTH": "other_unknown",
    "PUR": "storage", "MWH": "storage",
}
# Some codes have mixed meanings by EIA reporting vintage. Exclude unmapped
# fuels instead of silently attributing their capacity to a modeled technology.
def classify_generators(frame: pd.DataFrame) -> pd.DataFrame:
    required = {"state", "fuel", "capacity_mw"}
    if missing := required - set(frame.columns):
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    d = frame.copy()
    d["fuel"] = d["fuel"].astype(str).str.strip().str.upper()
    d["technology"] = d["fuel"].map(FUEL_TO_TECH)
    d["capacity_mw"] = pd.to_numeric(d["capacity_mw"], errors="coerce")
    d["mapping_status"] = "mapped"
    d.loc[d.technology.isna(), "mapping_status"] = "unmapped_fuel"
    d.loc[d.capacity_mw.isna() | (d.capacity_mw < 0), "mapping_status"] = "invalid_capacity"
    return d

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--year", type=int, default=2024)
    p.add_argument("--input", type=Path)
    p.add_argument("--output", type=Path, default=Path("outputs/eia860"))
    a = p.parse_args()
    source = a.input or a.output / f"western_state_generators_{a.year}.csv"
    df = classify_generators(pd.read_csv(source))
    a.output.mkdir(parents=True, exist_ok=True)
    df.to_csv(a.output / f"technology_mapping_audit_{a.year}.csv", index=False)
    good = df[df.mapping_status.eq("mapped")]
    other = df[~df.mapping_status.eq("mapped")]
    summary = good.groupby(["state", "technology"], as_index=False).agg(
        generators=("capacity_mw", "size"), nameplate_mw=("capacity_mw", "sum"))
    summary.to_csv(a.output / f"western_state_technology_capacity_{a.year}.csv", index=False)
    other.to_csv(a.output / f"unmapped_or_invalid_technology_{a.year}.csv", index=False)
    metrics = {
        "source_file": str(source), "year": a.year,
        "rows_total": len(df), "mapped_rows": len(good),
        "excluded_rows": len(other), "mapped_nameplate_mw": float(good.capacity_mw.sum()),
        "unmapped_fuel_codes": sorted(other.loc[other.mapping_status.eq("unmapped_fuel"), "fuel"].unique().tolist()),
        "boundary": "state-level EIA-860 nameplate capacity only; NOT BA-calibrated capacity or a PyPSA optimization output",
    }
    (a.output / f"technology_mapping_manifest_{a.year}.json").write_text(json.dumps(metrics, indent=2))
    print(json.dumps(metrics, indent=2))
if __name__ == "__main__":
    main()
