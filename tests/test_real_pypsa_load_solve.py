"""Real PyPSA + HiGHS solve over a synthetic two-zone network.

This is an engineering integration test, not an empirical Western grid model.
"""
import pandas as pd
import pytest

pypsa = pytest.importorskip("pypsa")
from energy_transition.pypsa_network_ingest import attach_bus_loads


def test_attached_bus_demand_solves_with_constrained_transfer():
    n = pypsa.Network()
    snapshots = pd.date_range("2024-01-01", periods=2, freq="h", tz="UTC")
    n.set_snapshots(snapshots.tz_localize(None))
    n.add("Bus", "supply")
    n.add("Bus", "demand")
    n.add("Link", "transfer", bus0="supply", bus1="demand",
          p_nom=30.0, efficiency=1.0, marginal_cost=0.0)
    n.add("Generator", "cheap", bus="supply",
          p_nom=100.0, marginal_cost=1.0)
    n.add("Generator", "local_backup", bus="demand",
          p_nom=100.0, marginal_cost=100.0)
    attached = pd.DataFrame({"demand": [50.0, 50.0]}, index=snapshots)
    attach_bus_loads(n, attached)
    status, condition = n.optimize(solver_name="highs")
    assert (status, condition) == ("ok", "optimal")
    assert n.links_t.p0.loc[snapshots.tz_localize(None), "transfer"].to_numpy() == pytest.approx([30.0, 30.0])
    assert n.generators_t.p.loc[snapshots.tz_localize(None), "local_backup"].to_numpy() == pytest.approx([20.0, 20.0])
    supply = n.generators_t.p.loc[snapshots.tz_localize(None)].sum(axis=1)
    consumed = n.loads_t.p.loc[snapshots.tz_localize(None)].sum(axis=1)
    assert supply.to_numpy() == pytest.approx(consumed.to_numpy())
