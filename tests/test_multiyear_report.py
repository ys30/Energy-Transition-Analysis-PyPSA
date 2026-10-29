import csv
import json

import pytest

from energy_transition.multiyear_report import aggregate


def test_aggregate_verified_two_year_artifacts(tmp_path):
    root = tmp_path / "artifacts"
    for year in (2023, 2024):
        folder = root / f"eia930-west-{year}"
        (folder / str(year)).mkdir(parents=True)
        (folder / str(year) / "metrics.json").write_text(json.dumps({
            "solve_status": "optimal",
            "observed_demand_mwh": 1000,
            "unserved_mwh": 0,
            "unserved_share": 0,
            "operational_tco2_assumed": 100,
            "objective_usd_assumed": 500,
            "dispatch_mwh_by_carrier": {"gas": 1000},
        }))
        (folder / f"energy_audit_{year}.json").write_text(json.dumps({
            "year": year, "balancing_authorities": ["BA1"],
            "relative_energy_difference": 0,
            "raw_demand_mwh_after_qc": 1000,
        }))
        with (folder / f"ba_audit_{year}.csv").open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=[
                "respondent", "observations", "expected_hours", "imputation_share"
            ])
            w.writeheader()
            w.writerow({"respondent": "BA1", "observations": 8784 if year == 2024 else 8760,
                        "expected_hours": 8784 if year == 2024 else 8760,
                        "imputation_share": 0})
    out = tmp_path / "summary"
    rows = aggregate(root, out, years=[2023, 2024])
    assert len(rows) == 2
    assert (out / "yearly_summary.csv").exists()
    assert (out / "ba_audit_all_years.csv").exists()
    assert (out / "energy_audit_all_years.json").exists()


def test_missing_year_rejected(tmp_path):
    with pytest.raises(FileNotFoundError):
        aggregate(tmp_path, tmp_path / "out", years=[2025])
