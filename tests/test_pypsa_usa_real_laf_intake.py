"""Test one-command real-network LAF intake using a tiny constructed network."""
import json
import pypsa
import pytest
from energy_transition.pypsa_usa_real_laf_intake import import_built_laf


def inputs(tmp_path, *, incomplete=False):
    n = pypsa.Network()
    n.add("Bus", "ca", reeds_state="CA", reeds_zone="p1", LAF_state=1.0)
    n.add("Bus", "nv", reeds_state="NV", reeds_zone="p2", LAF_state=1.0)
    nc = tmp_path / "source.nc"
    n.export_to_netcdf(nc)
    member = tmp_path / "members.csv"
    member.write_text("ba,st,interconnect,country\np1,CA,Western,USA\np2,NV,Western,USA\n")
    mapping = tmp_path / "mapping.json"
    mapping.write_text(json.dumps({
        "state_to_all_membership_zones": {
            "CA": ["p1"], "NV": ["p2"] if not incomplete else ["p3"]
        },
        "state_to_network_zones": {"CA": ["p1"], "NV": ["p2"]},
    }))
    return nc, member, mapping


def test_candidate_extraction_has_source_evidence_and_is_not_empirical_approval(tmp_path):
    nc, member, mapping = inputs(tmp_path)
    dest = tmp_path / "results"
    report = import_built_laf(nc, member, mapping, dest)
    assert report["candidate_weight_rows"] == 2
    assert report["intake"]["western_zones_expected"] == 2
    assert report["downstream_empirical_optimization_approved"] is False
    assert "CA,p1,1.0" in (dest / "candidate_western_laf_weights.csv").read_text()
    assert (dest / "candidate_western_laf_report.json").exists()


def test_reject_nonmatching_mapping_without_writing_candidate(tmp_path):
    nc, member, mapping = inputs(tmp_path, incomplete=True)
    dest = tmp_path / "results"
    with pytest.raises(ValueError):
        import_built_laf(nc, member, mapping, dest)
    assert not (dest / "candidate_western_laf_weights.csv").exists()
