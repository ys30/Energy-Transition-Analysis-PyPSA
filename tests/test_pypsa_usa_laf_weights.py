"""Pure-data checks for evidence-derived state-to-zone LAF weights."""
import pandas as pd
import pytest
from energy_transition.pypsa_usa_laf_weights import derive_state_zone_weights

MAPPING = {"state_to_all_membership_zones": {"CA": ["p1", "p2"], "NV": ["p3"]}}

def buses():
    return pd.DataFrame({
        "reeds_state": ["CA", "CA", "CA", "NV"],
        "reeds_zone": ["p1", "p1", "p2", "p3"],
        "LAF_state": [0.2, 0.3, 0.5, 1.0],
    })

def test_aggregate_real_bus_laf_without_fabricating_zone_shares():
    weights = derive_state_zone_weights(buses(), MAPPING)
    assert dict(zip(weights.zone, weights.weight)) == pytest.approx(
        {"p1": 0.5, "p2": 0.5, "p3": 1.0})
    assert len(weights) == 3

def test_refuse_missing_source_zone():
    with pytest.raises(ValueError, match="Missing source state-zone"):
        derive_state_zone_weights(buses().iloc[[0, 1, 3]], MAPPING)

def test_refuse_nonconserving_source_laf():
    original = buses()
    original.loc[2, "LAF_state"] = 0.4
    with pytest.raises(ValueError, match="fails state conservation"):
        derive_state_zone_weights(original, MAPPING)

def test_refuse_missing_bus_laf():
    original = buses()
    original.loc[1, "LAF_state"] = float("nan")
    with pytest.raises(ValueError, match="Missing state"):
        derive_state_zone_weights(original, MAPPING)


def test_national_network_excludes_nonwestern_bus_before_laf_checks():
    national = pd.concat([
        buses(),
        pd.DataFrame({
            "reeds_state": ["NY"],
            "reeds_zone": ["p_east"],
            "LAF_state": [float("nan")],
        }),
    ], ignore_index=True)
    derived = derive_state_zone_weights(national, MAPPING)
    assert set(derived.zone) == {"p1", "p2", "p3"}
    assert derived.groupby("state")["weight"].sum().to_dict() == pytest.approx(
        {"CA": 1.0, "NV": 1.0})


def test_cannot_replace_missing_western_laf_with_nonwestern_data():
    national = pd.concat([
        buses().iloc[[0, 1, 3]],
        pd.DataFrame({
            "reeds_state": ["NY"],
            "reeds_zone": ["p_east"],
            "LAF_state": [0.5],
        }),
    ], ignore_index=True)
    with pytest.raises(ValueError, match="Missing source state-zone"):
        derive_state_zone_weights(national, MAPPING)
