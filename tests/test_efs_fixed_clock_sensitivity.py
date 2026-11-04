"""Fixed offset compatibility is permutation, not certified UTC chronology."""
import pandas as pd
import pytest
from energy_transition.efs_fixed_clock_sensitivity import (
    audit_fixed_clock,fixed_utc_ordinal,STATE_SHIFTS,YEARS,
)


def sample():
    rows=[]
    for y in YEARS:
        for state in STATE_SHIFTS:
            for hour in range(1,8761):
                rows.append((y,state,"p9",hour,100.0+(hour%23)))
    return pd.DataFrame(rows,columns=[
        "year","state","reeds_zone","local_hour_id","allocated_mw"])


def test_pinned_shift_wraps_and_preserves_all_hours():
    assert fixed_utc_ordinal([1,8754,8755,8760],7).tolist()==[8,1,2,7]
    assert set(fixed_utc_ordinal(range(1,8761),7))==set(range(1,8761))
    with pytest.raises(ValueError,match="1..8760"):
        fixed_utc_ordinal([0],7)


def test_21_real_sized_state_year_series_are_permutations_not_utc_certification():
    out=audit_fixed_clock(sample())
    assert out["state_year_zone_count"]==21
    assert out["strict_per_zone_hour_permutation"]
    assert not out["actual_utc_alignment_verified"]
    assert not out["renewable_generation_snapshot_synchronization_verified"]
    for d in out["year_comparisons"]:
        assert d["annual_mwh"]==pytest.approx(d["shifted_annual_mwh"])


def test_all_seven_admitted_states_share_offset_so_aggregate_peak_is_invariant():
    x=sample()
    first=x.year.eq(2030)&x.state.eq("Arizona")&x.local_hour_id.eq(1)
    x.loc[first,"allocated_mw"]=3000
    out=audit_fixed_clock(x)
    assert out["no_energy_added_by_clock_transform"]
    assert out["year_comparisons"][0]["peak_difference_mw"]==pytest.approx(0)
    assert out["year_comparisons"][0]["annual_mwh"]==pytest.approx(
        out["year_comparisons"][0]["shifted_annual_mwh"])


def test_duplicate_zone_hour_fails_closed():
    x=sample()
    with pytest.raises(ValueError,match="Duplicate"):
        audit_fixed_clock(pd.concat([x,x.iloc[[0]]],ignore_index=True))
