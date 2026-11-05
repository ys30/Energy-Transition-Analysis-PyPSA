import pytest
from energy_transition.efs_montana_p18_western_reeds_exclusion_gate import check

CODE="""def main():
    reeds_exclusion = {
       "western":["p35","p19","p32"],
       "eastern":["p18"],
    }
def trim_shape_to_interconnect(shape_state_intersection, exclusion_dict, interconnect):
    return shape_state_intersection.name.str.contains("|".join(exclusion_dict[interconnect]))
"""
SOURCE={"reviewed_source_load_cases":[{
    "original_firstbus_id":"2077004",
    "source_county_bus_count":10,
    "source_county_raw_polygon_single_cover_counts":{"p35":8,"p19":1,"p18":1},
    "source_county_final_reeds_zone_counts":{"p18":10},
}]}

def test_actual_pinned_exclusion_rule_consistent_with_final_montana_label():
    r=check(CODE,SOURCE)
    assert r["raw_county_bins_remaining_after_explicit_western_exclusion"]=={"p18":1}
    assert r["pinned_county_majority_rule_is_consistent_with_observed_final_zone"]
    assert not r["actual_precountry_majority_zone_inputs_reconstructed"]
    assert not r["physical_2030_2050_OPF_validated"]

def test_if_p18_western_excluded_it_fails():
    with pytest.raises(ValueError,match="exclusion not verified"):
        check(CODE.replace('["p35","p19","p32"]','["p35","p19","p18"]'),SOURCE)

def test_changed_source_county_raw_membership_fails():
    bad={"reviewed_source_load_cases":[dict(SOURCE["reviewed_source_load_cases"][0],source_county_raw_polygon_single_cover_counts={"p35":7,"p19":1,"p18":2})]}
    with pytest.raises(ValueError,match="mass drift"):
        check(CODE,bad)
