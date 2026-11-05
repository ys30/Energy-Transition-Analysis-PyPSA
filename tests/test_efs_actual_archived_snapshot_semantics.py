from types import SimpleNamespace
import pandas as pd
import pytest
from energy_transition.efs_actual_archived_snapshot_semantics import audit

def net(year):
    idx=pd.date_range(f"{year}-01-01",periods=8760,freq="h")
    n=SimpleNamespace()
    n.snapshots=idx
    n.loads=pd.DataFrame({"bus":[str(i) for i in range(20)],"p_set":[0.]*20},index=[f"L{i}" for i in range(20)])
    n.loads_t=SimpleNamespace(p_set=pd.DataFrame({f"L{i}":[float(i+1)]*8760 for i in range(19)},index=idx))
    return n

def test_naive_calendar_is_not_UTC_evidence():
    r=audit({y:net(y) for y in (2030,2040,2050)})
    assert len(r["archive_years"])==3
    assert r["archived_model_snapshots_timezone_aware_UTC"] is False
    assert r["independent_source_EFS_clock_DST_convention_verified"] is False
    assert r["joint_synchronous_2030_2050_OPF_admitted"] is False
    # 2040 is a leap year. Exactly 8760 contiguous hours therefore has
    # different month/day index than two nonleap 2030/2050 calendars.
    assert r["all_three_years_have_same_naive_month_day_hour_order"] is False

def test_missing_source_hour_fails():
    nets={y:net(y) for y in (2030,2040,2050)}
    nets[2030].snapshots=nets[2030].snapshots[:-1]
    with pytest.raises(ValueError,match="8760"):
        audit(nets)
