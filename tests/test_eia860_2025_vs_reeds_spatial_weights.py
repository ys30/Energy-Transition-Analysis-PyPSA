import numpy as np
import pandas as pd
import pytest
from energy_transition.eia860_2025_vs_reeds_spatial_weights import (
    norm_county,census_map,contrast,
)

def test_county_name_normalization_is_explicit_not_fuzzy():
    assert norm_county("La Plata County")=="laplata"
    assert norm_county("La Plata")=="laplata"
    assert norm_county("St. Louis")=="stlouis"
    assert norm_county(None)==""

def test_official_census_pipe_delimited_fips(tmp_path):
    p=tmp_path/"counties.txt"
    p.write_text("STATE|STATEFP|COUNTYFP|COUNTYNS|COUNTYNAME|CLASSFP|FUNCSTAT\n"
                 "AZ|04|013|00037026|Maricopa County|H1|A\n"
                 "CO|08|067|00198146|La Plata County|H1|A\n")
    m=census_map(p)
    assert m.loc[m.state.eq("AZ"),"county_fips"].iloc[0]=="04013"
    assert m.loc[m.state.eq("CO"),"county_norm"].iloc[0]=="laplata"

def test_county_weight_contrast_excludes_unmapped_from_normalization():
    fleet=pd.DataFrame([
     {"state":"AZ","technology":"pv","county_fips":"04013",
      "nameplate_mw_ac":20.,"geographic_mapping_found":True},
     {"state":"AZ","technology":"pv","county_fips":"04001",
      "nameplate_mw_ac":10.,"geographic_mapping_found":True},
     {"state":"AZ","technology":"wind","county_fips":"04013",
      "nameplate_mw_ac":5.,"geographic_mapping_found":True},
     {"state":"AZ","technology":"wind","county_fips":None,
      "nameplate_mw_ac":5.,"geographic_mapping_found":False},
    ])
    potential=pd.DataFrame([
      {"state":"AZ","technology":"pv","county_fips":"04013","source_potential_mw_original_basis":10.},
      {"state":"AZ","technology":"pv","county_fips":"04001","source_potential_mw_original_basis":10.},
      {"state":"AZ","technology":"wind","county_fips":"04013","source_potential_mw_original_basis":2.},
    ])
    for state,code in [("CO","08001"),("ID","16001"),("WY","56001")]:
        for tech in ("wind","pv"):
            potential.loc[len(potential)]={"state":state,"technology":tech,
                   "county_fips":code,"source_potential_mw_original_basis":1.}
    summary,county=contrast(fleet,potential)
    az=summary.set_index(["state","technology"])
    assert az.loc[("AZ","wind"),"county_mapping_capacity_coverage"]==pytest.approx(.5)
    assert az.loc[("AZ","pv"),"fleet_to_potential_total_variation"]==pytest.approx(1/6)
    assert az.loc[("AZ","wind"),"eia_fleet_capacity_in_zero_reeds_potential_counties_fraction"]==0.
    assert len(summary)==8
