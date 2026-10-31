import pandas as pd
from energy_transition.eia930_generation_audit import summarize_net_generation

def test_generation_audit_keeps_negative_and_missing():
    f=pd.DataFrame({"period":pd.to_datetime(["2024-01-01T00:00Z","2024-01-01T01:00Z","2024-01-01T02:00Z"]),
      "respondent":["CISO"]*3,"value":[25.0,-2.0,float("nan")]})
    s=summarize_net_generation(f,2024,["CISO"])
    row=s.iloc[0]
    assert row.negative_value_hours==1
    assert row.missing_value_hours==1
    assert row.reported_net_generation_mwh_nonmissing_only==23.0
    assert not bool(row.complete)

def test_missing_timestamps_detected():
    hours=pd.date_range("2024-01-01", "2025-01-01", freq="h", inclusive="left", tz="UTC")
    hours=hours.delete(100)
    f=pd.DataFrame({"period":hours,"respondent":"CISO","value":1.0})
    audit=summarize_net_generation(f,2024,["CISO"]).iloc[0]
    assert audit.missing_timestamp_hours==1
    assert "2024-01-05" in audit.first_missing_timestamp_utc
    assert not bool(audit.complete)


def test_verified_ciso_24_hour_gap_is_timestamp_gap_not_null_values():
    hours=pd.date_range("2024-01-01","2025-01-01",freq="h",inclusive="left",tz="UTC")
    missing=pd.date_range("2024-11-02T08:00Z",periods=24,freq="h")
    f=pd.DataFrame({"period":hours.difference(missing),"respondent":"CISO","value":1.0})
    audit=summarize_net_generation(f,2024,["CISO"]).iloc[0]
    assert audit.received_hours==8760
    assert audit.missing_timestamp_hours==24
    assert audit.missing_value_hours==0
    assert audit.first_missing_timestamp_utc=="2024-11-02T08:00:00+00:00"
    assert audit.last_missing_timestamp_utc=="2024-11-03T07:00:00+00:00"
    assert not bool(audit.complete)


def test_eia_ng_fetch_rejects_malformed_numeric_payload(monkeypatch):
    import io, json
    from energy_transition import eia930_generation_audit as audit
    class FakeResponse(io.BytesIO):
        def __enter__(self): return self
        def __exit__(self,*args): self.close()
    payload={"response":{"total":"1","data":[
        {"period":"2024-01-01T00","respondent":"CISO","value":"bad"}]}}
    monkeypatch.setattr(audit.urllib.request,"urlopen",
                        lambda *args,**kwargs: FakeResponse(json.dumps(payload).encode()))
    import pytest
    with pytest.raises(ValueError,match="malformed"):
        audit.fetch_net_generation(2024,["CISO"],api_key="dummy")


def test_eia_ng_fetch_rejects_early_empty_page(monkeypatch):
    import io, json
    from energy_transition import eia930_generation_audit as audit
    class FakeResponse(io.BytesIO):
        def __enter__(self): return self
        def __exit__(self,*args): self.close()
    payloads=[
        {"response":{"total":"2","data":[{"period":"2024-01-01T00","respondent":"CISO","value":"5"}]}},
        {"response":{"total":"2","data":[]}},
    ]
    calls=iter(payloads)
    monkeypatch.setattr(audit.urllib.request,"urlopen",
                        lambda *args,**kwargs: FakeResponse(json.dumps(next(calls)).encode()))
    import pytest
    with pytest.raises(ValueError,match="empty page"):
        audit.fetch_net_generation(2024,["CISO"],api_key="dummy")
