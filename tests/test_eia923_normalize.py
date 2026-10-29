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


def test_schedule3_rejects_missing_month_without_zero_imputation():
    frame = _schedule()
    frame.loc[0, "Netgen February"] = None
    with pytest.raises(ValueError, match="Missing EIA-923 monthly"):
        normalize_schedule3(frame, 2024)


def test_schedule3_accepts_plant_id_number_and_annotated_fuel_header():
    frame = _schedule()
    frame = frame.rename(columns={
        "Plant Id": "Plant Id Number",
        "Reported Fuel Type Code": "Reported Fuel Type Code (EIA-923)",
    })
    result = normalize_schedule3(frame, 2024)
    assert result.net_generation_mwh.sum() == 120


def test_schedule3_accepts_official_multiline_fuel_header():
    frame = _schedule().rename(columns={
        "Reported Fuel Type Code": "Reported\nFuel Type Code"
    })
    result = normalize_schedule3(frame, 2024)
    assert len(result) == 12
    assert result.net_generation_mwh.sum() == 120


def test_schedule3_accepts_multiline_official_netgen_columns():
    frame = _schedule().rename(columns={
        "Plant Id": "Plant\nId",
        "Reported Fuel Type Code": "Reported\nFuel Type Code",
        **{f"Netgen {m.title()}": f"Netgen\n{m.title()}" for m in MONTHS},
    })
    out = normalize_schedule3(frame, 2024)
    assert len(out) == 12
    assert out.net_generation_mwh.sum() == 120


def test_official_incomplete_row_exclusion_does_not_zero_fill():
    frame = _schedule()
    second = _schedule(value=7)
    second["Plant Id"] = 999
    second.loc[0, "Netgen February"] = "not reported"
    data = pd.concat([frame, second], ignore_index=True)
    result = normalize_schedule3(data, 2024, allow_incomplete=True)
    assert result.plant_id.unique().tolist() == ["123"]
    assert result.net_generation_mwh.sum() == 120
    audit = result.attrs["excluded_cells"]
    assert len(audit) == 1
    assert str(audit.iloc[0].plant_id) == "999"
