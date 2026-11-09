import numpy as np
import pandas as pd
import pytest
from energy_transition.paper_s_parameter_robustness_figures import generate,validate,ORDER,SHAPES

def sample():
    rows=[]
    for group in range(1,8):
        for scenario in ORDER:
            for shape in SHAPES:
                rows.append({"source_shape_group":group,"scenario":scenario,
                  "synthetic_supply_shape":shape,
                  "additional_discharge_mwh":100.,
                  "avoided_firm_mwh":100.,"avoided_unused_mwh":105.,
                  "firm_unit_cost":90.,
                  "toy_objective_reduction_usd":8475.})
    return pd.DataFrame(rows)

def test_complete_source_and_svg_png(tmp_path):
    x=generate(sample(),tmp_path)
    assert x["source_marginal_comparisons"]==147
    assert (tmp_path/"Figure_S10_2030_parameter_robustness.svg").stat().st_size>1000

def test_duplicate_scenario_rejected():
    a=sample()
    a.iloc[1]=a.iloc[0]
    with pytest.raises(ValueError,match="147 unique"):validate(a)

def test_corrupted_objective_rejected():
    a=sample();a.loc[0,"toy_objective_reduction_usd"]+=1
    with pytest.raises(ValueError,match="objective source identity"):validate(a)
