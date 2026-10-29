import pandas as pd
import pytest

from energy_transition.eia930_west import representative_hours, fetch_eia_demand


def test_missing_key(monkeypatch):
    monkeypatch.delenv("EIA_API_KEY", raising=False)
    with pytest.raises(ValueError, match="EIA_API_KEY"):
        fetch_eia_demand(2024, api_key=None)


def test_representative_month_hour_weights():
    # One complete synthetic year as a unit test fixture, not a reported EIA result.
    dates = pd.date_range("2023-01-01", "2024-01-01", freq="h", inclusive="left", tz="UTC")
    df = pd.DataFrame({"period": dates, "respondent": "TEST", "value": 100.0})
    rep = representative_hours(df, 2023)
    assert len(rep) == 288
    assert (rep.value == 100).all()
    assert rep.weight_h.sum() == 365 * 24
    assert (rep.value * rep.weight_h).sum() == 100 * 8760


def test_missing_month_rejected():
    dates = pd.date_range("2023-01-01", "2023-02-01", freq="h", inclusive="left", tz="UTC")
    df = pd.DataFrame({"period": dates, "respondent": "TEST", "value": 100.0})
    with pytest.raises(ValueError, match="Incomplete"):
        representative_hours(df, 2023)


@pytest.mark.parametrize("year", [2023, 2024])
def test_multi_ba_energy_conservation(year):
    dates = pd.date_range(f"{year}-01-01", f"{year+1}-01-01",
                          freq="h", inclusive="left", tz="UTC")
    a = pd.DataFrame({"period": dates, "respondent": "BA_A",
                      "value": [100 + d.hour for d in dates]})
    b = pd.DataFrame({"period": dates, "respondent": "BA_B",
                      "value": [200 + d.month for d in dates]})
    observations = pd.concat([a, b], ignore_index=True)
    rep = representative_hours(observations, year)
    assert len(rep) == 288
    assert rep.weight_h.sum() == len(dates)
    assert (rep.value * rep.weight_h).sum() == pytest.approx(observations.value.sum())


def test_missing_one_hour_in_middle_rejected():
    dates = pd.date_range("2023-01-01", "2024-01-01",
                          freq="h", inclusive="left", tz="UTC")
    df = pd.DataFrame({"period": dates, "respondent": "TEST", "value": 100.0})
    df = df.drop(index=1234)
    with pytest.raises(ValueError, match="Incomplete"):
        representative_hours(df, 2023)


def test_duplicate_ba_hour_rejected():
    dates = pd.date_range("2023-01-01", "2024-01-01",
                          freq="h", inclusive="left", tz="UTC")
    df = pd.DataFrame({"period": dates, "respondent": "TEST", "value": 100.0})
    df = pd.concat([df, df.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="Duplicate"):
        representative_hours(df, 2023)


def test_missing_shared_hour_rejected():
    dates = pd.date_range("2023-01-01", "2024-01-01",
                          freq="h", inclusive="left", tz="UTC")
    a = pd.DataFrame({"period": dates, "respondent": "A", "value": 100.0})
    b = pd.DataFrame({"period": dates, "respondent": "B", "value": 200.0})
    both = pd.concat([a, b], ignore_index=True)
    both = both.loc[both.period != dates[1234]]
    with pytest.raises(ValueError, match="Incomplete"):
        representative_hours(both, 2023)
