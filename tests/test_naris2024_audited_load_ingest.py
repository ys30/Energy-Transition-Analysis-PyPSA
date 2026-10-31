"""End-to-end audited load ingestion fixture with explicit synthetic mode."""
import pandas as pd
import pytest

pypsa = pytest.importorskip("pypsa")
from energy_transition.naris2024_audited_load_ingest import prepare_network_loads


def fixture_files(tmp_path):
    network = pypsa.Network()
    network.add("Bus", "p8")
    network.add("Bus", "p9")
    network.add("Link", "p8_p9", bus0="p8", bus1="p9", p_nom=150.0, efficiency=0.98)
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
    assert report["netcdf_topology_roundtrip_verified"] is True
    assert list(result.links.index) == ["p8_p9"]
    assert result.links.loc["p8_p9", "p_nom"] == pytest.approx(150.0)
    assert result.links.loc["p8_p9", "efficiency"] == pytest.approx(0.98)
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


def test_partial_network_bus_coverage_rejected(tmp_path):
    network, loads, weights, buses = fixture_files(tmp_path)
    n = pypsa.Network(network)
    n.add("Bus", "p10")
    n.export_to_netcdf(network)
    output = tmp_path / "partial.nc"
    with pytest.raises(ValueError, match="missing demand coverage"):
        prepare_network_loads(
            network, loads, weights, buses, output,
            tmp_path / "audit.csv", tmp_path / "zonal.csv",
            allow_synthetic=True,
        )
    assert not output.exists()


def test_official_membership_rejects_missing_western_zone(tmp_path):
    network, loads, weights, buses = fixture_files(tmp_path)
    membership = tmp_path / "membership.csv"
    membership.write_text(
        "ba,st,interconnect,country\\n"
        "p8,CA,Western,USA\\n"
        "p9,CA,Western,USA\\n"
        "p10,CA,Western,USA\\n"
    )
    with pytest.raises(ValueError, match="Western membership mismatch"):
        prepare_network_loads(
            network, loads, weights, buses, tmp_path / "out.nc",
            tmp_path / "audit.csv", tmp_path / "zonal.csv",
            membership_csv=membership, allow_synthetic=True,
        )
    assert not (tmp_path / "out.nc").exists()


def test_source_mode_requires_membership_before_processing(tmp_path):
    network, loads, weights, buses = fixture_files(tmp_path)
    with pytest.raises(ValueError, match="official Western membership"):
        prepare_network_loads(
            network, loads, weights, buses, tmp_path / "out.nc",
            tmp_path / "audit.csv", tmp_path / "zonal.csv",
            mapping_json=tmp_path / "mapping.json",
            provenance_json=tmp_path / "manifest.json",
        )
