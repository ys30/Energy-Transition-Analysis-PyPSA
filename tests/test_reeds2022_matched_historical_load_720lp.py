"""Structural and calendar tests use synthetic records, not paper results."""
import numpy as np
import pandas as pd
import pytest
from energy_transition.reeds2022_matched_historical_load_720lp import (
    WEATHER_YEARS,STATES,DESIGNS,DURATIONS,LOAD_MODES,
    align_original_historical_load,analyze,
)

def test_load_calendar_nonleap_and_leap():
    for year in (2011,2012,2016):
        t=pd.date_range(f"{year}-01-01",periods=8760,freq="h")
        data=np.arange(8760,dtype=float)+1
        result,meta=align_original_historical_load(t,data)
        assert len(result)==8760
        assert meta["interpolated_feb29_hours"]==(0 if year in (2012,2016) else 24)
        assert meta["omitted_dec31_hours"]==(0 if year in (2012,2016) else 24)
        assert np.isclose(result.sum()-data.sum(),meta["calendar_substitution_mwh"])


def test_same_weather_complete_design():
    rows=[]
    for y in WEATHER_YEARS:
        for st in STATES:
            for scheme in DESIGNS:
                for mode in LOAD_MODES:
                    for h in DURATIONS:
                        rows.append({"weather_year":y,"state":st,
                            "county_weight_scheme":scheme,"load_mode":mode,
                            "battery_duration_h":h,
                            "objective_illustrative_variable_usd":20000-h*100,
                            "storage_capacity_mwh":float(h*10),
                            "solver_status":"optimal","max_equality_residual_mwh":1e-12})
    frame=pd.DataFrame(rows)
    pairs,geo=analyze(frame)
    assert len(frame)==720 and len(pairs)==240 and len(geo)==120
    with pytest.raises(ValueError,match="Exactly 720 unique"):
        analyze(frame.iloc[:-1])
