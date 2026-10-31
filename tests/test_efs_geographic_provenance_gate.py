import hashlib

from energy_transition.efs_geographic_provenance_gate import assess_weight_provenance

MAPPING = {
    "state_to_all_membership_zones": {"CA": ["p8", "p9"]},
    "state_to_network_zones": {"CA": ["p8", "p9"]},
}
WEIGHTS = b"state,zone,weight\nCA,p8,0.4\nCA,p9,0.6\n"

def manifest():
    return {
        "weights_sha256": hashlib.sha256(WEIGHTS).hexdigest(),
        "source_url": "https://example.org/source",
        "source_revision": "revision-123",
        "geographic_method": "population_geographic_overlay",
        "geography_vintage": "2020",
        "population_vintage": "2020",
        "processing_script_sha256": "a" * 64,
        "coverage_note": "Example-only fixture; not real evidence",
    }

def test_valid_manifest_and_weights_are_accepted_structurally():
    report = assess_weight_provenance(MAPPING, WEIGHTS, manifest())
    assert report["provenance_metadata_valid"]
    assert report["ready_for_full_network_dispatch"]

def test_checksum_mismatch_fails_closed():
    m = manifest()
    m["weights_sha256"] = "b" * 64
    report = assess_weight_provenance(MAPPING, WEIGHTS, m)
    assert not report["ready_for_full_network_dispatch"]
    assert any("does not match" in e for e in report["provenance_errors"])

def test_missing_geography_vintage_fails_closed():
    m = manifest()
    del m["geography_vintage"]
    report = assess_weight_provenance(MAPPING, WEIGHTS, m)
    assert not report["ready_for_full_network_dispatch"]

def test_unverifiable_allocation_method_fails_closed():
    m = manifest()
    m["geographic_method"] = "equal_zone_split"
    report = assess_weight_provenance(MAPPING, WEIGHTS, m)
    assert not report["ready_for_full_network_dispatch"]

def test_missing_network_bus_blocks_even_with_manifest():
    mapping = {**MAPPING, "state_to_network_zones": {"CA": ["p8"]}}
    report = assess_weight_provenance(mapping, WEIGHTS, manifest())
    assert not report["ready_for_full_network_dispatch"]
    assert report["missing_network_buses"] == ["p9"]
