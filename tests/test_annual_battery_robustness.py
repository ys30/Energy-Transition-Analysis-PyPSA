import pandas as pd
import pytest
from energy_transition.annual_battery_robustness import CASES,check_grid,run

def test_cases_are_distinct_and_controlled():
    assert len(CASES)==4
    assert len({case[0] for case in CASES})==4
    assert CASES[0][1:]==(55000.,20000.,10000.,False)
    assert CASES[-1][-1] is True

def test_reject_incomplete_annual_renewables():
    d=pd.DataFrame(columns=["period","respondent","value"])
    s=pd.DataFrame([{"method":"linear","period":"2024-01-01T00:00:00Z",
      "respondent":"CISO","fueltype":"SUN","value_mwh":1.,"is_imputed":False}])
    with pytest.raises(ValueError,match="Incomplete"):
        check_grid(d,s)
