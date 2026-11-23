"""Source-free tests: monthly BA population scope is not a measured capacity factor."""
import numpy as np
import pandas as pd
import pytest
from energy_transition.paper_s_eia860m_2023_12_month_BA_roster_audit import (
    BAS,MONTHS,comparison,
)

def fake_summary():
    return pd.DataFrame([
        {"month":f"2023-{m:02d}","ba_code":b,"fuel":f,
         "OP_nameplate_mw":100.} for m in range(1,13)
         for b in BAS for f in ("wind","solar")
    ])

def test_all_12_months_defined():
    assert len(MONTHS)==12
    assert MONTHS[6]=="july"

def test_comparison_does_not_claim_valid_capacity_factor():
    summary=fake_summary()
    obs=pd.DataFrame([
      {"utc_hour_end":"2023-07-03T18:00:00Z","ba_code":"PSCO",
       "fuel":"solar","reported_mw":121.,"adjusted_mw":99.},
      {"utc_hour_end":"2023-07-03T19:00:00Z","ba_code":"PSCO",
       "fuel":"solar","reported_mw":np.nan,"adjusted_mw":110.},
    ])
    s=comparison(summary,obs)
    assert len(s)==192
    r=s[(s.month=="2023-07")&(s.ba_code=="PSCO")&(s.fuel=="solar")]
    assert r.loc[r.source_MW_variant.eq("reported_mw"),"hours_BA_MW_above_month_OP_candidate"].iloc[0]==1
    assert r.loc[r.source_MW_variant.eq("adjusted_mw"),"hours_BA_MW_above_month_OP_candidate"].iloc[0]==1
    assert not s.BA_equals_state.any()
    assert not s.actual_measured_CF.any()

def test_duplicate_hour_raises():
    d=pd.DataFrame([{"utc_hour_end":"2023-07-01T00:00:00Z",
                     "ba_code":"PSCO","fuel":"solar",
                     "reported_mw":3.,"adjusted_mw":3.}]*2)
    with pytest.raises(ValueError,match="Duplicate"):
        comparison(fake_summary(),d)
