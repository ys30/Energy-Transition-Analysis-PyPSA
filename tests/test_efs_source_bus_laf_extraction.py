"""Unit checks for conservative source-network LAF aggregation."""
import pandas as pd
import pytest
from energy_transition.efs_source_bus_laf_extraction import candidate_weights, verify_western_membership


def buses():
    return pd.DataFrame({
        "reeds_state": ["CA", "CA", "CA", "NM"],
        "reeds_zone": ["p8", "p8", "p9", "p31"],
        "LAF_state": [0.2, 0.3, 0.5, 1.0],
    }, index=["busA", "busB", "busC", "busD"])


def test_aggregate_source_bus_weights_without_renormalizing():
    weights, report = candidate_weights(buses())
    got = {(r.state, r.zone): r.weight for r in weights.itertuples()}
    assert got == pytest.approx({("CA", "p8"): 0.5, ("CA", "p9"): 0.5,
                                 ("NM", "p31"): 1.0})
    assert report["state_laf_conservation_verified"]
    assert report["no_renormalization_performed"]
    assert report["independent_geographic_source_provenance_verified"] is False
    assert report["admitted_for_empirical_dispatch"] is False


def test_partial_state_footprint_is_not_redistributed():
    df = buses().drop(index="busC")
    with pytest.raises(ValueError, match="Do not re-normalize"):
        candidate_weights(df)


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -0.1, 1.2])
def test_invalid_laf_rejected(bad):
    df = buses()
    df.loc["busA", "LAF_state"] = bad
    with pytest.raises(ValueError):
        candidate_weights(df)


def test_missing_source_attributes_block_extraction():
    with pytest.raises(ValueError, match="Source bus attributes missing"):
        candidate_weights(buses().drop(columns="LAF_state"))


def test_duplicate_buses_block_extraction():
    df = buses()
    df.index = ["busA", "busA", "busC", "busD"]
    with pytest.raises(ValueError, match="duplicated source bus"):
        candidate_weights(df)


def test_zone_state_conflict_blocked():
    df = buses()
    df.loc["busD", "reeds_zone"] = "p8"
    with pytest.raises(ValueError, match="multiple states"):
        candidate_weights(df)


def test_sum_above_one_blocked():
    df = buses()
    df.loc["busA", "LAF_state"] = 0.8
    with pytest.raises(ValueError, match="Full-state LAF coverage"):
        candidate_weights(df)


def test_exact_western_membership_crosscheck_passes_without_promoting():
    weights, _ = candidate_weights(buses())
    mapping = {"state_to_all_membership_zones": {
        "CA": ["p8", "p9"], "NM": ["p31"]
    }}
    result = verify_western_membership(weights, mapping)
    assert result["western_membership_exactly_matched"]
    assert result["admitted_for_empirical_dispatch"] is False
    assert result["independent_geographic_source_provenance_verified"] is False


@pytest.mark.parametrize("membership", [
    {"CA": ["p8"], "NM": ["p31"]},
    {"CA": ["p8", "p9", "p10"], "NM": ["p31"]},
    {"CA": ["p8", "p9", "p31"], "NM": []},
])
def test_western_membership_mismatch_blocks_candidate(membership):
    weights, _ = candidate_weights(buses())
    with pytest.raises(ValueError, match="Western membership disagreement"):
        verify_western_membership(
            weights, {"state_to_all_membership_zones": membership}
        )


def test_duplicate_weight_rows_are_not_accepted_as_coverage():
    weights, _ = candidate_weights(buses())
    weights = pd.concat([weights, weights.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="Duplicate source state-zone"):
        verify_western_membership(
            weights, {"state_to_all_membership_zones": {
                "CA": ["p8", "p9"], "NM": ["p31"]
            }}
        )
