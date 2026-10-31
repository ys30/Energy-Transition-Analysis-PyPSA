import pytest
from energy_transition.pypsa_usa_zenodo_manifest import summarize_record


def test_manifest_validates_archive_but_does_not_claim_download_or_solve():
    record={"id":14611937,"doi":"10.5281/zenodo.14611937",
            "files":[{"key":"pypsa_usa_data.zip","size":567400000,
                      "checksum":"md5:23ac145bdbf0b799e8482ea469026877"}]}
    result=summarize_record(record)
    assert result["archive_size_bytes"]==567400000
    assert not result["archive_downloaded"]
    assert not result["network_data_parsed"]
    assert not result["planning_case_solved"]


@pytest.mark.parametrize("files", [[],[{"key":"pypsa_usa_data.zip","size":1,"checksum":"invalid"}]])
def test_manifest_rejects_missing_or_unverifiable_metadata(files):
    with pytest.raises(ValueError):
        summarize_record({"files":files})
