import numpy as np
import pandas as pd
import pytest
from energy_transition.reeds2022_eia2025_spatial_reweighted_lp import (
    county_tech_weights,paired_summary,DESIGNS,DURATIONS,
)

def table():
    return pd.DataFrame({
        "column":["1|p04001","2|p04001","1|p04003","1|p08001"],
        "resource_class":["1","2","1","1"],
        "county_fips":["04001","04001","04003","08001"],
        "state_fips":["04","04","04","08"],
        "capacity_mw":[10.,30.,60.,12.]})
def shares():
    return pd.DataFrame({"state":["AZ","AZ"],"technology":["wind","wind"],
        "county_fips":pd.Series(["04001","04003"],dtype="string"),
        "eia2025_share_among_geocoded":[.9,.1]})

def test_source_class_conditioning_preserves_county_totals():
    p,e=county_tech_weights(table(),shares(),"wind","AZ")
    np.testing.assert_allclose(p,[.1,.3,.6,0])
    np.testing.assert_allclose(e,[.225,.675,.1,0])
    assert np.sum(e)==pytest.approx(1.)

def test_eia_site_shares_missing_resource_classes_fails():
    x=shares()
    x.loc[1,"county_fips"]="04099"
    with pytest.raises(ValueError,match="missing ReEDS"):
        county_tech_weights(table(),x,"wind","AZ")

def test_eia_weights_must_sum_one():
    x=shares()
    x.loc[0,"eia2025_share_among_geocoded"]=.5
    with pytest.raises(ValueError,match="sum exactly"):
        county_tech_weights(table(),x,"wind","AZ")

def fake_lp():
    rows=[]
    for state in ("AZ","CO","ID","WY"):
        for scheme in DESIGNS:
            for duration in DURATIONS:
                obj=10000-duration*100
                if scheme==DESIGNS[1]:obj-=duration*10
                rows.append({"state":state,"county_weight_scheme":scheme,
                             "battery_duration_h":duration,
                             "objective_illustrative_variable_usd":obj,
                             "storage_capacity_mwh":duration*100})
    return pd.DataFrame(rows)
def test_24_lp_paired_hurdles_and_geo_comparisons():
    pair,geo=paired_summary(fake_lp())
    assert len(pair)==8 and len(geo)==4
    assert not geo["10usd_energy_annuity_screen_flips"].any()
    np.testing.assert_allclose(geo.incremental_4_to_8h_energy_annuity_usd_per_kwh_year_EIA_minus_potential,.0001)
