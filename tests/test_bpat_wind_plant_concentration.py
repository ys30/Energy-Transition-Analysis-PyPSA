import pandas as pd
from energy_transition.bpat_wind_plant_concentration import summarize

def test_plant_concentration_with_multiple_source_rows():
    x=pd.DataFrame([
      {"source_row_id":1,"ba_code":"BPAT","fuel":"WND","plant_id":"10","qualified":True,"plant_match_status":"matched","qualified_generation_mwh":50.},
      {"source_row_id":2,"ba_code":"BPAT","fuel":"WND","plant_id":"10","qualified":True,"plant_match_status":"matched","qualified_generation_mwh":30.},
      {"source_row_id":3,"ba_code":"BPAT","fuel":"WND","plant_id":"11","qualified":True,"plant_match_status":"matched","qualified_generation_mwh":20.}])
    plants,report=summarize(x)
    assert report["source_rows"]==3
    assert report["distinct_plants"]==2
    assert report["qualified_eia923_wind_mwh"]==100
    assert plants.iloc[0].source_rows==2
    assert plants.iloc[0].share_of_qualified_bpat_wind==.8
