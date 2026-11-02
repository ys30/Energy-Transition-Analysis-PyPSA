import pytest
from energy_transition.colstrip_hypothetical_interface import build

def test_rejects_nonphysical_hypothesis_parameter(tmp_path):
    with pytest.raises(ValueError, match="Invalid hypothetical"):
        build(tmp_path/"missing.nc",tmp_path/"out.nc",tmp_path/"out.json",capacity=-10)

def test_rejects_missing_bus_in_synthetic_network(tmp_path,monkeypatch):
    import pandas as pd
    import pypsa
    class Network:
        buses=pd.DataFrame({"v_nom":[345.]},index=["other_bus"])
    monkeypatch.setattr(pypsa,"Network",lambda *_:Network())
    with pytest.raises(ValueError,match="Missing base-network"):
        build(tmp_path/"base.nc",tmp_path/"out.nc",tmp_path/"out.json")
