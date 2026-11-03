"""Conservative full-Western OPF readiness checks on synthetic PyPSA inputs."""
import json

import pypsa
import pandas as pd

from energy_transition.western_full_opf_readiness_audit import inspect


def test_one_dynamic_load_does_not_certify_all_loads(tmp_path):
    n=pypsa.Network()
    n.set_snapshots(pd.date_range("2030-01-01",periods=3,freq="h"))
    n.add("Bus","b")
    n.add("Generator","g",bus="b",p_nom=100,marginal_cost=10,
          p_max_pu=[1,1,1])
    n.add("Load","profile",bus="b",p_set=[10,11,12])
    n.add("Load","static",bus="b",p_set=5)
    net=tmp_path/"network.nc"
    n.export_to_netcdf(net)
    out=tmp_path/"readiness.json"
    inspect(net,out)
    result=json.loads(out.read_text())
    assert "static" in result["load_components_without_dynamic_profile"]
    assert result["static_only_nonzero_load_ids"] == ["static"]
    assert result["static_only_zero_load_ids"] == []
    assert result["effective_load_invalid_cells"] == 0
    # 10+11+12 MW dynamic + 5 MW constant over three 1h snapshots.
    assert result["unweighted_snapshot_load_sum_mw"] == 48.0
    assert result["unweighted_snapshot_load_sum_is_certified_annual_mwh"] is False
    assert result["readiness_gates"]["load_timeseries_complete"] is False
    assert result["full_opf_ready"] is False
    assert "generator_operational_inputs_verified" in result["missing_required_inputs"]


def test_2040_ordinal_leap_year_cannot_be_calendar_certified(tmp_path):
    n=pypsa.Network()
    n.set_snapshots(pd.date_range("2040-01-01",periods=8760,freq="h"))
    n.add("Bus","b")
    n.add("Generator","g",bus="b",p_nom=20,p_max_pu=[1]*8760)
    n.add("Load","d",bus="b",p_set=[5]*8760)
    net=tmp_path/"network.nc"
    n.export_to_netcdf(net)
    out=tmp_path/"readiness.json"
    inspect(net,out)
    result=json.loads(out.read_text())
    assert result["readiness_gates"]["calendar_semantics_verified"] is False
    assert result["full_opf_ready"] is False
