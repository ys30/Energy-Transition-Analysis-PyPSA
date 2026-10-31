import pytest
from energy_transition.efs_zonal_weight_admission import validate_weights

M={"state_to_all_membership_zones":{"CA":["p8","p9"],"NM":["p31"]},
   "state_to_network_zones":{"CA":["p8","p9"],"NM":["p31"]}}

def test_complete_weights_pass():
    r=validate_weights(M,b"state,zone,weight\nCA,p8,0.4\nCA,p9,0.6\nNM,p31,1\n")
    assert r["ready_for_full_network_dispatch"]
    assert r["validated_zone_weights"]==3

def test_missing_zone_blocks():
    with pytest.raises(ValueError,match="Missing"):
        validate_weights(M,b"state,zone,weight\nCA,p8,1\nNM,p31,1\n")

def test_wrong_sum_blocks():
    with pytest.raises(ValueError,match="conservation"):
        validate_weights(M,b"state,zone,weight\nCA,p8,0.4\nCA,p9,0.4\nNM,p31,1\n")

def test_missing_network_bus_blocks():
    mapping={**M,"state_to_network_zones":{"CA":["p8"],"NM":["p31"]}}
    r=validate_weights(mapping,b"state,zone,weight\nCA,p8,0.4\nCA,p9,0.6\nNM,p31,1\n")
    assert not r["ready_for_full_network_dispatch"]
    assert r["missing_network_buses"]==["p9"]
