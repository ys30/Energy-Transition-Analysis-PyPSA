"""Offline tests for EIA-923 official download ZIP selection and provenance."""
import hashlib
import io
import json
import zipfile
from unittest.mock import patch

import pytest

from energy_transition.eia923_download import download_official_eia923


def _zip(files):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as z:
        for name, data in files.items():
            z.writestr(name, data)
    return buffer.getvalue()


def _xlsx():
    return _zip({"[Content_Types].xml": "<Types/>", "xl/workbook.xml": "<workbook/>"})


class _Response:
    def __init__(self, raw, url):
        self.raw, self.url = raw, url

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def geturl(self):
        return self.url

    def read(self):
        return self.raw


def test_extract_official_schedule_zip_and_provenance(tmp_path):
    workbook = _xlsx()
    archive = _zip({
        "EIA923_Schedules_2_3_4_5_M_12_2024_Final.xlsx": workbook,
        "readme.txt": "official",
    })
    url = "https://www.eia.gov/electricity/data/eia923/archive/xls/f923_2024.zip"
    with patch("urllib.request.urlopen", return_value=_Response(archive, url)):
        result = download_official_eia923(url, tmp_path / "source.xlsx", year=2024)
    assert (tmp_path / "source.xlsx").read_bytes() == workbook
    assert result["sha256"] == hashlib.sha256(workbook).hexdigest()
    assert result["archive_sha256"] == hashlib.sha256(archive).hexdigest()
    assert result["archive_member"].endswith(".xlsx")
    assert json.loads((tmp_path / "source.provenance.json").read_text())["report_year_requested"] == 2024


def test_reject_non_official_source(tmp_path):
    with pytest.raises(ValueError, match="Official EIA-923 source"):
        download_official_eia923("https://example.com/file.zip", tmp_path / "file.xlsx", year=2024)


def test_reject_ambiguous_schedule_workbooks(tmp_path):
    archive = _zip({"a_2_3_4_5.xlsx": _xlsx(), "b_2_3_4_5.xlsx": _xlsx()})
    url = "https://www.eia.gov/f923_2024.zip"
    with patch("urllib.request.urlopen", return_value=_Response(archive, url)):
        with pytest.raises(ValueError, match="exactly one"):
            download_official_eia923(url, tmp_path / "file.xlsx", year=2024)
