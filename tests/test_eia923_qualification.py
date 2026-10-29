import pandas as pd
import pytest
from energy_transition.eia923_qualification import qualify

def test_qualification_keeps_unverified_annual_totals_outside_qualified_sum():
    audit=pd.DataFrame([
      {"source_row_id":1,"ba_code":"CISO","fuel":"NG","annual_reported_mwh":120,
       "reconciles":True,"fully_numeric":True,"missing_months":0},
      {"source_row_id":2,"ba_code":"CISO","fuel":"NG","annual_reported_mwh":55,
       "reconciles":False,"fully_numeric":False,"missing_months":2},
    ])
    rows,summary=qualify(audit)
    record=summary.iloc[0]
    assert record.qualified_annual_mwh==120
    assert record.withheld_reported_annual_mwh==55
    assert record.missing_monthly_cells==2
    assert record.qualification_fraction==0.5

def test_duplicate_eia923_source_rows_fail():
    sample=pd.DataFrame([
      {"source_row_id":5,"ba_code":"CISO","fuel":"NG","annual_reported_mwh":1,
       "reconciles":True,"fully_numeric":True,"missing_months":0},
      {"source_row_id":5,"ba_code":"BPAT","fuel":"WAT","annual_reported_mwh":2,
       "reconciles":True,"fully_numeric":True,"missing_months":0}])
    with pytest.raises(ValueError,match="Duplicate"):
        qualify(sample)
