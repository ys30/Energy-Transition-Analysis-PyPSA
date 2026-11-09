import numpy as np
import pandas as pd
import pytest
from energy_transition.paper_s_orthogonal_interactions import audit

def samples():
    rows=[]
    for group in range(1,8):
      for shape in ("flat_50pct","ordinal24_wave_A","ordinal24_wave_B"):
        for power in (.125,.25,.5):
          for energy in (.5,1.,2.):
            # Baseline objective decreases as product p*e grows:
            # convex/cross interaction is positive over the grid.
            firm=1000-100*power*energy
            unused=100.
            cost=90*firm+5*(2000-unused)
            rows.append({"source_shape_group":group,"state":f"S{group}",
               "reeds_zone":f"p{group}","synthetic_supply_shape":shape,
               "battery_power_peak_ratio":power,"battery_energy_peak_hours":energy,
               "solver_status":"optimal","source_hours":8760,"storage_terminal_soc_mwh":0.,
               "firm_generation_mwh":firm,"unused_renewable_mwh":unused,
               "storage_discharge_to_load_mwh":100*power*energy,
               "objective_illustrative_variable_usd":cost})
    return pd.DataFrame(rows)

def test_complete_84_interaction_rectangles_and_objective_identity():
    a=audit(samples())
    assert len(a)==84
    assert a.interaction_positive_over_one_usd.all()
    assert (a.mw_mwh_objective_interaction_usd>0).all()

def test_fail_on_missing_factorial_cell():
    with pytest.raises(ValueError,match="189-case"):
        audit(samples().iloc[:-1])

def test_fail_when_source_cost_identity_tampered():
    a=samples()
    a.loc[0,"objective_illustrative_variable_usd"]+=5000
    with pytest.raises(ValueError,match="objective|identity|More"):
        audit(a)

def test_nonmonotone_optimum_is_rejected():
    a=samples()
    a.loc[(a.source_shape_group==1)&(a.synthetic_supply_shape=="flat_50pct")&
          (a.battery_power_peak_ratio==.5)&(a.battery_energy_peak_hours==2.),
          "objective_illustrative_variable_usd"]+=100000
    with pytest.raises(ValueError,match="More"):
        audit(a)
