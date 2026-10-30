import pandas as pd
from energy_transition.eia930_balance_audit import balance_audit

def test_eia930_balance_keeps_missing_hours_and_both_signs():
    hours=pd.date_range("2024-01-01",periods=2,freq="h",tz="UTC")
    d=pd.DataFrame({"period":hours,"respondent":["CISO"]*2,"value":[100.,100.]})
    ng=pd.DataFrame({"period":hours[:1],"respondent":["CISO"],"value":[80.]})
    ti=pd.DataFrame({"period":hours,"respondent":["CISO"]*2,"value":[20.,20.]})
    frame,audit=balance_audit(d,ng,ti,["CISO"],2024)
    row=audit.iloc[0]
    assert row.expected_hours==8784
    assert row.complete_triples==1
    assert row.missing_generation==8783
    assert row.mae_d_minus_ng_minus_ti==0
    assert row.mae_d_minus_ng_plus_ti==40
    assert row.complete_triple_share==1/8784
    assert row.common_residual_plus_mwh==40
    assert row.accounting_gate=="review_required"
    assert row.official_balance_residual_mwh==40
    assert row.official_balance_mae_mw==40

def test_monthly_residual_uses_only_complete_triples():
    from energy_transition.eia930_balance_audit import monthly_balance_audit
    hours=pd.date_range("2024-01-01",periods=2,freq="h",tz="UTC")
    frame=pd.DataFrame({
        "respondent":["BPAT","BPAT"],"period":hours,
        "demand":[100.,200.],"generation":[80.,None],"interchange":[-20.,-30.],
        "residual_d_minus_ng_plus_ti":[0.,None]
    })
    monthly=monthly_balance_audit(frame)
    assert monthly.iloc[0].common_hours==1
    assert monthly.iloc[0].missing_triples==1
    assert monthly.iloc[0].official_residual_mwh==0
    assert monthly.iloc[0].quality_flag=="review_required"


def test_balance_audit_rejects_duplicate_ba_hours():
    import pytest
    hour=pd.Timestamp("2024-01-01T00:00:00Z")
    d=pd.DataFrame({"respondent":["CISO","CISO"],"period":[hour,hour],"value":[10.,11.]})
    single=pd.DataFrame({"respondent":["CISO"],"period":[hour],"value":[10.]})
    with pytest.raises(ValueError,match="duplicate BA-hour"):
        balance_audit(d,single,single,["CISO"],2024)


def test_balance_audit_preserves_missing_and_rejects_infinite_measurements():
    import pytest
    hour=pd.Timestamp("2024-01-01T00:00:00Z")
    missing=pd.DataFrame({"respondent":["CISO"],"period":[hour],"value":[float("nan")]})
    good=pd.DataFrame({"respondent":["CISO"],"period":[hour],"value":[10.]})
    frame,summary=balance_audit(missing,good,good,["CISO"],2024)
    assert pd.isna(frame.loc[0,"demand"])
    assert summary.iloc[0].complete_triples==0
    assert summary.iloc[0].accounting_gate=="review_required"
    infinite=good.copy()
    infinite.loc[0,"value"]=float("inf")
    with pytest.raises(ValueError,match="infinite"):
        balance_audit(good,infinite,good,["CISO"],2024)


def test_zero_demand_cannot_pass_annual_or_monthly_accounting_gate():
    from energy_transition.eia930_balance_audit import monthly_balance_audit
    hours=pd.date_range("2024-01-01","2025-01-01",freq="h",inclusive="left",tz="UTC")
    zero=pd.DataFrame({"respondent":"CISO","period":hours,"value":0.0})
    hourly,summary=balance_audit(zero,zero,zero,["CISO"],2024)
    assert summary.iloc[0].complete_triples==8784
    assert summary.iloc[0].accounting_gate=="review_required"
    monthly=monthly_balance_audit(hourly)
    assert len(monthly)==12
    assert (monthly.quality_flag=="review_required").all()


def test_balanced_positive_load_remains_screening_only():
    hours=pd.date_range("2024-01-01","2025-01-01",freq="h",inclusive="left",tz="UTC")
    d=pd.DataFrame({"respondent":"CISO","period":hours,"value":100.0})
    ng=pd.DataFrame({"respondent":"CISO","period":hours,"value":80.0})
    ti=pd.DataFrame({"respondent":"CISO","period":hours,"value":-20.0})
    _,summary=balance_audit(d,ng,ti,["CISO"],2024)
    assert summary.iloc[0].accounting_gate=="screening_only_not_verified"


def test_monthly_signed_residual_cancellation_cannot_hide_hourly_imbalance():
    from energy_transition.eia930_balance_audit import monthly_balance_audit
    hours=pd.date_range("2024-01-01","2024-02-01",freq="h",inclusive="left",tz="UTC")
    demand=pd.DataFrame({"respondent":"CISO","period":hours,"value":100.0})
    generation=demand.copy()
    generation["value"]=[80.0 if i%2==0 else 120.0 for i in range(len(hours))]
    interchange=demand.copy()
    interchange["value"]=0.0
    hourly,_=balance_audit(demand,generation,interchange,["CISO"],2024)
    monthly=monthly_balance_audit(hourly)
    jan=monthly[monthly.month=="2024-01"].iloc[0]
    assert jan.official_residual_mwh==0.0
    assert jan.mae_share_of_load==0.2
    assert jan.quality_flag=="review_required"


def test_monthly_tail_metrics_detect_extreme_hour_even_with_low_mae():
    from energy_transition.eia930_balance_audit import monthly_balance_audit
    hours=pd.date_range("2024-01-01","2024-02-01",freq="h",inclusive="left",tz="UTC")
    demand=pd.DataFrame({"respondent":"CISO","period":hours,"value":100.0})
    generation=demand.copy()
    generation.loc[0,"value"]=0.0
    interchange=demand.copy()
    interchange["value"]=0.0
    hourly,_=balance_audit(demand,generation,interchange,["CISO"],2024)
    jan=monthly_balance_audit(hourly).iloc[0]
    assert jan.max_absolute_residual_mw==100.0
    assert jan.p95_absolute_residual_mw==0.0
    assert jan.mae_share_of_load < 0.01
    assert jan.quality_flag=="screening_only_not_verified"
