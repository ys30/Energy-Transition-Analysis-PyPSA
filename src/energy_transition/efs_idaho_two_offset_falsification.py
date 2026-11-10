"""Falsifiable Idaho two-offset source-index mixture (not timezone attribution).

Fit 2030 weight, freeze for 2040/2050; test both shift directions.
Non-wrapping common support is used for all offsets; no timestamp certification.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .reeds2022_reference_hdf5_provenance import CHECKSUM, YEARS, verify_publisher_2012_clock

N = 8760
DIRECTIONS = {"minus": (-2, -3), "plus": (2, 3)}


def fit_weight(y, first, second):
    d = first - second
    denom = float(d @ d)
    if denom <= 0:
        raise ValueError("Cannot identify mixture weight from identical candidates")
    return float(np.clip(((y - second) @ d) / denom, 0, 1))


def metrics(y, first, second, w):
    prediction = w * first + (1 - w) * second
    residual = y - prediction
    ae = np.abs(residual)
    return {
        "mae_mw": float(ae.mean()),
        "rmse_mw": float(np.sqrt(np.mean(residual**2))),
        "maximum_abs_error_mw": float(ae.max()),
        "hours_over_1mw": int((ae > 1).sum()),
        "hours_within_0_5mw": int((ae <= .5).sum()),
        "signed_mean_residual_mw": float(residual.mean()),
        "compared_hours": int(len(y)),
    }


def aligned(a, b, offsets):
    """For offset k, compare EFS[i] to ReEDS[i-k] without wrapping."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if a.shape != (N,) or b.shape != (N,):
        raise ValueError("Missing source hours")
    if not (np.isfinite(a).all() and np.isfinite(b).all()):
        raise ValueError("Invalid nonfinite values")
    if (a < 0).any() or (b < 0).any():
        raise ValueError("Negative source load")
    left = max(0, *offsets)
    right = min(N, *(N + k for k in offsets))
    idx = np.arange(left, right)
    return idx, a[idx], b[idx - offsets[0]], b[idx - offsets[1]]


def analyze(year_to_pair):
    if set(year_to_pair) != set(YEARS):
        raise ValueError("Need 2030, 2040, 2050 source pairs")
    records = []
    for direction, offsets in DIRECTIONS.items():
        aligned_years = {year: aligned(*year_to_pair[year], offsets) for year in YEARS}
        train_idx, ty, tx1, tx2 = aligned_years[2030]
        split = N // 2
        train_mask = train_idx < split
        if train_mask.sum() < 1000:
            raise ValueError("Insufficient training hours")
        frozen = fit_weight(ty[train_mask], tx1[train_mask], tx2[train_mask])
        full_2030 = fit_weight(ty, tx1, tx2)
        for year in YEARS:
            idx, y, x1, x2 = aligned_years[year]
            subsets = {"full": np.ones(len(idx), dtype=bool),
                       "first_half": idx < split,
                       "second_half": idx >= split}
            for name, mask in subsets.items():
                ym, a, b = y[mask], x1[mask], x2[mask]
                if not len(ym):
                    raise ValueError("Empty evaluation window")
                for model, w in [
                    ("single_first", 1.),
                    ("single_second", 0.),
                    ("frozen_2030_firsthalf", frozen),
                    ("fitted_same_window_diagnostic", fit_weight(ym, a, b)),
                    ("frozen_2030_fullyear_diagnostic", full_2030),
                ]:
                    records.append({
                        "year": int(year), "direction": direction,
                        "offset_first_h": offsets[0], "offset_second_h": offsets[1],
                        "window": name, "model": model,
                        "first_offset_weight": w,
                        "train_source_year": 2030 if model.startswith("frozen") else (year if model == "fitted_same_window_diagnostic" else None),
                        "train_window": "first_half" if model == "frozen_2030_firsthalf" else ("full" if model == "frozen_2030_fullyear_diagnostic" else (name if model == "fitted_same_window_diagnostic" else "none")),
                        **metrics(ym, a, b, w),
                    })
    return pd.DataFrame(records)


def source_audit(efs_csv, h5_path):
    import h5py
    with h5_path.open("rb") as f:
        md5 = hashlib.file_digest(f, "md5").hexdigest()
    if md5 != CHECKSUM:
        raise ValueError("Publisher HDF5 checksum mismatch")
    ef = pd.read_csv(efs_csv, compression="infer")
    required = {"year", "state", "local_hour_id", "load_mw"}
    if not required.issubset(ef) or ef[list(required)].isna().any().any():
        raise ValueError("Invalid EFS archive")
    idaho = ef.loc[ef.state == "ID"]
    if idaho.duplicated(["year", "local_hour_id"]).any():
        raise ValueError("Duplicate EFS source hour")
    series = {}
    with h5py.File(h5_path, "r") as h:
        for year in YEARS:
            e = idaho.loc[idaho.year == year].sort_values("local_hour_id")
            if not np.array_equal(e.local_hour_id.to_numpy(), np.arange(1, N+1)):
                raise ValueError("Missing Idaho hours")
            g = h[str(year)]
            verify_publisher_2012_clock(g["datetime"][:])
            series[year] = (e.load_mw.to_numpy(), g["ID"][:])
    return analyze(series), {
        "efs_csv_sha256": hashlib.sha256(efs_csv.read_bytes()).hexdigest(),
        "reeds2022_hdf5_publisher_md5": md5,
        "fit_scope": "2030 first source-ordinal half; fixed and scored on later halves and planning years",
        "nonwrapping": True,
        "clock_and_timezone_physical_cause_identified": False,
        "real_weather_join_authorized": False,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--efs-hourly", type=Path, required=True)
    p.add_argument("--reeds-h5", type=Path, required=True)
    p.add_argument("--out-csv", type=Path, required=True)
    p.add_argument("--out-json", type=Path, required=True)
    a = p.parse_args()
    table, meta = source_audit(a.efs_hourly, a.reeds_h5)
    a.out_csv.parent.mkdir(parents=True, exist_ok=True)
    a.out_json.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(a.out_csv, index=False)
    a.out_json.write_text(json.dumps(meta, indent=2) + "\n")
    selected = table[(table.window == "full") & (table.model == "frozen_2030_firsthalf")]
    print(selected[["year", "direction", "first_offset_weight", "mae_mw", "hours_over_1mw"]].to_string(index=False))


if __name__ == "__main__":
    main()
