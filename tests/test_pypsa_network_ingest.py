"""Network ingest unit tests using a minimal PyPSA-like interface."""
import pandas as pd
import pytest

from energy_transition.pypsa_network_ingest import attach_bus_loads


class FakeNetwork:
    def __init__(self):
        self.snapshots = pd.date_range("2024-01-01", periods=2, freq="h", tz="UTC")
        self.buses = pd.DataFrame(index=["bus_a", "bus_b"])
        self.loads = pd.DataFrame(index=pd.Index([], dtype=str))
        self.calls = []

    def add(self, component, name, **kwargs):
        self.calls.append((component, name, kwargs))
        self.loads.loc[name, "bus"] = kwargs["bus"]


def matrix(network):
    return pd.DataFrame({"bus_a": [10.0, 11.0], "bus_b": [20.0, 21.0]},
                        index=network.snapshots)


def test_attach_loads_to_existing_network():
    network = FakeNetwork()
    names = attach_bus_loads(network, matrix(network))
    assert names == ["demand_bus_a", "demand_bus_b"]
    assert len(network.calls) == 2
    assert network.calls[0][2]["p_set"].sum() == 21.0


def test_unknown_bus_rejected_before_mutation():
    network = FakeNetwork()
    demand = matrix(network).rename(columns={"bus_a": "fictional"})
    with pytest.raises(ValueError, match="absent from network"):
        attach_bus_loads(network, demand)
    assert not network.calls


def test_snapshot_mismatch_rejected_before_mutation():
    network = FakeNetwork()
    demand = matrix(network).iloc[:1]
    with pytest.raises(ValueError, match="exactly match"):
        attach_bus_loads(network, demand)
    assert not network.calls


def test_existing_load_id_rejected_before_mutation():
    network = FakeNetwork()
    network.loads.loc["demand_bus_a", "bus"] = "bus_a"
    with pytest.raises(ValueError, match="collide"):
        attach_bus_loads(network, matrix(network))
    assert not network.calls
