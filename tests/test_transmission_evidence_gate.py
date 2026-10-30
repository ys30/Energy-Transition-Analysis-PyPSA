import pandas as pd
import pytest
from energy_transition.transmission_evidence_gate import screen_transmission_inputs


def test_missing_evidence_never_yields_fabricated_interconnection():
    result=screen_transmission_inputs(pd.DataFrame(columns=[
        "from_ba","to_ba","capacity_mw","reactance_pu","source_url","source_year"]))
    assert result["ready"] is False
    assert result["accepted_edges"]==0


def test_sourced_transmission_record_is_screening_only():
    data=pd.DataFrame([{
        "from_ba":"CISO","to_ba":"BPAT","capacity_mw":1000.0,
        "reactance_pu":0.15,"source_url":"https://example.org/grid-study",
        "source_year":2024,
    }])
    result=screen_transmission_inputs(data)
    assert result["ready"] is True
    assert result["accepted_edges"]==1
    assert "not_yet_grid_calibrated" in result["reason"]


@pytest.mark.parametrize("capacity,reactance",[(0,0.2),(100,float("nan")),(100,-0.1)])
def test_reject_unsupported_or_invalid_physics(capacity,reactance):
    data=pd.DataFrame([{"from_ba":"CISO","to_ba":"BPAT",
        "capacity_mw":capacity,"reactance_pu":reactance,
        "source_url":"https://example.org/report","source_year":2024}])
    with pytest.raises(ValueError):
        screen_transmission_inputs(data)
