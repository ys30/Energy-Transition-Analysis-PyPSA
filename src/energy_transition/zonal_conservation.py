"""Strict hourly state-to-zone allocation and auditable conservation checks.

Input MW series must have one hourly UTC index; weights are static within a run.
This module validates accounting, not the empirical validity of source weights.
"""
import numpy as np
import pandas as pd


def validate_utc_year(index: pd.DatetimeIndex, year: int) -> int:
    if not isinstance(index, pd.DatetimeIndex) or index.tz is None or str(index.tz) != "UTC":
        raise ValueError("timezone-aware UTC index required")
    expected = pd.date_range(f"{year}-01-01", f"{year+1}-01-01", freq="h", inclusive="left", tz="UTC")
    if not index.equals(expected):
        raise ValueError("missing, duplicate, unordered or out-of-year hours")
    return len(expected)


def allocate_hourly_load(state_load: pd.DataFrame, weights: pd.DataFrame) -> pd.DataFrame:
    required = ["state", "zone", "weight"]
    if not set(required).issubset(weights.columns) or weights.empty:
        raise ValueError("missing or empty weight columns")
    if weights[required].isna().any().any() or weights.duplicated(["state", "zone"]).any():
        raise ValueError("missing or duplicate allocation records")
    if weights["zone"].duplicated().any():
        raise ValueError("zone owned by more than one state")
    try:
        w = pd.to_numeric(weights["weight"], errors="raise").to_numpy(dtype=float)
    except (ValueError, TypeError) as exc:
        raise ValueError("non-numeric weight") from exc
    if not np.isfinite(w).all() or (w < 0).any():
        raise ValueError("nonfinite or negative weight")
    weights = weights.copy()
    weights["weight"] = w
    sums = weights.groupby("state")["weight"].sum()
    if not np.allclose(sums.to_numpy(), 1, atol=1e-10, rtol=0):
        raise ValueError("state weights do not sum to one")
    if set(state_load.columns) != set(sums.index) or state_load.columns.has_duplicates:
        raise ValueError("state coverage mismatch")
    if state_load.index.has_duplicates or state_load.isna().any().any():
        raise ValueError("missing or duplicated input")
    if not all(pd.api.types.is_numeric_dtype(t) for t in state_load.dtypes):
        raise ValueError("non-numeric demand")
    if not np.isfinite(state_load.to_numpy(dtype=float)).all() or (state_load.to_numpy() < 0).any():
        raise ValueError("invalid load")
    out = pd.DataFrame({r.zone: state_load[r.state] * r.weight for r in weights.itertuples(index=False)}, index=state_load.index)
    if not np.allclose(out.sum(axis=1), state_load.sum(axis=1), atol=1e-7, rtol=1e-12):
        raise ValueError("hourly conservation failed")
    return out


def conservation_audit(state_load: pd.DataFrame, zonal_load: pd.DataFrame, weights: pd.DataFrame) -> pd.DataFrame:
    """Per-state annual MWh conservation; requires hourly MW input."""
    records = []
    for state, group in weights.groupby("state"):
        source = float(state_load[state].sum())
        assigned = float(zonal_load[group["zone"].tolist()].sum().sum())
        records.append({"state": state, "source_mwh": source, "allocated_mwh": assigned,
                        "difference_mwh": assigned - source})
    return pd.DataFrame(records).sort_values("state").reset_index(drop=True)
