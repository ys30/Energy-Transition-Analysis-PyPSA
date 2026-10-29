import io
import zipfile
import pandas as pd
from energy_transition.eia923_ba_generation import extract_page1, summarize_monthly, MONTHS

def test_page1_ba_fuel_extraction_does_not_add_page4():
    data = {
        "Plant Id":[1,2], "Plant State":["CA","WA"],
        "Reported\nFuel Type Code":["NG","WND"],
        "Balancing\nAuthority Code":["CISO","BPAT"],
        "Reported\nPrime Mover":["CT","WT"],
        "Net Generation\n(Megawatthours)":[120,240],
    }
    for month in MONTHS:
        data["Netgen\n"+month]=[10,20]
    stream=io.BytesIO()
    with pd.ExcelWriter(stream,engine="openpyxl") as writer:
        pd.DataFrame(data).to_excel(writer,sheet_name="Page 1 Generation and Fuel Data",index=False,startrow=5)
        pd.DataFrame({"Plant Id":[1],"Net Generation":[100000]}).to_excel(writer,sheet_name="Page 4 Generator Data",index=False)
    archive=io.BytesIO()
    with zipfile.ZipFile(archive,"w") as z:
        z.writestr("EIA923_Schedules_2_3_4_5_M_12_2024_Final.xlsx",stream.getvalue())
    original,monthly=extract_page1(archive.getvalue())
    selected,audit,totals=summarize_monthly(monthly,["CISO","BPAT"])
    assert len(original)==2
    assert len(selected)==24
    assert totals.groupby("ba_code").netgen_mwh.sum().to_dict()=={"BPAT":240,"CISO":120}
    assert audit.missing_or_nonnumeric.sum()==0
