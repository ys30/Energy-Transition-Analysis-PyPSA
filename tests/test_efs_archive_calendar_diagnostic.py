from datetime import datetime, timedelta
import pytest
from energy_transition.efs_archive_calendar_diagnostic import analyze


def records():
    return [
        {"model_year": y, "archive_sequence_ordinal": h+1,
         "stored_naive_snapshot": str(datetime(y, 1, 1) + timedelta(hours=h))}
        for y in (2030, 2040, 2050) for h in range(8760)
    ]


def test_nonleap_template_label_discrepancy():
    result = analyze(records())
    assert [r["hours_with_different_month_day_hour_label"]
            for r in result["calendar_comparison"]] == [0, 7344, 0]
    first = result["calendar_comparison"][1]["first_different_label"]
    assert first["archive_sequence_ordinal"] == 1417
    assert first["stored_naive_snapshot"] == "2040-02-29 00:00:00"
    assert first["nonleap_template_month_day_hour"] == "03-01 00"
    assert result["utc_alignment_verified"] is False
    assert result["physical_dispatch_admitted"] is False


def test_does_not_accept_reordered_source_index():
    data = records()
    data[0]["stored_naive_snapshot"] = "2030-01-02 00:00:00"
    with pytest.raises(ValueError, match="mismatch"):
        analyze(data)
