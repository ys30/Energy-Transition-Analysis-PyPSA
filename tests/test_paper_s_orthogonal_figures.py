import pandas as pd
import pytest
from energy_transition.paper_s_orthogonal_figures import verify

def test_incomplete_original_source_grid_rejected():
    with pytest.raises(ValueError,match="Incomplete 189-LP"):
        verify(pd.DataFrame({"source_shape_group":[],"synthetic_supply_shape":[],
              "battery_power_peak_ratio":[],"battery_energy_peak_hours":[],
              "storage_discharge_to_load_mwh":[]}),
              pd.DataFrame({"source_shape_group":[],"synthetic_supply_shape":[],
              "axis":[],"held_constant":[],"from_level":[],"to_level":[],
              "added_discharge_mwh":[]}))
