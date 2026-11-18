"""Synthetic tests for 2023 H2 hourly EIA-930 BA coverage, no source claims."""
import pandas as pd
import pytest
from energy_transition.paper_s_eia930_2023h2_full_BA_coverage import (
    START,END,EXPECTED_HOURS,coverage,BAS,TECHS
)

def test_full_2023H2_UTC_calendar_4416_hours():
    assert EXPECTED_HOURS == 4416
    assert END-START == pd.Timedelta(hours=4416)

def test_coverage_distinguishes_missing_hour_and_missing_reported_mw():
    frames=[]
    for ba in BAS:
        for fuel in TECHS:
            frames.append({"ba_code":ba,"fuel":fuel,
                           "utc_hour_end":START,
                           "reported_mw":1.,"adjusted_mw":2.,"imputed_mw":float("nan")})
            frames.append({"ba_code":ba,"fuel":fuel,
                           "utc_hour_end":START+pd.Timedelta(hours=1),
                           "reported_mw":float("nan"),"adjusted_mw":2.,
                           "imputed_mw":float("nan")})
    d=pd.DataFrame(frames)
    s,m,missing=coverage(d)
    assert len(s)==8 and len(m)==48
    assert len(missing)==8*(EXPECTED_HOURS-2)
    assert s.source_timestamp_count.eq(2).all()
    assert s.missing_source_timestamp_count.eq(EXPECTED_HOURS-2).all()
    assert s.reported_mw_null_on_present_timestamp.eq(1).all()
    assert s.reported_mw_present_count.eq(1).all()
    assert not s.BA_equals_state.any()
    assert not s.observed_CF_normalization_validated.any()
