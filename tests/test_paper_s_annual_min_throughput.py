import pandas as pd
import pytest
from energy_transition.paper_s_annual_min_throughput import compare,SELECTED

def test_selected_window_locked():
    assert SELECTED=="middle_4001_4168"

def test_missing_original_hours_rejected():
    a=pd.DataFrame({"synthetic_supply_shape":["flat_50pct"],
         "battery_duration_h":[0],"local_hour_id":[1]})
    with pytest.raises(ValueError,match="8760"):
        compare(a,pd.DataFrame(),pd.DataFrame(),pd.DataFrame(),1)
