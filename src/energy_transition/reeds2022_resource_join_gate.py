"""Fail-closed checks for matching ReEDS 2022 demand and wind/PV resources.

This module does NOT certify a physical hour-energy join or capacity-to-state
allocation; it exposes audit operations and refuses an unsupported empirical join.
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd

FIXED_CST = "Etc/GMT+6"
PV_INVERTER_LOADING_RATIO = 1.34
HOURS = 8760


@dataclass(frozen=True)
class NativeClockAudit:
    count: int
    first_utc: str
    last_utc: str
    reference_weather_year: int = 2012
    physical_hour_interval_admitted: bool = False


def _strict_2012_cst_index(index, *, allow_naive: bool) -> pd.DatetimeIndex:
    """Require exact publisher 2012 leap-calendar: Jan 1 through Dec 30."""
    native = pd.DatetimeIndex(pd.to_datetime(index, errors="raise"))
    if native.tz is None:
        if not allow_naive:
            raise ValueError("Explicitly offset-aware demand labels required")
        native = native.tz_localize(FIXED_CST)
    native = native.tz_convert(FIXED_CST)
    expected = pd.date_range("2012-01-01", periods=HOURS, freq="h", tz=FIXED_CST)
    if len(native) != HOURS or not native.equals(expected):
        raise ValueError("Incorrect 2012 CST calendar: no wrap, DST, Dec31, gaps, or duplicates")
    return native


def audit_native_clocks(demand_hour_ending, weather_instantaneous) -> NativeClockAudit:
    """Only check timestamp compatibility; never assert interval equivalence."""
    d = _strict_2012_cst_index(demand_hour_ending, allow_naive=False)
    w = _strict_2012_cst_index(weather_instantaneous, allow_naive=True)
    if not d.equals(w):
        raise ValueError("Demand and weather absolute hour labels disagree")
    return NativeClockAudit(
        count=HOURS, first_utc=d[0].tz_convert("UTC").isoformat(),
        last_utc=d[-1].tz_convert("UTC").isoformat()
    )


def validate_native_cf(values, *, technology: str, encoded_scale: float | None = None):
    """Validate *all* CF cells; refuse to guess integer HDF5 encoding scale.

    PV native denominator is DC array MW; this function changes denominator
    to AC nameplate MW after original native [0,1] normalization.
    """
    a = np.asarray(values)
    if a.ndim != 2:
        raise ValueError("Expected 2D CF matrix (hour, resource class/BA)")
    if np.issubdtype(a.dtype, np.integer) and encoded_scale is None:
        raise ValueError("Integer CF data require independently authenticated encoding scale")
    if encoded_scale is not None and (not np.isfinite(encoded_scale) or encoded_scale <= 0):
        raise ValueError("Invalid explicit numeric CF scale")
    a = a.astype(np.float64)
    if encoded_scale is not None:
        a = a / encoded_scale
    if not np.isfinite(a).all() or (a < -1e-10).any() or (a > 1 + 1e-10).any():
        raise ValueError("Publisher native CF out of physical [0,1] bounds")
    if technology == "pv":
        a *= PV_INVERTER_LOADING_RATIO
        if (a > 1 + 1e-8).any():
            raise ValueError("PV AC-nameplate CF above 1 after ILR conversion")
    elif technology != "wind":
        raise ValueError("Unrecognized resource technology")
    return a


def capacity_weighted_cf(cf, capacities_mw):
    """Independent class-and-zone capacity aggregation, not state allocation."""
    cf = np.asarray(cf, dtype=np.float64)
    weights = np.asarray(capacities_mw, dtype=np.float64)
    if cf.ndim != 2 or weights.ndim != 1 or cf.shape[1] != weights.size:
        raise ValueError("Capacity matrix columns must match CF classes exactly")
    if not np.isfinite(weights).all() or (weights < 0).any() or weights.sum() <= 0:
        raise ValueError("Capacities must be finite nonnegative MW, total > 0")
    if not np.isfinite(cf).all() or (cf < 0).any() or (cf > 1 + 1e-8).any():
        raise ValueError("Invalid normalized CF")
    return cf @ weights / weights.sum()


def audit_county_zone_cross_state(county_fips, reeds_ba):
    """Diagnose cross-state BA memberships; not area/capacity allocations."""
    data = pd.DataFrame({"county": pd.Series(county_fips, dtype="string"),
                         "ba": pd.Series(reeds_ba, dtype="string")})
    if data.isna().any().any() or data.duplicated("county").any():
        raise ValueError("Incomplete or duplicated county-to-BA allocation")
    if not data["county"].str.fullmatch(r"\d{5}").all():
        raise ValueError("Every county must have 5-digit FIPS, preserving zeroes")
    if not data["ba"].str.fullmatch(r"p\d+").all():
        raise ValueError("Every ReEDS BA key must match p<number>")
    data["state_fips"] = data["county"].str[:2]
    summary = (data.groupby("ba").agg(
        county_count=("county", "size"),
        distinct_states=("state_fips", "nunique")
    ).reset_index())
    summary["crosses_state_border"] = summary.distinct_states.gt(1)
    summary["capacity_state_fraction_certified"] = False
    return summary


def require_empirical_join(*, hour_energy_contract: bool,
                           state_capacity_allocation_certified: bool,
                           full_cf_scale_certified: bool):
    """Stop workflow until each independently supported admission is true."""
    blocked = []
    if not hour_energy_contract:
        blocked.append("instantaneous CF -> demand hour-ending energy")
    if not state_capacity_allocation_certified:
        blocked.append("BA resource capacity -> state allocation")
    if not full_cf_scale_certified:
        blocked.append("original publisher CF scaling")
    if blocked:
        raise ValueError("BLOCK_PHYSICAL_JOIN: " + "; ".join(blocked))
    return True
