import numpy as np
import pandas as pd
import pytest

from energy_transition.paper_s_marginal_duration import derive
from test_paper_s_lp_objective_certification import cases


def test_full_540_case_grid_has_nine_annual_comparisons():
    rows = derive(cases())
    assert len(rows) == 9
    assert (rows.zones == 20).all()
    # Synthetic test: at duration 0, charge 0; at 4 and 8, charge 100.
    s = rows.iloc[0]
    assert np.isclose(s.unused_renewable_mwh_reduction_0to4h, 2000)
    assert np.isclose(s.unused_renewable_mwh_reduction_4to8h, 0)
    assert np.isclose(s.objective_illustrative_variable_usd_reduction_0to4h, 152000)
    assert np.isclose(s.objective_illustrative_variable_usd_reduction_4to8h, 0)


def test_missing_one_shape_duration_in_a_zone_rejected_even_if_population_restored():
    a = cases()
    # Duplicate key deliberately preserves 540 count, should fail closed.
    a.iloc[0] = a.iloc[1]
    with pytest.raises(ValueError, match="duplicate|Incomplete"):
        derive(a)


def test_corrupted_lp_objective_is_rejected_before_reporting_marginals():
    a = cases()
    a.loc[0, "objective_illustrative_variable_usd"] += 100
    with pytest.raises(ValueError, match="Code-objective mismatch"):
        derive(a)


def test_missing_year_case_rejected():
    with pytest.raises(ValueError, match="540-case"):
        derive(cases().iloc[:-1])


def test_nan_value_rejected():
    a = cases()
    a.loc[0, "unused_renewable_mwh"] = np.nan
    with pytest.raises(ValueError, match="Nonfinite"):
        derive(a)
