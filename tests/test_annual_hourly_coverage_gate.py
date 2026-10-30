import pandas as pd
import pytest
from energy_transition.annual_hourly_coverage_gate import audit_annual_inputs

def test_leap_year_gate_rejects_incomplete_series_without_filling():
    h=pd.Timestamp("2024-01-01",tz="UTC")
    d=pd.DataFrame([{"period":h,"respondent":ba,"value":100.} for ba in ("CISO","BPAT")])
    r=pd.DataFrame([{"period":h,"respondent":ba,"fueltype":f,"value":-2. if f=="SUN" else 5.}
         for ba in ("CISO","BPAT") for f in ("SUN","WND")])
    x=audit_annual_inputs(d,r)
    assert x["expected_utc_hours"]==8784
    assert x["aligned_complete_hours"]==1
    assert x["full_year_optimization_permitted"] is False
    assert x["longest_aligned_contiguous_run"]["hours"]==1

def test_duplicate_demand_rejected():
    d=pd.DataFrame([{"period":"2024-01-01T00:00Z","respondent":"CISO","value":100.}]*2)
    r=pd.DataFrame(columns=["period","respondent","fueltype","value"])
    with pytest.raises(ValueError,match="Duplicate demand"):
        audit_annual_inputs(d,r)
