"""Guard numeric EIA-860 / EIA-923 BA-level screening against silent string sums."""
import json
import pandas as pd
import pytest
from energy_transition.eia860_eia923_ba_screen import audit


def run_case(tmp_path, capacity, generation):
    cap=tmp_path/"capacity.csv";gen=tmp_path/"generation.csv";out=tmp_path/"screen.csv"
    pd.DataFrame(capacity).to_csv(cap,index=False)
    pd.DataFrame(generation).to_csv(gen,index=False)
    audit(cap,gen,out)
    return pd.read_csv(out),json.loads(out.with_suffix(".json").read_text())


def test_ba_aggregation_uses_numeric_arithmetic(tmp_path):
    result,report=run_case(tmp_path,
      [{"ba_code":"BPAT","official_nameplate_mw":"100"},
       {"ba_code":"BPAT","official_nameplate_mw":"200"}],
      [{"ba_code":"BPAT","qualified_annual_mwh":"1000","withheld_reported_annual_mwh":"30"},
       {"ba_code":"BPAT","qualified_annual_mwh":"500","withheld_reported_annual_mwh":"20"}])
    assert result.iloc[0].official_nameplate_mw==300
    assert result.iloc[0].qualified_annual_mwh==1500
    assert result.iloc[0].withheld_reported_annual_mwh==50
    assert result.iloc[0].calibrated_capacity_factor==False
    assert report["full_ba_capacity_factor_verified"] is False


def test_invalid_numeric_capacity_fails_closed(tmp_path):
    with pytest.raises(ValueError,match="invalid numeric"):
        run_case(tmp_path,[{"ba_code":"BPAT","official_nameplate_mw":"unknown"}],
          [{"ba_code":"BPAT","qualified_annual_mwh":10,"withheld_reported_annual_mwh":0}])


def test_missing_ba_rejected(tmp_path):
    with pytest.raises(ValueError,match="BA identifiers"):
        run_case(tmp_path,[{"ba_code":None,"official_nameplate_mw":100}],
          [{"ba_code":"BPAT","qualified_annual_mwh":10,"withheld_reported_annual_mwh":0}])


@pytest.mark.parametrize("capacity_rows", [
    [{"ba_code":"BPAT","official_nameplate_mw":0}],
    [{"ba_code":"CISO","official_nameplate_mw":100}],
])
def test_screen_rejects_zero_or_unmatched_capacity_denominator(tmp_path, capacity_rows):
    with pytest.raises(ValueError,match="Missing or nonpositive EIA860 BA nameplate"):
        run_case(tmp_path,capacity_rows,
          [{"ba_code":"BPAT","qualified_annual_mwh":10,"withheld_reported_annual_mwh":0}])
