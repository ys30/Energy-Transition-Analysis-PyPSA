import pandas as pd
import pytest
from energy_transition.eia923_ba_technology_coverage import audit

def test_qualification_and_withheld_per_ba():
    d=pd.DataFrame([
      {"ba_code":"CISO","fuel":"NG","source_rows":10,"qualified_rows":8,"qualified_annual_mwh":100.,"withheld_reported_annual_mwh":30.},
      {"ba_code":"BPAT","fuel":"WAT","source_rows":5,"qualified_rows":5,"qualified_annual_mwh":200.,"withheld_reported_annual_mwh":0.}])
    out=audit(d)
    gas=out[out.technology.eq("gas")].iloc[0]
    assert gas.row_qualification_fraction==.8
    assert gas.withheld_reported_mwh==30
    assert not out.usable_as_complete_ba_generation.any()

def test_duplicate_ba_fuel_fails():
    d=pd.DataFrame([{"ba_code":"CISO","fuel":"NG","source_rows":1,"qualified_rows":1,"qualified_annual_mwh":10.,"withheld_reported_annual_mwh":0.}]*2)
    with pytest.raises(ValueError,match="Duplicate"):
        audit(d)
