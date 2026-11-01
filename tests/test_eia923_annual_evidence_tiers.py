"""Regression tests for conservative EIA-923 annual evidence tiers."""
import json
import pandas as pd
import pytest
from energy_transition.eia923_annual_evidence_tiers import examine


def _audit(rows, tmp_path):
    source = tmp_path / "source.csv"
    out = tmp_path / "summary.csv"
    pd.DataFrame(rows).to_csv(source, index=False)
    examine(source, out)
    return pd.read_csv(out), json.loads(out.with_suffix(".json").read_text())


def _row(identifier, *, months=0, annual=120.0, numeric=True, reconciles=True):
    return {"source_row_id": identifier, "plant_id": "11", "ba_code": "BPAT",
            "fuel": "WAT", "fully_numeric": numeric,
            "reconciles": reconciles, "annual_reported_mwh": annual,
            "missing_months": months}


def test_certification_excludes_missing_months_even_if_flags_say_true(tmp_path):
    result, report = _audit([
        _row("good"),
        _row("missing", months=1, annual=40.0),
        _row("no_annual", annual=float("nan")),
    ], tmp_path)
    tiers = result.set_index("evidence_tier")
    assert tiers.loc["twelve_month_reconciled", "strict_monthly_certified_mwh"] == 120.0
    assert tiers.loc["annual_reported_only_not_monthly_certified", "annual_only_mwh"] == 40.0
    assert report["annual_only_records"] == 1
    assert report["no_monthly_imputation"] is True
    assert report["verified_hourly_generation_profiles"] is False


@pytest.mark.parametrize("months", [-1, 13, None, "not_numeric"])
def test_invalid_month_counts_are_rejected(tmp_path, months):
    source = tmp_path / "bad.csv"
    pd.DataFrame([_row("bad", months=months)]).to_csv(source, index=False)
    with pytest.raises(ValueError, match="monthly-coverage"):
        examine(source, tmp_path / "out.csv")


def test_duplicate_source_record_ids_rejected(tmp_path):
    source = tmp_path / "duplicate.csv"
    pd.DataFrame([_row("same"), _row("same", annual=10.0)]).to_csv(source, index=False)
    with pytest.raises(ValueError, match="Duplicate"):
        examine(source, tmp_path / "out.csv")
