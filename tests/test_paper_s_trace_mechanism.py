import numpy as np
import pytest
from energy_transition.paper_s_trace_mechanism import run_lengths,summarize

def test_run_lengths_do_not_wrap_year_boundary():
    assert run_lengths([True,True,False,True,True,True]).tolist()==[2,3]
    assert run_lengths([False,False]).tolist()==[]
    assert run_lengths([True,True,True]).tolist()==[3]

def test_incomplete_population_rejected():
    import pandas as pd
    with pytest.raises(ValueError,match="nine full-year"):
        summarize(pd.DataFrame(),pd.DataFrame())
