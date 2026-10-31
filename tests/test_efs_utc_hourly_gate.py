import pytest
from energy_transition.efs_utc_hourly_gate import validate_utc_hourly


def rows():
    return [
        {"state": state, "snapshot": timestamp, "demand_mw": 100}
        for state in ("CA", "NM")
        for timestamp in ("2024-11-03T08:00:00Z", "2024-11-03T09:00:00Z")
    ]


def test_dst_fallback_utc_hours_are_distinct():
    assert validate_utc_hourly(rows())["hours_per_state"] == 2


@pytest.mark.parametrize("bad", [
    "2024-11-03T01:00:00",
    "2024-11-03T01:00:00-07:00",
    "2024-11-03T08:30:00Z",
])
def test_ambiguous_or_non_utc_hour_rejected(bad):
    data = rows()
    data[0]["snapshot"] = bad
    with pytest.raises(ValueError):
        validate_utc_hourly(data)


def test_missing_hour_rejected():
    data = rows()
    data[1]["snapshot"] = "2024-11-03T10:00:00Z"
    with pytest.raises(ValueError):
        validate_utc_hourly(data)


def test_cross_state_coverage_rejected():
    data = rows()
    data.pop()
    with pytest.raises(ValueError):
        validate_utc_hourly(data)
