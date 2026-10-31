"""Synthetic tests for strict zone-to-network-bus adapter."""
import pandas as pd
import pytest

from energy_transition.pypsa_load_adapter import build_load_matrix


def inputs(tmp_path):
    zonal = tmp_path / "zonal.csv"
    mapping = tmp_path / "mapping.csv"
    pd.DataFrame([
        ("2024-01-01T00:00:00+00:00", "A", 10.0),
        ("2024-01-01T00:00:00+00:00", "B", 20.0),
        ("2024-01-01T01:00:00+00:00", "A", 11.0),
        ("2024-01-01T01:00:00+00:00", "B", 21.0),
    ], columns=["timestamp_utc", "zone", "load_mw"]).to_csv(zonal, index=False)
    pd.DataFrame([("A", "bus_a"), ("B", "bus_b")],
                 columns=["zone", "bus"]).to_csv(mapping, index=False)
    return zonal, mapping


def test_build_matrix(tmp_path):
    zonal, mapping = inputs(tmp_path)
    matrix = build_load_matrix(zonal, mapping)
    assert list(matrix.columns) == ["bus_a", "bus_b"]
    assert len(matrix) == 2
    assert matrix.to_numpy().sum() == pytest.approx(62.0)


def test_unmapped_zone_rejected(tmp_path):
    zonal, mapping = inputs(tmp_path)
    pd.DataFrame([("A", "bus_a")], columns=["zone", "bus"]).to_csv(mapping, index=False)
    with pytest.raises(ValueError, match="zone coverage"):
        build_load_matrix(zonal, mapping)


def test_duplicate_bus_rejected(tmp_path):
    zonal, mapping = inputs(tmp_path)
    pd.DataFrame([("A", "bus_a"), ("B", "bus_a")],
                 columns=["zone", "bus"]).to_csv(mapping, index=False)
    with pytest.raises(ValueError, match="multiple zones"):
        build_load_matrix(zonal, mapping)


def test_missing_zone_hour_rejected(tmp_path):
    zonal, mapping = inputs(tmp_path)
    data = pd.read_csv(zonal).iloc[:-1]
    data.to_csv(zonal, index=False)
    with pytest.raises(ValueError, match="missing zone-hour"):
        build_load_matrix(zonal, mapping)
