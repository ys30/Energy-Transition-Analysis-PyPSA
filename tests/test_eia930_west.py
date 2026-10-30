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


def test_eia_api_rejects_concentrated_ba_anomalies(monkeypatch):
    """A BA with >1% bad demand cannot hide under a low pooled QC rate."""
    import json
    from energy_transition import eia930_west

    class Response:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
        def read(self, *args):
            return self.payload
        payload = b""

    dates = pd.date_range("2023-01-01", periods=1000, freq="h", tz="UTC")
    rows = []
    for ba in ("A", "B"):
        for i, dt in enumerate(dates):
            value = -1 if ba == "A" and 10 <= i < 22 else 100
            rows.append({"period": dt.strftime("%Y-%m-%dT%H"),
                         "respondent": ba, "value": value})
    # 12 bad rows out of 2000 is 0.6% overall, but 1.2% for BA A.
    payload = json.dumps({"response": {"data": rows, "total": len(rows)}}).encode()
    Response.payload = payload
    monkeypatch.setattr(eia930_west.urllib.request, "urlopen", lambda *args, **kwargs: Response())
    with pytest.raises(ValueError, match="BA-specific"):
        eia930_west.fetch_eia_demand(2023, bas=("A", "B"), api_key="test", length=3000)


@pytest.mark.parametrize("raw, representative", [
    (1000.0, 999.0),
    (1000.0, float("nan")),
    (float("inf"), 1000.0),
    (0.0, 0.0),
    (-1.0, -1.0),
])
def test_annual_energy_conservation_gate_rejects_bad_totals(raw, representative):
    from energy_transition.eia930_west import validate_annual_energy_conservation
    with pytest.raises(ValueError, match="does not conserve annual demand energy"):
        validate_annual_energy_conservation(raw, representative, 2024)


def test_annual_energy_conservation_gate_accepts_rounding_tolerance():
    from energy_transition.eia930_west import validate_annual_energy_conservation
    validate_annual_energy_conservation(1000000.0, 1000000.00001, 2024)


@pytest.mark.parametrize("invalid_ba", [None, "", "   "])
def test_representative_hours_rejects_missing_ba_identity(invalid_ba):
    dates = pd.date_range("2023-01-01", "2024-01-01", freq="h", inclusive="left", tz="UTC")
    df = pd.DataFrame({"period": dates, "respondent": "BA_A", "value": 100.0})
    df.loc[0, "respondent"] = invalid_ba
    with pytest.raises(ValueError, match="balancing authority identifier"):
        representative_hours(df, 2023)


@pytest.mark.parametrize("bad_value", [float("inf"), float("-inf"), float("nan")])
def test_representative_hours_rejects_nonfinite_hourly_demand(bad_value):
    dates = pd.date_range("2023-01-01", "2024-01-01", freq="h", inclusive="left", tz="UTC")
    df = pd.DataFrame({"period": dates, "respondent": "BA_A", "value": 100.0})
    df.loc[123, "value"] = bad_value
    with pytest.raises(ValueError, match="nonfinite"):
        representative_hours(df, 2023)


@pytest.mark.parametrize("respondent, timestamp, expected_error", [
    ("OTHER", "2023-01-01T00", "BA identifiers"),
    (None, "2023-01-01T00", "BA identifiers"),
    ("BA_A", "2022-12-31T23", "outside requested year"),
    ("BA_A", "2024-01-01T00", "outside requested year"),
])
def test_eia_api_rejects_out_of_scope_rows_before_gap_filling(
    monkeypatch, respondent, timestamp, expected_error
):
    import json
    from energy_transition import eia930_west

    class Response:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
        def read(self, *args):
            return json.dumps({"response": {"data": [
                {"period": timestamp, "respondent": respondent, "value": 100}
            ], "total": 1}}).encode()

    monkeypatch.setattr(eia930_west.urllib.request, "urlopen",
                        lambda *args, **kwargs: Response())
    with pytest.raises(ValueError, match=expected_error):
        fetch_eia_demand(2023, bas=("BA_A",), api_key="test")
