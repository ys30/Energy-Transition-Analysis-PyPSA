import pandas as pd
import pytest
from energy_transition.paper_t_source_figures import generate, validate, YEARS, STATES

def inputs():
    a=pd.DataFrame([{
        "year":y,"state":s,"best_nonwrap_offset":-3 if s in ("CA","NV","OR","WA") else -2,
        "best_nonwrap_mae_mw":17.0 if s=="ID" else .25,
        "second_best_mae_mw":50.0,"best_nonwrap_compared_hours":8757 if s in ("CA","NV","OR","WA") else 8758
    } for y in YEARS for s in STATES])
    b=pd.DataFrame([{
        "planning_year":y,"baseline_firsthalf_mae_mw":18.,
        "fixed_2030_transport_plus1_firsthalf_mae_mw":17. if y==2030 else 19.,
        "baseline_heldout_mae_mw":20.,
        "fixed_2030_transport_plus1_heldout_mae_mw":18.
    } for y in YEARS])
    return a,b

def test_accepted_33_plus_3_actual_artifact_shapes(tmp_path):
    a,b=inputs()
    m=generate(a,b,tmp_path)
    assert m["source_state_year_lag_pairs"]==33
    assert not m["EFS2020_physical_UTC_certified"]
    assert m["frozen_shift_first_half_improvements_mw"]["2040"]<0
    assert m["frozen_shift_heldout_improvements_mw"]["2040"]>0
    assert len(list(tmp_path.glob("*.svg")))==2
    assert len(list(tmp_path.glob("*.png")))==2
    assert all(p.stat().st_size>1000 for p in tmp_path.glob("*"))

def test_duplicate_source_pair_rejected():
    a,b=inputs()
    with pytest.raises(ValueError,match="Incomplete"):
        validate(pd.concat([a,a.iloc[[0]]]),b)

def test_missing_original_year_source_rejected():
    a,b=inputs()
    with pytest.raises(ValueError,match="Incomplete"):
        validate(a[a.year!=2050],b)

def test_invalid_runner_up_rejected():
    a,b=inputs()
    a.loc[0,"second_best_mae_mw"]=0.
    with pytest.raises(ValueError,match="Invalid"):
        validate(a,b)
