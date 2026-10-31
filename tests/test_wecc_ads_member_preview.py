import zipfile
from energy_transition.wecc_ads_member_preview import preview_archive


def test_preview_reports_only_bounded_text_and_refuses_binary(tmp_path):
    archive=tmp_path/"ads.zip"
    with zipfile.ZipFile(archive,"w") as z:
        z.writestr("case/branches.csv","bus0,bus1,x\\n1,2,0.1\\n")
        z.writestr("case/grid.mdb",b"binary\\x00data")
        z.writestr("case/large.dat","a"*6000)
    report=preview_archive(archive)
    assert not report["ready_for_pypsa_line"]
    assert not report["source_authenticity_confirmed"]
    records={x["name"]:x for x in report["members"]}
    assert records["case/branches.csv"]["status"]=="text_sample_only"
    assert "bus0" in records["case/branches.csv"]["sample_utf8"]
    assert records["case/grid.mdb"]["status"]=="not_text_previewed"
    assert records["case/large.dat"]["sample_truncated"] is True
    assert len(records["case/large.dat"]["sample_utf8"])==4096


def test_binary_dat_member_is_not_decoded(tmp_path):
    archive=tmp_path/"binary_dat.zip"
    with zipfile.ZipFile(archive,"w") as z:
        z.writestr("case/model.dat",bytes([65,0,66]))
    report=preview_archive(archive)
    assert report["members"][0]["status"]=="binary_content_not_previewed"
    assert "sample_utf8" not in report["members"][0]


def test_preview_cli_emits_valid_json_file(tmp_path):
    import json
    import subprocess
    import sys
    archive=tmp_path/"case.zip"
    output=tmp_path/"preview.json"
    with zipfile.ZipFile(archive,"w") as z:
        z.writestr("case/branches.csv","branch_id,bus_a,bus_b\\n")
    subprocess.run([sys.executable,"-m","energy_transition.wecc_ads_member_preview",
                    "--archive",str(archive),"--report",str(output)],
                   check=True,capture_output=True,text=True)
    report=json.loads(output.read_text())
    assert report["members"][0]["status"]=="text_sample_only"
    assert not report["ready_for_pypsa_line"]
