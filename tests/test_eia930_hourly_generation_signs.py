"""Regression tests for observed net-generation sign and modeled output checks."""
import pandas as pd
import pytest

from energy_transition.eia930_hourly_model_comparison import compare_hourly


def _frame(values):
    return pd.DataFrame({
        "respondent": ["CISO"] * len(values),
        "period": pd.date_range("2024-01-01", periods=len(values), freq="h", tz="UTC"),
        "value": values,
    })


def test_negative_observed_net_generation_is_preserved_and_counted():
    pairs, summary = compare_hourly(_frame([-5.0, 0.0, 12.0]),
                                    _frame([0.0, 1.0, 10.0]), 2024, ["CISO"])
    row = summary.iloc[0]
    assert row["observed_negative_hours"] == 1
    assert row["observed_zero_hours"] == 1
    assert row["paired_hours"] == 3
    assert pairs.loc[0, "observed"] == -5.0
    assert pairs.loc[0, "model_minus_observed_mw"] == 5.0
    assert not row["validated_calibration"]


def test_negative_modeled_generation_is_rejected():
    with pytest.raises(ValueError, match="negative generator production"):
        compare_hourly(_frame([2.0]), _frame([-0.01]), 2024, ["CISO"])


def test_missing_observed_hours_do_not_count_as_zero():
    pairs, summary = compare_hourly(_frame([None, 0.0]),
                                    _frame([1.0, 1.0]), 2024, ["CISO"])
    row = summary.iloc[0]
    assert row["observed_zero_hours"] == 1
    assert row["observed_negative_hours"] == 0
    assert row["paired_hours"] == 1
    assert not pairs.loc[0, "complete_pair"]


def test_malformed_observed_mw_is_not_silently_missing():
    with pytest.raises(ValueError, match="nonnumeric MW"):
        compare_hourly(_frame(["bad"]), _frame([1.0]), 2024, ["CISO"])


def test_explicit_null_observed_mw_remains_missing():
    pairs, summary = compare_hourly(_frame([None]), _frame([1.0]), 2024, ["CISO"])
    assert summary.iloc[0]["paired_hours"] == 0
    assert not pairs.loc[0, "complete_pair"]
