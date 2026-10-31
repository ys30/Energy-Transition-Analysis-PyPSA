import pandas as pd
import pytest
from energy_transition.eia930_gap_windows import gap_windows
from energy_transition.eia930_gap_window_validation import verify


def test_validates_exact_intervals_and_rejects_omission():
    h=pd.DataFrame({"respondent":["CISO"]*4,
      "period":pd.date_range("2024-01-01",periods=4,freq="h",tz="UTC"),
      "demand":[1]*4,"generation":[1,None,1,1],
      "interchange":[0,None,None,0]})
    gaps=gap_windows(h)
    outcome=verify(h,gaps)
    assert outcome["verified"]
    assert outcome["missing_hours_by_ba_field"]["CISO"]=={
        "demand":0,"generation":1,"interchange":2}
    with pytest.raises(ValueError,match="total mismatch"):
        verify(h,gaps.loc[~gaps.field.eq("generation")])


def test_rejects_window_with_false_missing_hour():
    h=pd.DataFrame({"respondent":["BPAT"]*3,
      "period":pd.date_range("2024-01-01",periods=3,freq="h",tz="UTC"),
      "demand":[1]*3,"generation":[1]*3,"interchange":[0,None,0]})
    gaps=gap_windows(h)
    gaps.loc[0,"end_utc_exclusive"]="2024-01-01T03:00:00+00:00"
    gaps.loc[0,"missing_hours"]=2
    with pytest.raises(ValueError,match="does not match"):
        verify(h,gaps)
