"""Real PyPSA built-network input audit, using small synthetic fixtures."""
import pandas as pd
import pypsa
import pytest

from energy_transition.pypsa_usa_built_network_intake import inspect_built_network


def make_inputs(tmp_path, *, complete=True):
    net = pypsa.Network()
    for name, state, zone, laf in (
        ("ca", "CA", "p1", 1.0),
        ("nv", "NV", "p2", 1.0),
    ):
        net.add("Bus", name, reeds_state=state, reeds_zone=zone, LAF_state=laf)
    path = tmp_path / "upstream.nc"
    net.export_to_netcdf(path)
    membership = tmp_path / "membership.csv"
    members = "ba,st,interconnect,country\np1,CA,Western,USA\np2,NV,Western,USA\n"
    if not complete:
        members += "p3,UT,Western,USA\n"
    membership.write_text(members)
    return path, membership


def test_upstream_network_intake_records_sha_and_coverage(tmp_path):
    path, membership = make_inputs(tmp_path)
    result = inspect_built_network(path, membership)
    assert result["western_zones_expected"] == 2
    assert result["western_bus_count"] == 2
    assert len(result["network_sha256"]) == 64
    assert result["geographic_laf_derivation_independently_verified"] is False


def test_upstream_network_intake_rejects_missing_western_zone(tmp_path):
    path, membership = make_inputs(tmp_path, complete=False)
    with pytest.raises(ValueError, match="zone coverage"):
        inspect_built_network(path, membership)
