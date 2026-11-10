import pytest
from energy_transition.paper_s_e3_two_group_final_window_check import GROUP_STATES
from energy_transition.paper_s_five_window_robustness import WINDOWS,validate_windows
def test_e3_frozen_unique_group_states():
    assert GROUP_STATES=={2:"CO",3:"ID"}
    assert validate_windows()
    assert len(WINDOWS)==5
    assert set(WINDOWS.values())=={(1,168),(2001,2168),(4001,4168),(6001,6168),(8001,8168)}
def test_no_other_groups_admitted():
    assert 1 not in GROUP_STATES and 7 not in GROUP_STATES
