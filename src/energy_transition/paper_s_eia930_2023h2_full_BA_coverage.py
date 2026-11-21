"""Observed EIA-930 2023 July–December BA wind/solar hour coverage audit.

This is an *observation-only* archival source inventory: no BA=state,
no imputed-as-measured MW, no candidate nameplate denominator, no modeled CF.
Missing source timestamp rows and blank reported MW are separately tallied.
The archived 2023 H2 source is independently pinned by the original MD5.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

from energy_transition.paper_s_eia930_2023half2_archive_inventory import EXPECTED_MD5
from energy_transition.paper_s_eia930_2023h2_ba_observed_extract import (
    BAS, TECHS, RAW_NAME, TIME_COL, BA_COL,
)

START = pd.Timestamp("2023-07-01T00:00:00Z")
END = pd.Timestamp("2024-01-01T00:00:00Z")
FREQ = "h"
EXPECTED_HOURS = len(pd.date_range(START, END, freq=FREQ, inclusive="left"))


def audited_archive(path: Path) -> str:
    digest = hashlib.md5()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(2**20), b""):
            digest.update(block)
    if digest.hexdigest() != EXPECTED_MD5:
        raise ValueError("2023 H2 EIA-930 raw archive MD5 mismatch")
    return digest.hexdigest()


def extract_observed(archive: Path) -> pd.DataFrame:
    audited_archive(archive)
    all_parts = []
    cols = [BA_COL, TIME_COL]
    for technology in TECHS.values():
        base = f"Net Generation (MW) from {technology}"
        cols.extend([base, f"{base} (Adjusted)", f"{base} (Imputed)"])
    with zipfile.ZipFile(archive) as zipped:
        if RAW_NAME not in zipped.namelist():
            raise ValueError(f"Missing original balance CSV {RAW_NAME}")
        with zipped.open(RAW_NAME) as stream:
            for chunk in pd.read_csv(
                stream, usecols=cols, chunksize=50000, low_memory=False,
                encoding="utf-8-sig",
            ):
                scoped = chunk.loc[chunk[BA_COL].isin(BAS)].copy()
                if scoped.empty:
                    continue
                scoped["utc_hour_end"] = pd.to_datetime(
                    scoped[TIME_COL], format="%m/%d/%Y %I:%M:%S %p", utc=True,
                    errors="raise",
                )
                scoped = scoped.loc[
                    (scoped.utc_hour_end >= START) & (scoped.utc_hour_end < END)
                ]
                if scoped.empty:
                    continue
                for fuel, tech in TECHS.items():
                    base = f"Net Generation (MW) from {tech}"
                    frame = scoped[
                        [BA_COL, "utc_hour_end", base, f"{base} (Adjusted)", f"{base} (Imputed)"]
                    ].copy()
                    frame.columns = [
                        "ba_code", "utc_hour_end", "reported_mw",
                        "adjusted_mw", "imputed_mw",
                    ]
                    frame["fuel"] = fuel
                    for field in ("reported_mw", "adjusted_mw", "imputed_mw"):
                        frame[field] = pd.to_numeric(frame[field], errors="coerce")
                        if np.isinf(frame[field].to_numpy(float)).any():
                            raise ValueError("Infinite source generation MW")
                    all_parts.append(frame)
    if not all_parts:
        raise ValueError("No selected BA observation hours in archived source")
    result = pd.concat(all_parts, ignore_index=True)
    if result.duplicated(["ba_code", "fuel", "utc_hour_end"]).any():
        raise ValueError("Duplicate BA/fuel/UTC hour-ending source rows")
    if result.utc_hour_end.isna().any():
        raise ValueError("Malformed source hour-end UTC")
    if not result.ba_code.isin(BAS).all() or not result.fuel.isin(TECHS).all():
        raise ValueError("Unsupported original BA or fuel")
    return result.sort_values(["ba_code", "fuel", "utc_hour_end"]).reset_index(drop=True)


def coverage(panel: pd.DataFrame):
    expected = pd.date_range(START, END, freq="h", inclusive="left")
    rows, monthly, missing = [], [], []
    for ba in BAS:
        for fuel in TECHS:
            subset = panel.loc[(panel.ba_code == ba) & (panel.fuel == fuel)]
            frame = subset.set_index("utc_hour_end")
            absent = expected.difference(frame.index)
            missing.extend({"ba_code": ba, "fuel": fuel, "utc_hour_end": t.isoformat()}
                           for t in absent)
            present = frame.reindex(expected)
            reported = present.reported_mw
            row_present = expected.isin(frame.index)
            count_present = int(row_present.sum())
            count_missing_values = int(frame.reported_mw.isna().sum())
            rows.append({
                "ba_code": ba, "fuel": fuel, "expected_utc_hour_end_count": len(expected),
                "source_timestamp_count": count_present,
                "missing_source_timestamp_count": len(absent),
                "reported_mw_present_count": int(frame.reported_mw.notna().sum()),
                "reported_mw_null_on_present_timestamp": count_missing_values,
                "adjusted_mw_present_count": int(frame.adjusted_mw.notna().sum()),
                "imputed_mw_present_count": int(frame.imputed_mw.notna().sum()),
                "negative_reported_mw_count": int((frame.reported_mw < 0).sum()),
                "zero_reported_mw_count": int((frame.reported_mw == 0).sum()),
                "reported_mw_max": float(frame.reported_mw.max()) if frame.reported_mw.notna().any() else None,
                "reported_mw_min": float(frame.reported_mw.min()) if frame.reported_mw.notna().any() else None,
                "first_source_utc_hour_end": frame.index.min().isoformat() if len(frame) else None,
                "last_source_utc_hour_end": frame.index.max().isoformat() if len(frame) else None,
                "BA_equals_state": False,
                "observed_CF_normalization_validated": False,
            })
            for month in range(7, 13):
                idx = expected[expected.month == month]
                slice_ = present.reindex(idx)
                source_present = idx.isin(frame.index)
                monthly.append({
                    "ba_code": ba, "fuel": fuel, "month": f"2023-{month:02d}",
                    "expected_hours": len(idx),
                    "source_timestamp_count": int(source_present.sum()),
                    "missing_source_timestamps": int((~source_present).sum()),
                    "reported_valid_mw_hours": int(slice_.reported_mw.notna().sum()),
                    "reported_null_on_present_timestamps": int(
                        frame.reindex(idx[source_present]).reported_mw.isna().sum()),
                    "negative_reported_mw_hours": int((slice_.reported_mw < 0).sum()),
                    "reported_mw_max": float(slice_.reported_mw.max()) if slice_.reported_mw.notna().any() else None,
                })
    summary = pd.DataFrame(rows)
    by_month = pd.DataFrame(monthly)
    if len(summary) != len(BAS)*len(TECHS) or len(by_month) != len(summary)*6:
        raise ValueError("Coverage cohort mismatch")
    if not summary.source_timestamp_count.add(
        summary.missing_source_timestamp_count).eq(EXPECTED_HOURS).all():
        raise ValueError("Coverage is not reconcilable to target UTC calendar")
    return summary, by_month, pd.DataFrame(
        missing, columns=["ba_code", "fuel", "utc_hour_end"]
    )


def run(archive, out):
    obs = extract_observed(Path(archive))
    summary, monthly, missing = coverage(obs)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    obs.to_csv(out/"paper_s_eia930_2023H2_four_BA_wind_solar_raw_MW.csv", index=False)
    summary.to_csv(out/"paper_s_eia930_2023H2_8_BA_fuel_coverage.csv", index=False)
    monthly.to_csv(out/"paper_s_eia930_2023H2_48_month_BA_fuel_coverage.csv", index=False)
    missing.to_csv(out/"paper_s_eia930_2023H2_missing_hour_end_timestamps.csv", index=False)
    manifest = {
        "status": "2023H2_RAW_BA_REPORTED_MW_COVERAGE_ONLY",
        "source_archive_url": "https://zenodo.org/records/22856870/files/eia930-2023half2.zip?download=1",
        "source_archive_MD5": EXPECTED_MD5,
        "utc_window_half_open": [START.isoformat(), END.isoformat()],
        "expected_hours_each_BA_fuel": EXPECTED_HOURS,
        "expected_BA_fuel_groups": len(summary),
        "observed_source_rows": len(obs),
        "missing_hour_end_timestamps": len(missing),
        "missing_reported_MW_values_on_present_hours": int(
            summary.reported_mw_null_on_present_timestamp.sum()),
        "source_hour_integrated_MWh_validated": False,
        "BA_equals_state": False,
        "source_capacity_factor_calculated": False,
        "ReEDS_comparison_performed": False,
        "historical_2023H1_coverage_examined": False,
        "original_Paper_S_LPs_modified": False,
    }
    (out/"paper_s_eia930_2023H2_coverage_manifest.json").write_text(
        json.dumps(manifest, indent=2)+"\n"
    )
    print("PAPER_S_EIA930_2023_H2_BA_COVERAGE_AUDITED", json.dumps(manifest))
    return summary, monthly, missing


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    x=p.parse_args()
    run(x.archive,x.out)


if __name__=="__main__":
    main()
