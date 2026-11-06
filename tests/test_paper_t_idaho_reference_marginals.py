import pandas as pd
import pytest
from energy_transition.paper_t_idaho_reference_marginals import make,validate

def fixture():
    return pd.DataFrame([
        {"year":y,"state":s,"group_type":t,"reference_index_label":v,
         "compared_hours":100,"mean_absolute_error_mw":20. if s=="ID" else .25}
        for y in (2030,2040,2050) for s in ("ID","AZ","CA")
        for t,values in (("month",range(1,13)),("hour",range(24)))
        for v in values
    ])

def test_no_invented_joint_heatmap(tmp_path):
    m=make(fixture(),tmp_path)
    assert m["archived_group_rows"]==324
    assert not m["figure_is_joint_heatmap"]
    assert not m["ReEDS_reference_clock_is_EFS2020_physical_UTC"]
    assert len(list(tmp_path.glob("*.svg")))==1
    assert len(list(tmp_path.glob("*.png")))==1

def test_missing_reference_hour_rejected():
    with pytest.raises(ValueError,match="Incomplete"):
        validate(fixture().iloc[:-1])

def test_negative_error_rejected():
    d=fixture();d.loc[1,"mean_absolute_error_mw"]=-1.
    with pytest.raises(ValueError,match="Invalid"):
        validate(d)
