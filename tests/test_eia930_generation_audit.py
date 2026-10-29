import pandas as pd
from energy_transition.eia930_generation_audit import summarize_net_generation

def test_generation_audit_keeps_negative_and_missing():
    f=pd.DataFrame({"period":pd.to_datetime(["2024-01-01T00:00Z","2024-01-01T01:00Z","2024-01-01T02:00Z"]),
      "respondent":["CISO"]*3,"value":[25.0,-2.0,float("nan")]})
    s=summarize_net_generation(f,2024,["CISO"])
    row=s.iloc[0]
    assert row.negative_value_hours==1
    assert row.missing_value_hours==1
    assert row.reported_net_generation_mwh_nonmissing_only==23.0
    assert not bool(row.complete)
