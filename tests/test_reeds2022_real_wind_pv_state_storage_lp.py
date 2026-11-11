import numpy as np
import pandas as pd
from energy_transition.reeds2022_real_wind_pv_state_storage_lp import (
    strict_pure_ba_crosswalk,STATES,SAMPLE_MODES
)
def test_only_wholly_within_state_bas_allowed():
    a=pd.DataFrame({"FIPS":["04001","04003","08001","08003","16001","56001"],
                    "ba":["p1","p1","p2","p2","p3","p3"],
                    "state":["AZ","AZ","CO","CO","ID","WY"]})
    pure,c=strict_pure_ba_crosswalk(a)
    assert pure["AZ"]=={"p1"} and pure["CO"]=={"p2"}
    assert pure["ID"]==set() and pure["WY"]==set()
    assert c.loc[c.state.eq("ID"),"source_counties_in_pure_state_BAs"].iloc[0]==0
def test_fixed_8hour_model_assumptions():
    assert STATES==("AZ","CO","ID","WY")
    assert set(SAMPLE_MODES)=={"trapezoidal_previous_instant","instantaneous_end_label"}
