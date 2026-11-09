import pandas as pd
import pytest
from energy_transition.paper_s_bound_dual_figures import plot

def cases():
    r=[]
    for group,state in ((1,"Arizona"),(7,"Wyoming")):
        for shape,p,e in (("flat_50pct",.25,1.),
                          ("ordinal24_wave_A",.125,.5),
                          ("ordinal24_wave_A",.25,1.),
                          ("ordinal24_wave_B",.25,1.)):
            r.append({"source_shape_group":group,"state":state,
               "synthetic_supply_shape":shape,
               "battery_power_peak_ratio":p,"battery_energy_peak_hours":e,
               "dual_objective_derivative_power_usd_per_mw":-1.,
               "dual_objective_derivative_energy_usd_per_mwh":-10.,
               "forward_difference_power_usd_per_mw":-1.,
               "forward_difference_energy_usd_per_mwh":-10.})
    return pd.DataFrame(r)

def test_source_reconciled_plot_created(tmp_path):
    plot(cases(),tmp_path)
    assert (tmp_path/"Figure_S14_dual_capacity_marginal_values.svg").stat().st_size>1000

def test_nonmatching_source_duals_rejected(tmp_path):
    x=cases();x.loc[0,"forward_difference_energy_usd_per_mwh"]=-100
    with pytest.raises(ValueError,match="disagree"):plot(x,tmp_path)

def test_missing_source_configuration_rejected(tmp_path):
    with pytest.raises(ValueError,match="eight"):plot(cases().iloc[:-1],tmp_path)
