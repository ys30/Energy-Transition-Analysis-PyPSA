"""End-to-end audited load ingestion fixture with explicit synthetic mode."""
import pandas as pd
import pytest

pypsa = pytest.importorskip("pypsa")
from energy_transition.naris2024_audited_load_ingest import prepare_network_loads


def fixture_files(tmp_path):
    network = pypsa.Network()
    network.add("Bus", "p8")
    network.add("Bus", "p9")
    network_path = tmp_path / "topology.nc"
    network.export_to_netcdf(network_path)
    hours = pd.date_range("2024-01-01", "2025-01-01", freq="h",
                          inclusive="left", tz="UTC")
    loads = tmp_path / "states.csv"
    pd.DataFrame({
        "timestamp_utc": [t.isoformat() for t in hours],
        "state": ["CA"] * len(hours),
        "load_mw": [100.0] * len(hours),
    }).to_csv(loads, index=False)
    weights = tmp_path / "weights.csv"
    pd.DataFrame({"state": ["CA", "CA"], "zone": ["p8", "p9"],
                  "weight": [0.4, 0.6]}).to_csv(weights, index=False)
    zone_bus = tmp_path / "zone_bus.csv"
    pd.DataFrame({"zone": ["p8", "p9"], "bus": ["p8", "p9"]}).to_csv(zone_bus, index=False)
    return network_path, loads, weights, zone_bus


def test_reject_missing_provenance_before_writing(tmp_path):
    network, loads, weights, buses = fixture_files(tmp_path)
    out = tmp_path / "model.nc"
    with pytest.raises(ValueError, match="Source-backed mode"):
        prepare_network_loads(network, loads, weights, buses,
                              out, tmp_path / "audit.csv",
                              tmp_path / "zonal.csv")
    assert not out.exists()


def test_synthetic_full_year_network_roundtrip(tmp_path):
    network, loads, weights, buses = fixture_files(tmp_path)
    output = tmp_path / "model.nc"
    report = prepare_network_loads(
        network, loads, weights, buses, output,
        tmp_path / "audit.csv", tmp_path / "zonal.csv",
        allow_synthetic=True,
    )
    result = pypsa.Network(output)
    assert len(result.snapshots) == 8784
    assert report["total_load_mwh"] == pytest.approx(878400.0)
    assert report["netcdf_load_roundtrip_verified"] is True
    assert report["optimization_solved"] is False
    assert report["source_provenance_required"] is False
    assert set(result.loads.bus) == {"p8", "p9"}
    assert float(result.loads_t.p_set.iloc[0].sum()) == pytest.approx(100.0)


def test_unrecognized_network_bus_rejected(tmp_path):
    network, loads, weights, buses = fixture_files(tmp_path)
    pd.DataFrame({"zone": ["p8", "p9"], "bus": ["p8", "missing"]}).to_csv(buses, index=False)
    with pytest.raises(ValueError, match="absent from actual network"):
        prepare_network_loads(
            network, loads, weights, buses, tmp_path / "bad.nc",
            tmp_path / "audit.csv", tmp_path / "zonal.csv",
            allow_synthetic=True,
        )
    assert not (tmp_path / "bad.nc").exists()
