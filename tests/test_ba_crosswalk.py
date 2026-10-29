import pandas as pd
import pytest
from energy_transition.ba_crosswalk import join_verified_crosswalk

def test_verified_ba_join_and_unmatched():
    g = pd.DataFrame({"plant_id": ["34.0", "45.0"], "generator_id": ["A","B"],
                      "capacity_mw": [10., 20.], "status": ["OP", "SB"]})
    x = pd.DataFrame({"plant_id": ["34"], "ba_code": ["CISO"]})
    matched = join_verified_crosswalk(g, x)
    assert matched.ba_code.iloc[0] == "CISO"
    assert matched.crosswalk_status.astype(str).tolist() == ["matched", "unmatched"]

def test_ambiguous_ba_crosswalk_rejected():
    g = pd.DataFrame({"plant_id": ["34"], "generator_id": ["A"],
                      "capacity_mw": [10.], "status": ["OP"]})
    x = pd.DataFrame({"plant_id": ["34", "34"], "ba_code": ["CISO", "BPAT"]})
    with pytest.raises(ValueError, match="duplicate"):
        join_verified_crosswalk(g, x)
