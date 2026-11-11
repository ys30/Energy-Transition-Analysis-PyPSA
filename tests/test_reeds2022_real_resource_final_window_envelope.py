import pytest
from energy_transition.reeds2022_real_resource_final_window_envelope import validate_controls
def test_frozen_2030_2012_four_state_original_168h_control():
 assert validate_controls()
def test_no_new_states_or_posthoc_windows():
 with pytest.raises(ValueError):validate_controls(("AZ","CO","ID","NV"))
 with pytest.raises(ValueError):validate_controls(window=(6001,6168))
