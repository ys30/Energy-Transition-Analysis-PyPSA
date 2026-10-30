import pandas as pd
import pytest
from energy_transition.eia2024_technology_utilization_screen import calculate

def test_utilization_retains_qualification_flag_and_never_claims_calibration():
    c=pd.DataFrame([{"ba_code":"CISO","fuel":"NG","capacity_mw":100.},
      {"ba_code":"BPAT","fuel":"WAT","capacity_mw":200.}])
    q=pd.DataFrame([{"ba_code":"CISO","fuel":"NG","qualified_annual_mwh":87840.,
      "source_rows":4,"qualified_rows":3}])
    x=calculate(c,q)
    ng=x[x.technology.eq("gas")].iloc[0]
    assert ng.qualified_generation_over_nameplate_hours==.1
    assert not bool(ng.qualified_rows_complete)
    assert not x.ratio_calibrated.any()
    assert x[x.technology.eq("hydro")].qualified_generation_over_nameplate_hours.isna().all()

def test_duplicate_source_fuel_rejected():
    c=pd.DataFrame([{"ba_code":"CISO","fuel":"NG","capacity_mw":100.}]*2)
    q=pd.DataFrame(columns=["ba_code","fuel","qualified_annual_mwh","source_rows","qualified_rows"])
    with pytest.raises(ValueError,match="Duplicate"):
        calculate(c,q)
