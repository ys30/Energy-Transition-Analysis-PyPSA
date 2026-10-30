import pandas as pd
import pytest
from energy_transition.storage_savings_attribution import audit

def test_shortage_attribution_reconciles_total_objective_difference():
    df=pd.DataFrame([{"season":"summer","duration_h":4.,
        "operating_savings_usd":218583308.,
        "avoided_unserved_mwh":22179.,
        "avoided_unserved_penalty_usd":221790000.,
        "non_shortage_dispatch_savings_usd":-3206692.,
        "unserved_mwh":315022.,"unserved_without_storage_mwh":337201.}])
    out=audit(df)
    assert bool(out.iloc[0].shortage_affected)
    assert out.iloc[0].interpretation=="shortage_penalty_scenario_not_market_arbitrage"

def test_inconsistent_attribution_fails():
    df=pd.DataFrame([{"season":"winter","duration_h":2.,
        "operating_savings_usd":100.,"avoided_unserved_mwh":0.,
        "avoided_unserved_penalty_usd":0.,
        "non_shortage_dispatch_savings_usd":10.,
        "unserved_mwh":0.,"unserved_without_storage_mwh":0.}])
    with pytest.raises(ValueError,match="reconcile"):
        audit(df)
