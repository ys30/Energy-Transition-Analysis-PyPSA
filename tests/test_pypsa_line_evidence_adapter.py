from types import SimpleNamespace
import pandas as pd
import pytest
from energy_transition.pypsa_line_evidence_adapter import add_screened_ba_lines


def record():
    return pd.DataFrame([{
        "from_ba":"CISO","to_ba":"BPAT","capacity_mw":1000.,
        "reactance_pu":0.1,"source_url":"https://example.org/provenance",
        "source_year":2024,"reactance_ohm":8.,"resistance_ohm":0.1,
        "nominal_kv":230.,"evidence_status":"independently_verified"
    }])


class FakeNetwork:
    def __init__(self):
        self.buses=pd.DataFrame({"v_nom":[230.,230.]},index=["CISO","BPAT"])
        self.lines=pd.DataFrame(index=pd.Index([],name="Line"))
        self.added=[]
    def add(self,*args,**kwargs):
        self.added.append((args,kwargs))


def test_evidence_line_maps_ohm_units_and_capacity_to_pypsa():
    n=FakeNetwork()
    result=add_screened_ba_lines(n,record())
    assert result["ready"] is True
    assert len(n.added)==1
    assert n.added[0][0][0]=="Line"
    assert n.added[0][1]["x"]==8.0
    assert n.added[0][1]["s_nom"]==1000.0


def test_unverified_line_is_rejected_before_network_mutation():
    n=FakeNetwork()
    data=record()
    data.loc[0,"evidence_status"]="unsourced"
    with pytest.raises(ValueError,match="independently verified"):
        add_screened_ba_lines(n,data)
    assert not n.added


def test_pu_cannot_be_misrepresented_as_ohms():
    data=record().drop(columns=["reactance_ohm"])
    with pytest.raises(ValueError,match="ohm"):
        add_screened_ba_lines(FakeNetwork(),data)
