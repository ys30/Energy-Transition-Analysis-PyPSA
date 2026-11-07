import copy
from datetime import datetime,timedelta
import pytest
from energy_transition.paper_t_nasa_power_external_clock import audit,parse_hourly,request_url

def fixture():
    start=datetime(2024,1,15)
    u={}
    l={}
    for i in range(96):
        date=start+timedelta(hours=i)
        key=date.strftime("%Y%m%d%H")
        u[key]=15.+float((i*7)%19)/10
        # NASA LST timestamp H maps physical UTC H+7 for longitude -105.
        shifted=i+7
        l[key]=15.+float((shifted*7)%19)/10
    return ({"properties":{"parameter":{"T2M":u}}},
            {"properties":{"parameter":{"T2M":l}}})

def test_real_api_schema_publisher_shift_contract():
    u,l=fixture()
    result=audit(u,l)
    assert result["nonwrapping_matched_hours"]==89
    assert result["publisher_expected_LST_minus_UTC_hours"]==-7
    assert result["publisher_time_normalized_hour_mae_celsius"]==0.
    assert result["naive_equal_hour_label_mae_celsius"]>0
    assert result["UTC_and_LST_independent_physical_observations"] is False

def test_do_not_accept_missing_hour():
    u,l=fixture()
    del l["properties"]["parameter"]["T2M"]["2024011501"]
    with pytest.raises(ValueError,match="missing or extra"):audit(u,l)

def test_do_not_accept_unrelated_source_values():
    u,l=fixture()
    l["properties"]["parameter"]["T2M"]["2024011700"]=444.0
    with pytest.raises(ValueError,match="conversion failed"):audit(u,l)

def test_explicit_time_standard_required():
    assert "time-standard=UTC" in request_url("UTC")
    assert "time-standard=LST" in request_url("LST")
    with pytest.raises(ValueError):request_url("local")
