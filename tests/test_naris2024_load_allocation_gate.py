import pytest
from energy_transition.naris2024_load_allocation_gate import validate_weights


def mapping():
    return {"state_to_network_zones": {"CA": ["p8", "p9"], "NM": ["p31"]},
            "unmatched_membership_zones": []}


def rows():
    return [
        {"state": "CA", "zone": "p8", "weight": "0.4", "source": "documented_metering"},
        {"state": "CA", "zone": "p9", "weight": "0.6", "source": "documented_metering"},
        {"state": "NM", "zone": "p31", "weight": "1.0", "source": "documented_metering"},
    ]


def test_valid_complete_weights():
    assert validate_weights(mapping(), rows())["allocation_weights_validated"]


@pytest.mark.parametrize("change", [
    lambda r: r.pop(),
    lambda r: r[0].update(weight="0.8"),
    lambda r: r[0].update(source="assumed"),
    lambda r: r[0].update(zone="p99"),
    lambda r: r[0].update(weight="nan"),
])
def test_invalid_weights_rejected(change):
    values = rows()
    change(values)
    with pytest.raises(ValueError):
        validate_weights(mapping(), values)


def test_unmatched_zone_blocks_allocation():
    m = mapping()
    m["unmatched_membership_zones"] = ["p19"]
    with pytest.raises(ValueError):
        validate_weights(m, rows())
