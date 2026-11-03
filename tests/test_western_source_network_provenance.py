"""Protect against treating synthetic PyPSA-USA source IDs as real facility POIs."""
import json
from pathlib import Path


def test_pinned_western_base_topology_is_labeled_synthetic():
    path=Path(__file__).resolve().parents[1]/"docs"/"western_source_network_provenance.json"
    x=json.loads(path.read_text())
    assert x["upstream_commit"]=="338af9912addbaf038c6098fe27e1e6ef099d8aa"
    assert "USATestSystem.zip" in x["source_archive"]
    assert "synthetic" in x["source_network_family"].lower()
    assert "synthetic" in x["source_sub_id_meaning"]
    assert x["real_world_geographic_references"] is True
    assert x["utility_authenticated_electrical_facility_identities"] is False
    assert x["eia860_electrical_interconnection_approved"] is False
    assert x["real_world_transmission_topology_validated"] is False
    assert x["empirical_western_opf_ready"] is False
