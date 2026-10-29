import io
import zipfile

import pandas as pd

from energy_transition.eia860_capacity import read_operable_inventory


def test_eia860_nullable_generator_ids_are_flagged():
    frame = pd.DataFrame({
        "Plant Code": [1001, None, 1003],
        "Generator ID": ["G1", "G2", None],
        "State": ["CA", "AZ", "NM"],
        "Energy Source 1": ["NG", "SUN", "WND"],
        "Nameplate Capacity (MW)": [100, 25, 30],
        "Status": ["OP", "OP", "OP"],
    })
    workbook = io.BytesIO()
    with pd.ExcelWriter(workbook, engine="openpyxl") as writer:
        frame.to_excel(writer, sheet_name="Operable", index=False)
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w") as z:
        z.writestr("3_1_Generator_Y2024.xlsx", workbook.getvalue())
    parsed = read_operable_inventory(archive.getvalue(), 2024)
    assert parsed.id_qc.tolist() == [
        "valid", "missing_identifier", "missing_identifier"
    ]
    assert parsed.loc[0, "plant_id"] == "1001"
    assert parsed.loc[0, "capacity_mw"] == 100
