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


def test_nonnumeric_demand_rejected_before_mutation():
    network = FakeNetwork()
    demand = matrix(network).astype(str)
    with pytest.raises(ValueError, match="must be numeric"):
        attach_bus_loads(network, demand)
    assert not network.calls


def test_nondatetime_network_snapshots_rejected_before_mutation():
    network = FakeNetwork()
    demand = matrix(network)
    network.snapshots = pd.Index(["a", "b"])
    with pytest.raises(ValueError, match="DatetimeIndex"):
        attach_bus_loads(network, demand)
    assert not network.calls


def test_existing_bus_load_rejected_even_when_name_different():
    network = FakeNetwork()
    network.loads.loc["legacy_load", "bus"] = "bus_a"
    with pytest.raises(ValueError, match="double-count"):
        attach_bus_loads(network, matrix(network))
    assert not network.calls


def test_explicit_existing_bus_override_is_opt_in():
    network = FakeNetwork()
    network.loads.loc["legacy_load", "bus"] = "bus_a"
    names = attach_bus_loads(network, matrix(network), allow_existing_bus_loads=True)
    assert names == ["demand_bus_a", "demand_bus_b"]


def test_existing_load_on_other_bus_does_not_block():
    network = FakeNetwork()
    network.loads.loc["unrelated", "bus"] = "bus_c"
    assert len(attach_bus_loads(network, matrix(network))) == 2
