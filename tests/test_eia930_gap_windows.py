import pandas as pd
import pytest
from energy_transition.eia930_gap_windows import gap_windows


def test_gap_windows_reports_exact_contiguous_utc_intervals():
    df=pd.DataFrame({"respondent":["CISO"]*5,
       "period":pd.date_range("2024-03-01",periods=5,freq="h",tz="UTC"),
       "demand":[1]*5,"generation":[1,None,None,1,1],
       "interchange":[0,None,None,None,0]})
    gaps=gap_windows(df)
    ng=gaps.loc[gaps.field.eq("generation")].iloc[0]
    ti=gaps.loc[gaps.field.eq("interchange")].iloc[0]
    assert ng.missing_hours==2 and ng.start_utc=="2024-03-01T01:00:00+00:00"
    assert ng.end_utc_exclusive=="2024-03-01T03:00:00+00:00"
    assert ti.missing_hours==3
    assert ti.end_utc_exclusive=="2024-03-01T04:00:00+00:00"


def test_gap_windows_refuses_discontinuous_source_index():
    df=pd.DataFrame({"respondent":["BPAT"]*2,
       "period":["2024-01-01T00:00:00Z","2024-01-01T02:00:00Z"],
       "demand":[1,1],"generation":[1,1],"interchange":[None,None]})
    with pytest.raises(ValueError,match="Non-contiguous"):
        gap_windows(df)
