import pandas as pd
import pytest
from energy_transition.efs_55_positive_pd_state_concentration import summarize

def sample():
    rows=[]
    for year in [2030,2040,2050]:
        for id,state,w in [("a","NM",0.02),("b","NM",0.03),("c","CA",0.01)]:
            source={"NM":10000,"CA":20000}[state]
            rows.append({"year":year,"bus_id":id,"exported_state_code":state,
                         "source_v_nom_kv":13.8,"source_Pd":20.,
                         "source_LAF_state":w,"efs_state_annual_mwh":source,
                         "hypothetical_exported_state_laf_annual_mwh":source*w})
    return pd.DataFrame(rows)

def test_source_state_concentration_and_source_mass():
    table,r=summarize(sample())
    assert r["screened_unique_source_bus_count"]==3
    assert r["screened_source_bus_year_rows"]==9
    assert r["annual_state_concentration"][0]["largest_source_state"]=="NM"
    assert r["annual_state_concentration"][0]["hypothetical_annual_exposure_mwh"]==pytest.approx(700.)
    assert r["physically_correct_bus_level_efs_allocations_admitted"] is False
    assert len(table)==6

def test_source_weight_change_across_years_rejected():
    d=sample()
    d.loc[(d.bus_id=="a")&(d.year==2050),"source_LAF_state"]=0.1
    with pytest.raises(ValueError,match="identity"):
        summarize(d)

def test_false_annual_exposure_rejected():
    d=sample()
    d.loc[0,"hypothetical_exported_state_laf_annual_mwh"]=999.
    with pytest.raises(ValueError,match="not numerically"):
        summarize(d)
