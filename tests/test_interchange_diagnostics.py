import pandas as pd
from energy_transition.interchange_diagnostics import diagnose

def test_interchange_diagnostics_use_only_common_hour_data():
    ts=pd.date_range("2024-01-01",periods=3,freq="h",tz="UTC")
    df=pd.DataFrame({
      "respondent":["BPAT"]*3,"period":ts,
      "demand":[100.,100.,100.],
      "generation":[80.,80.,None],
      "interchange":[-20.,10.,10.]})
    monthly,by_ba=diagnose(df)
    m=monthly.iloc[0]
    assert m.expected_hours==3
    assert m.common_hours==2
    assert m.coverage_share==2/3
    assert m.sum_official_residual_mwh==30
    assert m.positive_residual_hours==1
    assert by_ba.iloc[0].sum_residual_mwh==30
