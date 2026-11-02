"""Unit-test Colstrip identity lookup without claiming a source network tie."""
from types import SimpleNamespace
from unittest.mock import patch
import pandas as pd
from energy_transition.colstrip_original_bus_identity_audit import inspect

def test_named_colstrip_is_only_candidate(tmp_path):
    buses=pd.DataFrame({"v_nom":[500,230],"substation_name":["Colstrip Substation","Other"]},index=["model_bus_1","model_bus_2"])
    lines=pd.DataFrame({"bus0":["model_bus_1"],"bus1":["model_bus_2"]})
    n=SimpleNamespace(buses=buses,lines=lines)
    with patch("pypsa.Network",return_value=n):
        result=inspect(tmp_path/"network.nc",tmp_path/"report.json")
    assert result["candidate_count"]==1
    assert result["explicit_colstrip_name_candidates"][0]["bus_id"]=="model_bus_1"
    assert result["explicit_colstrip_name_candidates"][0]["connected_lines"]==1
    assert result["independently_verified_eia_generator_bus_ties"]==0

def test_no_named_substation_no_approved_ties(tmp_path):
    buses=pd.DataFrame({"v_nom":[500],"substation_name":["Unknown"]},index=["nearby_bus"])
    n=SimpleNamespace(buses=buses,lines=pd.DataFrame(columns=["bus0","bus1"]))
    with patch("pypsa.Network",return_value=n):
        result=inspect(tmp_path/"network.nc",tmp_path/"report.json")
    assert result["candidate_count"]==0
    assert result["coordinate_nearest_bus_inferred"] is False
