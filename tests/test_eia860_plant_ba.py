import io
import zipfile

import pandas as pd

from energy_transition.eia860_plant_ba import extract_plant_ba


def test_plant_ba_workbook_extraction():
    workbook = io.BytesIO()
    with pd.ExcelWriter(workbook, engine="openpyxl") as writer:
        data = pd.DataFrame({
            "Plant Code": [34, 45, 46],
            "Balancing Authority Code": ["CISO", "BPAT", None],
            "State": ["CA", "OR", "NM"],
        })
        data.to_excel(writer, sheet_name="Plant", index=False, startrow=1)
    zio = io.BytesIO()
    with zipfile.ZipFile(zio, "w") as z:
        z.writestr("2___Plant2024.xlsx", workbook.getvalue())
    actual, sheet = extract_plant_ba(zio.getvalue())
    assert sheet == "Plant"
    assert actual.loc[0, "plant_id"] == "34"
    assert actual.loc[0, "ba_code"] == "CISO"
    assert actual.loc[1, "ba_code"] == "BPAT"
    assert actual.loc[2, "crosswalk_qc"] == "missing_plant_or_ba"


def test_plant_ba_conflicting_state_rejected():
    workbook = io.BytesIO()
    with pd.ExcelWriter(workbook, engine="openpyxl") as writer:
        pd.DataFrame({
            "Plant Code": [101, 101, 102],
            "Balancing Authority Code": ["CISO", "CISO", "BPAT"],
            "State": ["CA", "NV", "WA"],
        }).to_excel(writer, sheet_name="Plant", index=False, startrow=1)
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w") as z:
        z.writestr("2___Plant2024.xlsx", workbook.getvalue())
    result, _ = extract_plant_ba(archive.getvalue())
    assert result.loc[result.plant_id.eq("101"), "crosswalk_qc"].eq(
        "conflicting_plant_state"
    ).all()
    assert result.loc[result.plant_id.eq("102"), "crosswalk_qc"].eq("valid").all()


def test_plant_ba_conflicting_authority_rejected():
    workbook = io.BytesIO()
    with pd.ExcelWriter(workbook, engine="openpyxl") as writer:
        pd.DataFrame({
            "Plant Code": [101, 101],
            "Balancing Authority Code": ["CISO", "BPAT"],
            "State": ["CA", "CA"],
        }).to_excel(writer, sheet_name="Plant", index=False, startrow=1)
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w") as z:
        z.writestr("2___Plant2024.xlsx", workbook.getvalue())
    result, _ = extract_plant_ba(archive.getvalue())
    assert result.crosswalk_qc.eq("conflicting_ba").all()
