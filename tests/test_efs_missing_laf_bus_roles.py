"""Missing LAF bus roles must remain evidence, never imputed shares."""
import pandas as pd
import pytest
from types import SimpleNamespace
from energy_transition.efs_missing_laf_bus_roles import classify_missing_laf_buses


def fixture():
    buses = pd.DataFrame({
        "reeds_state": ["CA", "CA", "OR"],
        "reeds_zone": ["p9", "p9", "p5"],
        "LAF_state": [0.4, float("nan"), float("nan")],
    }, index=["a", "missing_load", "missing_no_load"])
    loads = pd.DataFrame({
        "bus": ["missing_load"], "p_set": [12.0],
    }, index=["d1"])
    return SimpleNamespace(
        buses=buses, loads=loads,
        generators=pd.DataFrame({"bus": ["missing_no_load"]}),
        storage_units=pd.DataFrame({"bus": []}),
        lines=pd.DataFrame({"bus0": ["a"], "bus1": ["missing_no_load"]}),
        links=pd.DataFrame({"bus0": [], "bus1": []}),
        loads_t=SimpleNamespace(p_set=pd.DataFrame({"d1": [12.0, 10.0]}))
    )


def test_differentiate_missing_bus_with_load_from_non_load():
    r=classify_missing_laf_buses(fixture())
    assert r["missing_laf_bus_count"] == 2
    assert r["missing_laf_load_component_buses"] == 1
    assert r["missing_laf_static_nonzero_load_buses"] == 1
    assert r["missing_laf_dynamic_nonzero_load_buses"] == 1
    assert r["missing_laf_generator_buses"] == 1
    assert r["missing_laf_transmission_endpoint_buses"] == 1
    assert r["missing_laf_can_be_assumed_zero"] is False
    assert r["missing_laf_buses_may_be_excluded"] is False
    assert r["empirical_laf_admitted"] is False


def test_missing_bus_without_load_not_automatically_excluded():
    n=fixture()
    n.loads=n.loads.iloc[:0]
    n.loads_t.p_set=pd.DataFrame()
    r=classify_missing_laf_buses(n)
    assert r["missing_laf_load_component_buses"] == 0
    assert not r["missing_laf_buses_may_be_excluded"]


def test_required_geography_is_mandatory():
    n=fixture()
    n.buses=n.buses.drop(columns=["reeds_state"])
    with pytest.raises(ValueError, match="Required geographic"):
        classify_missing_laf_buses(n)
