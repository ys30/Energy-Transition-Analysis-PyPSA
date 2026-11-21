"""Guard against treating daily transfer potential or BA-state shape as actual LP validation."""
import numpy as np
import pytest
from energy_transition.paper_s_daily_transfer_proxy_and_ipco_shape import (
    daily_proxy,shape_metrics,chronological_daily_policy,chronological_comparison
)

def test_daily_transfer_requires_surplus_and_deficit():
    x=np.ones(8760)*100
    zero=daily_proxy(x,np.zeros(8760),ratio=1.5)
    assert zero.incremental_4to8_daily_proxy_mwh.sum()==0
    full=daily_proxy(x,np.ones(8760),ratio=1.5)
    assert full.incremental_4to8_daily_proxy_mwh.sum()==0

def test_daily_proxy_nonzero_only_above_four_hour_deliverable_capacity():
    load=np.ones(8760)*100.
    cf=np.tile(np.r_[np.ones(12),np.zeros(12)],365)
    out=daily_proxy(load,cf,ratio=2.0)
    assert len(out)==365
    assert out.incremental_4to8_daily_proxy_mwh.ge(0).all()
    assert out.incremental_4to8_daily_proxy_mwh.gt(0).all()
    assert out.incremental_4to8_daily_proxy_mwh.le(8*25*np.sqrt(.9)-4*25*np.sqrt(.9)+1e-6).all()

def test_shape_is_scale_invariant_and_not_affected_by_capacity_denominator():
    x=np.tile(np.array([1.,2.,3.,4.]),300)
    a=shape_metrics(x,10*x)
    assert a["pearson"]==pytest.approx(1.,abs=1e-12)
    assert a["normalized_MAE"]==pytest.approx(0,abs=1e-12)

def test_shape_zero_mean_fails_closed():
    with pytest.raises(ValueError):
        shape_metrics(np.zeros(1200),np.ones(1200))

def test_chronological_zero_when_all_surplus_follows_deficit():
    load=np.full(8760,100.)
    # First 12 hours deficit, final 12 surplus; no carryover between days.
    cf=np.tile(np.r_[np.zeros(12),np.ones(12)],365)
    x=chronological_comparison(load,cf,ratio=2.)
    assert x.four_h_feasible_delivered_mwh.sum()==pytest.approx(0.)
    assert x.eight_h_feasible_delivered_mwh.sum()==pytest.approx(0.)
    # The old order-blind indicator is nonzero, demonstrating the caveat.
    assert daily_proxy(load,cf,ratio=2.).incremental_4to8_daily_proxy_mwh.sum()>0

def test_chronological_capacity_delta_when_surplus_precedes_deficit():
    load=np.full(8760,100.)
    cf=np.tile(np.r_[np.ones(12),np.zeros(12)],365)
    x=chronological_comparison(load,cf,ratio=2.)
    assert len(x)==365
    assert x.incremental_eight_minus_four_policy_delivered_mwh.gt(0).all()
    assert x.eight_h_feasible_delivered_mwh.ge(x.four_h_feasible_delivered_mwh).all()
    assert np.isfinite(x.to_numpy(dtype=float)).all()

def test_chronological_rejects_negative_and_nonfinite_cf():
    load=np.ones(8760)*100
    cf=np.ones(8760)*.5
    cf[3]=np.nan
    with pytest.raises(ValueError):
        chronological_daily_policy(load,cf)
