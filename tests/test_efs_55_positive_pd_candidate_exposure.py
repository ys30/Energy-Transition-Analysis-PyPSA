import numpy as np
import pandas as pd
import pytest
from energy_transition.efs_55_positive_pd_candidate_exposure import screening

class Network:
    def __init__(self):
        ids=[str(i) for i in range(879)]
        self.buses=pd.DataFrame({
            "Pd":[2.]*55+[0.]*824,
            "LAF_state":[0.01]*879,
            "state":["New Mexico"]*879,
            "v_nom":[13.8]*877+[115.]*2,
            "substation_off":[False]*879,
        },index=ids)
        self.lines=pd.DataFrame({"bus0":["877"],"bus1":["878"]})
        self.transformers=pd.DataFrame(columns=["bus0","bus1"])

def efs():
    state_codes=["AZ","CA","CO","ID","MT","NM","NV","OR","UT","WA","WY"]
    return pd.MultiIndex.from_product([[2030,2040,2050],state_codes,range(1,8761)],
        names=["year","state","local_hour_id"]).to_frame(index=False).assign(load_mw=10.)

def test_source_evidence_stays_hypothetical():
    table,r=screening(Network(),efs())
    assert len(table)==165
    assert r["positive_source_pd_zero_degree_bus_count"]==55
    assert r["candidate_bus_year_rows"]==165
    assert r["source_positive_pd_sum_mw"]==pytest.approx(110.)
    assert r["planning_year_rows"][0]["hypothetical_exported_state_laf_annual_mwh"]==pytest.approx(48180)
    assert not r["direct_physically_validated_efs_load_attached_to_55_buses"]
    assert not r["full_western_opf_solved"]

def test_missing_efs_year_fails_closed():
    d=efs()
    with pytest.raises(ValueError,match="cohort"):
        screening(Network(),d.loc[d.year!=2050].copy())

def test_duplicate_efs_hour_fails_closed():
    d=efs()
    d=pd.concat([d,d.iloc[[0]]],ignore_index=True)
    with pytest.raises(ValueError,match="Missing or duplicate"):
        screening(Network(),d)
