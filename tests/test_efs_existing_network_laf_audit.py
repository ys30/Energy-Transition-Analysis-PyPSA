"""Audit absent, incomplete and numerically valid network LAF source fields."""
import pandas as pd
from energy_transition.efs_existing_network_laf_audit import audit_bus_laf


def test_network_without_laf_is_blocked_without_fabrication():
    report = audit_bus_laf(pd.DataFrame({"x": [1, 2]}))
    assert not report["candidate_laf_extraction_passed"]
    assert set(report["missing_laf_columns"]) == {
        "reeds_state", "reeds_zone", "LAF_state"
    }
    assert report["empirical_load_admitted"] is False


def test_partial_laf_state_coverage_is_a_blocker():
    data = pd.DataFrame({
        "reeds_state": ["CA", "CA"],
        "reeds_zone": ["p8", "p9"],
        "LAF_state": [0.2, 0.3],
    })
    report = audit_bus_laf(data)
    assert report["candidate_laf_extraction_passed"] is False
    assert "Do not re-normalize" in report["blocker"]


def test_candidate_passes_without_empirical_promotion():
    data = pd.DataFrame({
        "reeds_state": ["CA", "CA"],
        "reeds_zone": ["p8", "p9"],
        "LAF_state": [0.4, 0.6],
    })
    report = audit_bus_laf(data)
    assert report["candidate_laf_extraction_passed"] is True
    assert report["candidate_zone_pairs"] == 2
    assert report["candidate_weights_verified_source"] is False
    assert report["empirical_load_admitted"] is False
