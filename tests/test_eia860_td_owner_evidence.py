"""Evidence-only PUDL yearly-owner enrichment provenance checks."""
import pandas as pd
import pytest
from energy_transition.eia860_td_owner_evidence import enrich


def prepare(tmp_path, owners):
    q=tmp_path/"q.csv";o=tmp_path/"owners.csv"
    pd.DataFrame({"plant_id":["123","456"],"priority_reason":["repeat","repeat"]}).to_csv(q,index=False)
    pd.DataFrame(owners).to_csv(o,index=False)
    return q,o,tmp_path/"enriched.csv"


def test_year_filter_and_missing_owner(tmp_path):
    q,o,out=prepare(tmp_path,[
      {"plant_id_eia":"123","report_date":"2023-12-31",
       "transmission_distribution_owner_id":"X","transmission_distribution_owner_name":"Other",
       "transmission_distribution_owner_state":"NM"},
      {"plant_id_eia":"123","report_date":"2024-12-31",
       "transmission_distribution_owner_id":"12","transmission_distribution_owner_name":"Utility",
       "transmission_distribution_owner_state":"NM"}])
    report=enrich(q,o,out,2024)
    assert report["review_plants"]==2
    assert report["owner_source_matched_plants"]==1
    assert report["plants_with_owner_identity"]==1
    v=pd.read_csv(out,dtype={"plant_id":"string"})
    assert v.loc[v.plant_id.eq("123"),"evidence_tier"].iloc[0]=="G1_owner_only"
    assert v.loc[v.plant_id.eq("456"),"evidence_tier"].iloc[0]=="G0_geographic_only"
    assert not v.eligible_for_real_dispatch.any()


def test_duplicate_plant_year_rejected(tmp_path):
    row={"plant_id_eia":"123","report_date":"2024-12-31",
         "transmission_distribution_owner_id":"12",
         "transmission_distribution_owner_name":"Utility",
         "transmission_distribution_owner_state":"NM"}
    q,o,out=prepare(tmp_path,[row,row])
    with pytest.raises(ValueError,match="Ambiguous"):
        enrich(q,o,out,2024)
