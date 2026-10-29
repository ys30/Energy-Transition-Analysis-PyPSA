import pandas as pd
import pytest
from energy_transition.generation_calibration_gate import validate_annual_generation

def test_incomplete_ba_excluded_without_imputation():
    data=pd.DataFrame({"ba_code":["CISO","BPAT"],"complete":[False,True],
      "missing_timestamp_hours":[24,0],"missing_value_hours":[0,0],"outside_year_hours":[0,0]})
    result=validate_annual_generation(data,["CISO","BPAT"])
    assert result.set_index("ba_code").loc["CISO","calibration_status"]=="incomplete_exclude"
    assert bool(result.set_index("ba_code").loc["BPAT","ready_for_annual_calibration"])

def test_missing_required_ba_is_error():
    df=pd.DataFrame({"ba_code":["BPAT"],"complete":[True],"missing_timestamp_hours":[0],
                     "missing_value_hours":[0],"outside_year_hours":[0]})
    with pytest.raises(ValueError,match="Missing requested"):
        validate_annual_generation(df,["CISO","BPAT"])
