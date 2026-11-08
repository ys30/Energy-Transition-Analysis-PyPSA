import numpy as np
import pytest
from energy_transition.paper_s_objective_decomposition import decompose
from test_paper_s_lp_objective_certification import cases


def test_exact_toy_cost_identity_on_complete_synthetic_540_cases():
    r=decompose(cases())
    assert len(r)==9
    assert np.isclose(r.reconciliation_error_0to4h_usd.abs().max(),0,atol=1e-8)
    assert np.isclose(r.reconciliation_error_4to8h_usd.abs().max(),0,atol=1e-8)
    # Mock case 0->4: firm drops 90 MWh per zone; additional renewables charged 100 MWh.
    assert np.isclose(r.iloc[0].firm_component_0to4h_usd,162000)
    assert np.isclose(r.iloc[0].renewable_utilization_component_0to4h_usd,-10000)


def test_availability_varying_with_duration_fails_closed():
    a=cases()
    # Keep renewable mass conservation by increasing unused and available together.
    row=a.index[1]
    a.loc[row,"renewable_available_mwh"]+=10.
    a.loc[row,"unused_renewable_mwh"]+=10.
    with pytest.raises(ValueError,match="Renewable availability changes"):
        decompose(a)


def test_wrong_objective_rejected_by_independent_certificate():
    a=cases()
    a.loc[0,"objective_illustrative_variable_usd"]+=50
    with pytest.raises(ValueError,match="Code-objective mismatch"):
        decompose(a)


def test_incomplete_source_case_set_rejected():
    with pytest.raises(ValueError,match="540-case"):
        decompose(cases().iloc[:-1])
