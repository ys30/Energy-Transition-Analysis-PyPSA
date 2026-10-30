import pandas as pd
from energy_transition.eia2024_plant_qualification_match import reconcile

def test_ba_mismatch_and_qualified_absolute_energy():
    q=pd.DataFrame([
      {"source_row_id":1,"plant_id":"42","ba_code":"CISO","fuel":"WND","qualified":True,"annual_reported_mwh":-20.},
      {"source_row_id":2,"plant_id":"43","ba_code":"BPAT","fuel":"WND","qualified":True,"annual_reported_mwh":100.},
      {"source_row_id":3,"plant_id":"99","ba_code":"BPAT","fuel":"SUN","qualified":False,"annual_reported_mwh":10.}])
    g=pd.DataFrame([
      {"plant_id":"42","ba_code":"CISO","crosswalk_status":"matched"},
      {"plant_id":"43","ba_code":"CISO","crosswalk_status":"matched"}])
    rows,summary,report=reconcile(q,g)
    assert report["ba_disagreement_rows"]==1
    assert report["unmatched_or_ambiguous_rows"]==1
    assert report["all_qualified_abs_mwh"]==120
    assert report["matched_same_ba_qualified_abs_mwh"]==20
    assert len(summary)==3
