import csv
import gzip
import pytest
from energy_transition.nlr_efs_annual_metrics import summarize
from energy_transition.nlr_efs_western_hourly import CORE_WEST, YEARS, HOURS


def test_valid_yearly_metrics(tmp_path):
    p = tmp_path / "loads.csv.gz"
    with gzip.open(p, "wt", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "state", "local_hour_id", "load_mw"])
        for y in YEARS:
            for state in CORE_WEST:
                for h in range(1, HOURS + 1):
                    w.writerow([y, state, h, 2.0])
    result = summarize(p)
    assert result["rows_verified"] == 3 * 11 * 8760
    assert result["by_year"][0]["core_11_state_annual_mwh"] == 11 * 8760 * 2
    assert result["by_year"][0]["state_peak_mw"]["AZ"] == 2.0
    assert result["utc_hourly_alignment_verified"] is False


def test_incomplete_source_rejected(tmp_path):
    p = tmp_path / "missing.csv.gz"
    with gzip.open(p, "wt", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "state", "local_hour_id", "load_mw"])
        w.writerow([2030, "AZ", 1, 10])
    with pytest.raises(ValueError, match="Incomplete"):
        summarize(p)
