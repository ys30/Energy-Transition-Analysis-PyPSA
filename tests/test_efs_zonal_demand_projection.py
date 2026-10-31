import pytest
from energy_transition.efs_zonal_demand_projection import allocate_state_demand


def test_conservation_by_snapshot():
    demand = [{"state":"CA","snapshot":"2024-01-01T00:00","demand_mw":100},
              {"state":"CA","snapshot":"2024-01-01T01:00","demand_mw":200}]
    weights = [{"state":"CA","zone":"p8","weight":0.4},
               {"state":"CA","zone":"p9","weight":0.6}]
    result = allocate_state_demand(demand, weights)
    assert len(result) == 4
    assert sum(x["demand_mw"] for x in result if x["snapshot"].endswith("00:00")) == pytest.approx(100)
    assert sum(x["demand_mw"] for x in result if x["snapshot"].endswith("01:00")) == pytest.approx(200)


@pytest.mark.parametrize("weights", [
    [{"state":"CA","zone":"p8","weight":0.3}],
    [{"state":"CA","zone":"p8","weight":float("nan")}],
    [{"state":"CA","zone":"p8","weight":0.5},{"state":"CA","zone":"p8","weight":0.5}],
])
def test_bad_weights_rejected(weights):
    with pytest.raises(ValueError):
        allocate_state_demand([{"state":"CA","snapshot":"t","demand_mw":100}],weights)


def test_duplicate_snapshot_rejected():
    rows = [{"state":"NM","snapshot":"t","demand_mw":100}]*2
    with pytest.raises(ValueError):
        allocate_state_demand(rows,[{"state":"NM","zone":"p31","weight":1}])


def test_missing_state_rejected():
    with pytest.raises(ValueError):
        allocate_state_demand([{"state":"CA","snapshot":"t","demand_mw":100}],
                              [{"state":"NM","zone":"p31","weight":1}])


def test_misaligned_state_snapshots_rejected():
    demand = [
        {"state":"CA","snapshot":"2024-01-01T00:00","demand_mw":100},
        {"state":"CA","snapshot":"2024-01-01T01:00","demand_mw":110},
        {"state":"NM","snapshot":"2024-01-01T00:00","demand_mw":50},
    ]
    weights = [{"state":"CA","zone":"p8","weight":1},
               {"state":"NM","zone":"p31","weight":1}]
    with pytest.raises(ValueError, match="time coverage differs"):
        allocate_state_demand(demand, weights)


def test_zone_cannot_be_shared_between_states():
    demand = [
        {"state":"CA","snapshot":"2024-01-01T00:00Z","demand_mw":100},
        {"state":"NM","snapshot":"2024-01-01T00:00Z","demand_mw":50},
    ]
    weights = [{"state":"CA","zone":"p8","weight":1},
               {"state":"NM","zone":"p8","weight":1}]
    with pytest.raises(ValueError, match="multiple states"):
        allocate_state_demand(demand, weights)


def test_empty_state_demand_is_explicitly_rejected():
    with pytest.raises(ValueError, match="No state demand snapshots"):
        allocate_state_demand([], [{"state":"CA","zone":"p8","weight":1}])
