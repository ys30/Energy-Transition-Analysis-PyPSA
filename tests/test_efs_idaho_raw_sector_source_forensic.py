import numpy as np
import pandas as pd
import pytest
from energy_transition.efs_idaho_raw_sector_source_forensic import aggregate_idaho_sectors, one_year

def hourly_fixture():
    h=np.arange(1,8761,dtype=float)
    a=120.+15*np.cos(h/17)
    b=30.+10*np.sin(h/12)
    sector=pd.DataFrame({
      "Year":np.repeat(2030,17520),"Sector":np.repeat(["A","B"],8760),
      "LocalHourID":np.tile(np.arange(1,8761),2),
      "LoadMW":np.r_[a,b]
    })
    return sector,a+b

def test_sector_source_recovers_state_hour_and_holdout():
    sector,state=hourly_fixture()
    published=np.roll(state,2)
    r=one_year(sector,state,published,2030)
    assert r["exact_state_reconciliation"]
    assert r["source_original_state_mwh"]==pytest.approx(r["source_sector_sum_mwh"])
    assert r["baseline_nonwrap_full_mae_mw"]==pytest.approx(0)
    assert r["exhaustive_sector_shift_candidates"]==8
    assert r["baseline_interior_test_mae_mw"]==pytest.approx(0)
    assert not r["source_sector_shifts_have_physical_timezone_credibility"]

def test_wrong_original_state_data_is_rejected():
    sector,state=hourly_fixture()
    state[250]+=50
    with pytest.raises(ValueError,match="does not reproduce"):
        one_year(sector,state,np.roll(state,2),2030)

def test_bad_hour_and_missing_sector_detection(tmp_path):
    base,_=hourly_fixture()
    d=pd.concat([base.assign(Year=year) for year in (2030,2040,2050)],ignore_index=True)
    d["State"]="ID"
    d["Subsector"]="base"
    d["Electrification"]="Reference"
    d["TechnologyAdvancement"]="Moderate"
    d.to_csv(tmp_path/"raw.csv",index=False)
    source,meta=aggregate_idaho_sectors(tmp_path/"raw.csv",chunksize=4000)
    assert meta["grouped_sector_hour_rows"]==52560
    assert len(source)==52560
    wrong=d.iloc[:-1]
    wrong.to_csv(tmp_path/"missing.csv",index=False)
    with pytest.raises(ValueError,match="Incomplete"):
        aggregate_idaho_sectors(tmp_path/"missing.csv",chunksize=4000)
