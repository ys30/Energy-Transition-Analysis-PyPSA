"""Three-zone PyPSA + HiGHS congestion integration regression.

Synthetic capacities and demand; proves numerical integration, not empirical
Western transmission or historical dispatch calibration.
"""
import pandas as pd
import pytest

pypsa = pytest.importorskip("pypsa")
from energy_transition.pypsa_network_ingest import attach_bus_loads


def test_three_zone_serial_bottlenecks_and_nodal_balance():
    n = pypsa.Network()
    utc = pd.date_range("2024-01-01", periods=2, freq="h", tz="UTC")
    n.set_snapshots(utc.tz_localize(None))
    for bus in ("A", "B", "C"):
        n.add("Bus", bus)
    n.add("Link", "A_B", bus0="A", bus1="B",
          p_nom=40.0, efficiency=1.0)
    n.add("Link", "B_C", bus0="B", bus1="C",
          p_nom=25.0, efficiency=1.0)
    n.add("Generator", "cheap_A", bus="A", p_nom=100.0, marginal_cost=1.0)
    n.add("Generator", "backup_B", bus="B", p_nom=100.0, marginal_cost=50.0)
    n.add("Generator", "backup_C", bus="C", p_nom=100.0, marginal_cost=100.0)
    attach_bus_loads(n, pd.DataFrame({"B": [20., 20.], "C": [50., 50.]}, index=utc))
    status, condition = n.optimize(solver_name="highs")
    assert (status, condition) == ("ok", "optimal")
    for t in n.snapshots:
        ab = float(n.links_t.p0.loc[t, "A_B"])
        bc = float(n.links_t.p0.loc[t, "B_C"])
        assert ab == pytest.approx(40., abs=1e-5)
        assert bc == pytest.approx(25., abs=1e-5)
        assert float(n.generators_t.p.loc[t, "cheap_A"]) == pytest.approx(40., abs=1e-5)
        assert float(n.generators_t.p.loc[t, "backup_B"]) == pytest.approx(5., abs=1e-5)
        assert float(n.generators_t.p.loc[t, "backup_C"]) == pytest.approx(25., abs=1e-5)
        for bus in n.buses.index:
            gen = float(n.generators_t.p.loc[t, n.generators.bus == bus].sum())
            load = float(n.loads_t.p.loc[t, n.loads.bus == bus].sum())
            export = float(n.links_t.p0.loc[t, n.links.bus0 == bus].sum())
            import_negative = float(n.links_t.p1.loc[t, n.links.bus1 == bus].sum())
            assert gen - load - export - import_negative == pytest.approx(0., abs=1e-5)
