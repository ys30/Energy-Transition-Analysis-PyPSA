import io
import zipfile

import pandas as pd

from energy_transition.eia923_schema_audit import inspect_archive


def test_official_workbook_schema_audit_keeps_header_candidates():
    xlsx = io.BytesIO()
    with pd.ExcelWriter(xlsx, engine="openpyxl") as writer:
        pd.DataFrame({"Plant Id": [42], "Net Generation (Megawatthours)": [99]}).to_excel(
            writer, sheet_name="Page 1 Generation and Fuel Data", index=False, startrow=4
        )
    zip_bytes = io.BytesIO()
    with zipfile.ZipFile(zip_bytes, "w") as z:
        z.writestr("EIA923_Schedules_2_3_4_5_M_12_2024_Final.xlsx", xlsx.getvalue())
    result = inspect_archive(zip_bytes.getvalue())
    assert len(result) == 1
    assert "Plant Id" in result[0]["headers"]["4"]
    assert "Net Generation (Megawatthours)" in result[0]["headers"]["4"]
