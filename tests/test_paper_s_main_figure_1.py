import pytest
from energy_transition.paper_s_main_figure_1 import render,verify_design

def test_original_provenance_counts_locked():
    r=verify_design()
    assert r["baseline_full_year_LP_cases"]==540
    assert r["orthogonal_independent_P_E_LP_cases"]==189
    assert r["distinct_peak_normalized_nonzero_shapes_per_year"]==7
    assert not r["cross_year_normalized_shape_identity_verified"]
    assert not r["source_hour_certified_utc"]

def test_no_claim_of_real_renewables_or_western_opf():
    r=verify_design()
    assert r["resource_profiles_observed"] is False
    assert r["western_network_OPF"] is False
    assert r["storage_capex_included"] is False
    assert r["original_initial_and_terminal_SOC_zero"] is True

def test_main_figure_actual_render(tmp_path):
    manifest=render(tmp_path)
    assert (tmp_path/"Paper_S_proposed_main_Figure_1_source_workflow.png").stat().st_size>3000
    assert (tmp_path/"Paper_S_proposed_main_Figure_1_source_workflow.svg").stat().st_size>3000
    assert manifest["source_years"]==[2030,2040,2050]
