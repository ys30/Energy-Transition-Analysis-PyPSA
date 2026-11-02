"""Protect EIA-860 candidate-bus provenance against CSV boolean coercion."""
import json
import pandas as pd
import pytest
from energy_transition.eia860_plant_bus_distance_qc import main
import sys


def execute(tmp_path, monkeypatch, verified, distance=12):
    source=tmp_path/"candidates.csv"
    pd.DataFrame([{"plant_id":"1","state":"NM","nearest_candidate_bus":"100",
      "distance_km":distance,"assignment_status":"geographic_candidate_only",
      "electrical_connection_verified":verified}]).to_csv(source,index=False)
    monkeypatch.setattr(sys,"argv",["program","--candidates",str(source),
      "--out-dir",str(tmp_path/"out"),"--year","2024"])
    main()
    return json.loads((tmp_path/"out"/"eia860_plant_bus_distance_qc_2024.json").read_text())


def test_geographic_only_false_is_not_approved(tmp_path,monkeypatch):
    result=execute(tmp_path,monkeypatch,False)
    assert result["electrical_connections_verified"]==0
    assert result["plant_bus_assignment_approved"] is False


@pytest.mark.parametrize("flag", [True,"unknown",None])
def test_electrical_flags_fail_closed(tmp_path,monkeypatch,flag):
    with pytest.raises(ValueError,match="electrical connection|electrical connections"):
        execute(tmp_path,monkeypatch,flag)


@pytest.mark.parametrize("bad_distance", ["inf",-1,"not-a-number"])
def test_invalid_distance_rejected(tmp_path,monkeypatch,bad_distance):
    with pytest.raises(ValueError,match="Invalid distances"):
        execute(tmp_path,monkeypatch,False,bad_distance)
