"""EIA930 API BA fuel constraints; all records are synthetic unit fixtures."""
import json
import pytest
from energy_transition.paper_s_eia930_observed_ba_pilot import (
    url_for,parse_payload
)


def test_explicit_2023_source_api_facets():
    url=url_for("PNM","wind","2023-07-01T00","2023-07-07T23")
    assert "electricity/rto/fuel-type-data/data/" in url
    assert "facets%5Brespondent%5D%5B%5D=PNM" in url
    assert "facets%5Bfueltype%5D%5B%5D=WND" in url
    with pytest.raises(ValueError):
        url_for("UNVERIFIED","solar","2023-07-01T00","2023-07-07T23")


def test_source_rows_are_measured_ba_not_state():
    payload={"response":{"total":"2","data":[
        {"period":"2023-07-01T00","respondent":"PNM","fueltype":"WND",
         "value":"45.8","value-units":"megawatthours"},
        {"period":"2023-07-01T01","respondent":"PNM","fueltype":"WND",
         "value":"-3.5","value-units":"megawatthours"}]}}
    f=parse_payload(json.dumps(payload).encode(),"PNM","wind")
    assert len(f)==2
    assert f.net_generation_mwh.tolist()==[45.8,-3.5]
    assert "state" not in f.columns
    assert all("+00:00" in s for s in f.utc_hour_end)


def test_reject_cross_fuel_or_incomplete_pagination():
    payload={"response":{"total":2,"data":[
        {"period":"2023-07-01T00","respondent":"PNM","fueltype":"SUN",
         "value":"1","value-units":"megawatthours"}]}}
    with pytest.raises(ValueError,match="pagination"):
        parse_payload(json.dumps(payload).encode(),"PNM","wind")
    payload["response"]["total"]=1
    with pytest.raises(ValueError,match="facet"):
        parse_payload(json.dumps(payload).encode(),"PNM","wind")
