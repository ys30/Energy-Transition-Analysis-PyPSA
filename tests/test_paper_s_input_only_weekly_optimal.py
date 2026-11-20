"""Source-independent physical invariants for 168h renewable-only mechanism."""
import numpy as np
import pandas as pd
import pytest
from energy_transition.paper_s_input_only_weekly_optimal import transport,one_week,report

def test_cross_midnight_only_week_can_transfer():
    surplus=np.zeros(168);deficit=np.zeros(168)
    surplus[20:24]=100
    deficit[24:28]=100
    daily=transport(surplus,deficit,25,8,daily=True)
    weekly=transport(surplus,deficit,25,8,daily=False)
    assert daily["delivered_mwh"]==pytest.approx(0,abs=1e-8)
    assert weekly["delivered_mwh"]==pytest.approx(90,abs=1e-6)
    assert weekly["equality_residual_mwh"]<1e-5

def test_4h_and_8h_with_identical_source_and_horizon():
    load=np.full(168,100.)
    cf=np.tile(np.r_[np.ones(12),np.zeros(12)],7)
    r=one_week(load,cf,2.0,100.)
    assert r["daily_incremental_4to8_mwh"]>0
    assert r["weekly_incremental_4to8_mwh"]>0
    for d in (4,8):
        assert r[f"weekly_{d}h_delivered_mwh"]+1e-5>=r[f"daily_{d}h_delivered_mwh"]
    assert r["weekly_equality_residual_mwh"]<1e-5

def test_surplus_after_deficit_no_false_cross_day_terminal_delivery():
    load=np.full(168,100.)
    cf=np.tile(np.r_[np.zeros(12),np.ones(12)],7)
    r=one_week(load,cf,2.0,100.)
    assert r["weekly_4h_delivered_mwh"]>=0
    assert r["weekly_8h_delivered_mwh"]>=r["weekly_4h_delivered_mwh"]-1e-5
    assert r["weekly_8h_delivered_mwh"]>=r["daily_8h_delivered_mwh"]-1e-5

def test_bad_168h_inputs_fail_closed():
    with pytest.raises(ValueError):
        one_week(np.ones(167),np.ones(167),1.5,100.)
    with pytest.raises(ValueError):
        transport(np.array([-1.]*24),np.zeros(24),25,4)
    with pytest.raises(ValueError):
        transport(np.ones(24),np.ones(24),25,4)
    with pytest.raises(ValueError):
        report(pd.DataFrame(),pd.DataFrame())
