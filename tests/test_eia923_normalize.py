import pandas as pd
import pytest

from energy_transition.eia923_normalize import MONTHS, normalize_schedule3


def _schedule(fuel="NG", value=10):
    row = {"Plant Id": 123, "Reported Fuel Type Code": fuel}
    row.update({f"Netgen {month.title()}": value for month in MONTHS})
    return pd.DataFrame([row])


def test_schedule3_normalizes_months_and_annual_energy():
    result = normalize_schedule3(_schedule(), 2024)
    assert len(result) == 12
    assert result.net_generation_mwh.sum() == 120
    assert result.fuel.unique().tolist() == ["gas"]
    assert result.month.tolist() == list(range(1, 13))


def test_schedule3_rejects_unknown_fuel():
    with pytest.raises(ValueError, match="Unmapped"):
        normalize_schedule3(_schedule(fuel="UNKNOWN"), 2024)


def test_schedule3_rejects_nonnumeric_observation():
    with pytest.raises(ValueError, match="Non-numeric"):
        normalize_schedule3(_schedule(value="withheld"), 2024)


def test_schedule3_preserves_negative_generation():
    result = normalize_schedule3(_schedule(value=-2), 2024)
    assert result.net_generation_mwh.sum() == -24
