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
