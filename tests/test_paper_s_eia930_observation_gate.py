"""Synthetic EIA930 schema checks only: not a calibration to observations."""
import pandas as pd
import pytest
from energy_transition.paper_s_eia930_observation_gate import (
    validate_observations,validate_ba_crosswalk,audit
)


def fixture_rows():
    t=pd.date_range("2020-01-01 01:00:00+00:00",periods=24,freq="h")
    data=pd.DataFrame([
        dict(utc_hour_end=x.isoformat(),ba_code="TEST_BA",fuel=tech,
             net_generation_mwh=100.,source_url="https://www.eia.gov/electricity/930-content/",
             source_release="synthetic test only",observation_year=2020)
        for tech in ("wind","solar") for x in t
    ])
    mapping=pd.DataFrame([
        dict(ba_code="TEST_BA",state=state,state_share_of_ba_generation=.25,
             geometry_basis="audited_ba_state_geospatial_intersection",
             source_url="https://example.test/synthetic-geometry",mapping_year=2020,
             all_ba_counties_accounted_for=True,
             state_share_includes_unmodeled_regions=False)
        for state in ("AZ","CO","ID","WY")
    ])
    return data,mapping


def test_schema_is_not_empirical_validation():
    data,map_data=fixture_rows()
    a,b,meta=audit(data,map_data)
    assert len(a)==2 and len(b)==4
    assert meta["publication_validation_passed"] is False
    assert meta["numeric_measured_cf_validation_performed"] is False


def test_reject_naive_or_wrong_source_clock():
    data,m=fixture_rows()
    data.loc[0,"utc_hour_end"]="2020-01-01 01:00:00"
    # UTC labels lacking explicit timezone must be rejected at source-intake level.
    with pytest.raises(ValueError):
        validate_observations(data)


def test_reject_unverified_ba_as_state_mapping_and_double_allocation():
    data,m=fixture_rows()
    observed=validate_observations(data)
    bad=m.copy()
    bad.loc[0,"geometry_basis"]="BA_is_state"
    with pytest.raises(ValueError,match="Unverified"):
        validate_ba_crosswalk(bad,observed)
    bad=m.copy()
    bad.loc[0,"state_share_of_ba_generation"]=.6
    with pytest.raises(ValueError,match="allocated"):
        validate_ba_crosswalk(bad,observed)
