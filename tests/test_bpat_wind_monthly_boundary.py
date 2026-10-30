import pandas as pd
from energy_transition.bpat_wind_monthly_boundary import compare

def test_monthly_comparison_preserves_gaps_and_signed_values():
    monthly=pd.DataFrame([{"ba_code":"BPAT","fuel":"WND","month":1,"netgen_mwh":100.}])
    hourly=pd.DataFrame([{"respondent":"BPAT","fueltype":"WND","period":"2024-01-01T00:00:00Z","value":-2.}])
    out=compare(monthly,hourly)
    jan=out[out.month.eq(1)].iloc[0]
    assert jan.eia930_signed_wind_mwh==-2
    assert jan.eia923_observed_plant_month_wind_mwh==100
    assert jan.difference_eia923_minus_eia930_mwh==102
    assert jan.eia930_missing_or_null_hours==743
    assert out.expected_utc_hours.sum()==8784
