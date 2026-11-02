"""Check plant-universe overlap uses strict EIA-923 monthly certification."""
import json
import pandas as pd
import pytest
from energy_transition.eia860_eia923_plant_universe_audit import run


def test_plant_overlap_excludes_incomplete_months(tmp_path):
    e860=tmp_path/"e860.csv"; e923=tmp_path/"e923.csv"; out=tmp_path/"audit.csv"
    pd.DataFrame([{"plant_id":"10","generator_id":"A","status":"OP",
      "crosswalk_status":"matched","ba_code":"BPAT","capacity_mw":100.0}]).to_csv(e860,index=False)
    pd.DataFrame([
      {"plant_id":"10","ba_code":"BPAT","reconciles":True,"fully_numeric":True,
       "annual_reported_mwh":90.0,"missing_months":0},
      {"plant_id":"20","ba_code":"BPAT","reconciles":True,"fully_numeric":True,
       "annual_reported_mwh":70.0,"missing_months":2},
    ]).to_csv(e923,index=False)
    run(e860,e923,out)
    audit=pd.read_csv(out).iloc[0]
    assert audit.eia923_reported_plants == 2
    assert audit.eia923_qualified_plants == 1
    assert audit.qualified_plant_id_overlap == 1
    assert audit.qualified_eia923_mwh_on_common_plant_ids == 90.0
    assert audit.qualified_eia923_mwh_not_on_eia860_operating_plant_ids == 0.0
    assert json.loads(out.with_suffix(".json").read_text())["full_plant_and_generator_coverage_verified"] is False


def test_plant_universe_rejects_missing_month_coverage_field(tmp_path):
    e860=tmp_path/"e860.csv";e923=tmp_path/"e923.csv"
    pd.DataFrame([{"plant_id":"10","generator_id":"A","status":"OP",
      "crosswalk_status":"matched","ba_code":"BPAT","capacity_mw":100.0}]).to_csv(e860,index=False)
    pd.DataFrame([{"plant_id":"10","ba_code":"BPAT","reconciles":True,
      "fully_numeric":True,"annual_reported_mwh":90.0}]).to_csv(e923,index=False)
    with pytest.raises(ValueError,match="monthly coverage column"):
        run(e860,e923,tmp_path/"out.csv")
