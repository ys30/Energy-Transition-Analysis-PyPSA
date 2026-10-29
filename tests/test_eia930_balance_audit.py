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
