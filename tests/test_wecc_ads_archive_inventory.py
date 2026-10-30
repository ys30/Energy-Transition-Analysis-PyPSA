import io
import zipfile
import pytest
from energy_transition.wecc_ads_archive_inventory import inventory


def test_inventory_is_source_hashed_and_not_false_certification(tmp_path):
    archive=tmp_path/"planning_case.zip"
    with zipfile.ZipFile(archive,"w") as z:
        z.writestr("case/branch.dat","sample text")
        z.writestr("case/model.mdb","synthetic")
    report=inventory(archive)
    assert report["ready_for_pypsa_line"] is False
    assert len(report["sha256"])==64
    assert [x["extension"] for x in report["files"]]==[".dat",".mdb"]


def test_reject_archive_path_traversal(tmp_path):
    archive=tmp_path/"unsafe.zip"
    with zipfile.ZipFile(archive,"w") as z:
        z.writestr("../escape.dat","unsafe")
    with pytest.raises(ValueError,match="Unsafe"):
        inventory(archive)
