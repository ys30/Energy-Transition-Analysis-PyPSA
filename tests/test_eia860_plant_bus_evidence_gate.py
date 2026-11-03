"""Reject geographic candidates without separately reviewed electrical bus evidence."""
import json

import pandas as pd
import pypsa
import pytest

from energy_transition.eia860_plant_bus_evidence_gate import audit


def fixtures(tmp_path, *, evidence_rows=None):
    net = pypsa.Network()
    net.add("Bus", "b1")
    net.add("Bus", "b2")
    net_path = tmp_path / "network.nc"
    net.export_to_netcdf(net_path)
    candidates = tmp_path / "candidates.csv"
    pd.DataFrame([
        {"plant_id": "100", "nearest_candidate_bus": "b1",
         "assignment_status": "geographic_candidate_only",
         "electrical_connection_verified": False},
        {"plant_id": "200", "nearest_candidate_bus": "b1",
         "assignment_status": "geographic_candidate_only",
         "electrical_connection_verified": False},
    ]).to_csv(candidates, index=False)
    evidence = tmp_path / "evidence.csv"
    if evidence_rows is None:
        evidence_rows = [{
            "plant_id": "100", "verified_bus_id": "b2",
            "evidence_source": "independent interconnection record",
            "reviewer": "reviewer-1", "evidence_status": "reviewed_approved",
            "electrical_connection_verified": True,
        }]
    pd.DataFrame(evidence_rows).to_csv(evidence, index=False)
    return candidates, evidence, net_path


def test_independent_verified_bus_need_not_equal_geographic_nearest(tmp_path):
    candidate, evidence, network = fixtures(tmp_path)
    output = tmp_path / "admission.csv"
    summary = audit(candidate, evidence, network, output)
    rows = pd.read_csv(output).set_index("plant_id")
    assert summary["independently_reviewed_electrical_bus_evidence_records"] == 1
    assert summary["candidate_matches_verified_bus"] == 0
    assert bool(rows.loc[100, "evidence_admitted"])
    assert rows.loc[100, "verified_bus_id"] == "b2"
    assert not bool(rows.loc[200, "evidence_admitted"])
    assert not bool(rows.loc[100, "ready_for_full_western_opf"])
    assert json.loads(output.with_suffix(".json").read_text())["full_western_opf_ready"] is False


@pytest.mark.parametrize("field,value,expected", [
    ("verified_bus_id", "not_in_grid", "blocked_bus_not_in_network"),
    ("evidence_source", "", "blocked_missing_source_or_reviewer"),
    ("reviewer", "", "blocked_missing_source_or_reviewer"),
])
def test_missing_evidence_blocks_admission(tmp_path, field, value, expected):
    row = {"plant_id": "100", "verified_bus_id": "b2",
           "evidence_source": "documented POI", "reviewer": "reviewer-1",
           "evidence_status": "reviewed_approved",
           "electrical_connection_verified": True}
    row[field] = value
    candidate, evidence, network = fixtures(tmp_path, evidence_rows=[row])
    out = tmp_path / "screen.csv"
    summary = audit(candidate, evidence, network, out)
    result = pd.read_csv(out).set_index("plant_id")
    assert result.loc[100, "admission_status"] == expected
    assert summary["independently_reviewed_electrical_bus_evidence_records"] == 0


def test_candidate_cannot_self_certify(tmp_path):
    candidate, evidence, network = fixtures(tmp_path)
    source = pd.read_csv(candidate)
    source.loc[0, "electrical_connection_verified"] = True
    source.to_csv(candidate, index=False)
    with pytest.raises(ValueError, match="Candidates cannot certify"):
        audit(candidate, evidence, network, tmp_path / "result.csv")


def test_approval_flag_mismatch_fails_closed(tmp_path):
    row = {"plant_id": "100", "verified_bus_id": "b2",
           "evidence_source": "documented POI", "reviewer": "reviewer-1",
           "evidence_status": "reviewed_approved",
           "electrical_connection_verified": False}
    candidate, evidence, network = fixtures(tmp_path, evidence_rows=[row])
    with pytest.raises(ValueError, match="disagree"):
        audit(candidate, evidence, network, tmp_path / "result.csv")
