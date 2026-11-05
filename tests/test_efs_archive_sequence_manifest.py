from datetime import datetime, timedelta
import pytest
from energy_transition.efs_archive_sequence_manifest import build_rows


def fixture():
    return {"archive_years": [
        {"model_year": y, "stored_snapshot_count": 8760,
         "stored_timestamp_timezone_name": None,
         "stored_snapshot_first": f"{y}-01-01 00:00:00",
         "stored_snapshot_last": str(datetime(y, 1, 1) + timedelta(hours=8759))}
        for y in (2030, 2040, 2050)
    ]}


def test_leap_year_and_no_utc_admission():
    rows, result = build_rows(fixture())
    assert len(rows) == 3 * 8760
    assert [x["archived_leap_day_hours"] for x in result["years"]] == [0, 24, 0]
    assert [x["archived_dec31_hours"] for x in result["years"]] == [24, 0, 24]
    assert result["weather_generator_join_admitted"] is False
    assert all(x["verified_utc_timestamp"] == "" for x in rows)
    assert all(x["verified_source_local_hour_id"] == "" for x in rows)


def test_refuse_fake_timestamp_completion():
    source = fixture()
    source["archive_years"][1]["stored_snapshot_last"] = "2040-12-31 23:00:00"
    with pytest.raises(ValueError, match="boundaries"):
        build_rows(source)


def test_refuse_partial_source():
    source = fixture()
    source["archive_years"][1]["stored_snapshot_count"] = 8759
    with pytest.raises(ValueError, match="8760"):
        build_rows(source)
