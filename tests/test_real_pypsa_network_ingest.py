"""Real PyPSA object smoke test; synthetic network, no empirical claims."""
import pandas as pd
import pytest

pypsa = pytest.importorskip("pypsa")
from energy_transition.pypsa_network_ingest import attach_bus_loads


def test_real_pypsa_loads_t_p_set():
    network = pypsa.Network()
    snapshots = pd.date_range("2024-01-01", periods=3, freq="h", tz="UTC")
    network.set_snapshots(snapshots)
    network.add("Bus", "CA_bus")
    network.add("Bus", "NV_bus")
    demand = pd.DataFrame({"CA_bus": [100., 110., 120.],
                           "NV_bus": [40., 42., 44.]}, index=snapshots)
    ids = attach_bus_loads(network, demand)
    assert ids == ["demand_CA_bus", "demand_NV_bus"]
    actual = network.loads_t.p_set.loc[snapshots, ids]
    pd.testing.assert_frame_equal(actual, demand.set_axis(ids, axis=1),
                                  check_names=False, check_freq=False)
    assert network.loads.loc["demand_CA_bus", "bus"] == "CA_bus"
    assert network.loads.loc["demand_NV_bus", "bus"] == "NV_bus"
