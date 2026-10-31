import pandas as pd
import pytest
from energy_transition.eia930_ciso_gap_recheck import audit_gap, GAP_START


def test_gap_audit_distinguishes_null_from_missing_timestamp():
    frame=pd.DataFrame({"respondent":["CISO","CISO"],
                        "period":[GAP_START,GAP_START+pd.Timedelta(hours=1)],
                        "value":[100.0,None]})
    report=audit_gap(frame)
    assert report["expected_hours"]==24
    assert report["returned_timestamp_hours"]==2
    assert report["returned_nonnull_hours"]==1
    assert report["returned_null_hours"]==1
    assert report["missing_timestamp_hours"]==22
    assert report["missing_or_null_hours"]==23


def test_gap_audit_rejects_duplicate_period():
    frame=pd.DataFrame({"respondent":["CISO","CISO"],
                        "period":[GAP_START,GAP_START],
                        "value":[10.0,11.0]})
    with pytest.raises(ValueError,match="Duplicate"):
        audit_gap(frame)
