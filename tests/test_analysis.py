from energy_transition.analysis import scenario_data,metrics,analyze

def test_generation_balance():
    assert (scenario_data().sum(axis=1)==100).all()

def test_renewables_increase():
    assert metrics(scenario_data()).renewable_share.is_monotonic_increasing

def test_emissions_decline():
    assert metrics(scenario_data()).emissions_mtco2.is_monotonic_decreasing

def test_figures(tmp_path):
    analyze(tmp_path)
    assert all((tmp_path/f).is_file() for f in ["generation_mix.png","renewable_share.png","emissions.png","metrics.csv"])
