import pandas as pd
import pytest
from energy_transition.pudl_eia930_stage_audit import evaluate, STAGES

def test_pudl_stage_balance_preserves_distinct_series_and_missingness():
    cols={"datetime_utc":pd.date_range("2024-01-01",periods=2,freq="h",tz="UTC"),
          "balancing_authority_code_eia":["BPAT","BPAT"]}
    for stage in STAGES:
        cols[f"demand_{stage}_mwh"]=[100.,100.]
        cols[f"net_generation_{stage}_mwh"]=[90.,90.]
        cols[f"interchange_{stage}_mwh"]=[-10.,-10.]
    cols["interchange_reported_mwh"][1]=None
    cols["interchange_adjusted_mwh"]=[10.,10.]
    result=evaluate(pd.DataFrame(cols),bas=["BPAT"])
    reported=result[result.stage.eq("reported")].iloc[0]
    adjusted=result[result.stage.eq("adjusted")].iloc[0]
    assert reported.complete_hours==1
    assert reported.residual_sum_mwh==0
    assert adjusted.complete_hours==2
    assert adjusted.residual_sum_mwh==40

def test_pudl_stage_rejects_missing_field():
    with pytest.raises(ValueError,match="missing columns"):
        evaluate(pd.DataFrame({"datetime_utc":[],"balancing_authority_code_eia":[]}))
