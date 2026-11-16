"""No invented BA mapping: inspect synthetic Schedule2/4 source rows only."""
import pytest
from energy_transition.paper_s_eia930a_2023_ba_renewable_crosswalk import aggregate

def generator(ba="PNM",fuel="wind",state="NM",sheet="SCH 2",plant="1",gen="A",mw=100,when=True):
    return dict(sheet=sheet,ba_code=ba,fuel=fuel,
        state_for_geography=state,EIA_plant_id=plant,EIA_generator_id=gen,
        EIA930A_plant_id="",EIA930A_generator_id="",
        operating_by_july_2023_candidate=when,candidate_capacity_mw=mw)

def test_annual_source_not_pretended_hourly_and_schedule4_excluded():
    source=[
        generator(),
        generator(ba="PNM",fuel="wind",state="AZ",plant="2",mw=90),
        generator(ba="PNM",fuel="solar",state="NM",plant="3",mw=60),
        generator(ba="PNM",fuel="wind",state="NM",sheet="SCH 4",plant="4",mw=900),
        generator(ba="PNM",fuel="wind",state="NM",plant="5",mw=500,when=False),
    ]
    caps,audit=aggregate(source)
    x={(r["ba_code"],r["fuel"],r["generator_state"]):r["candidate_nameplate_mw"] for r in caps}
    assert x=={("PNM","wind","NM"):100,("PNM","wind","AZ"):90,("PNM","solar","NM"):60}
    assert any(row["schedule"]=="SCH 4" for row in audit)

def test_duplicate_generator_id_fails_closed():
    a=generator()
    with pytest.raises(ValueError,match="Duplicate"):
        aggregate([a,dict(a)])

def test_undefined_capacity_is_counted_not_assumed_zero_installed():
    caps,_=aggregate([generator(mw=None)])
    assert len(caps)==1
    assert caps[0]["rows_with_unresolved_capacity_or_id"]==1
