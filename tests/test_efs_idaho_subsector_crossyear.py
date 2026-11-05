import numpy as np
import pandas as pd
import pytest
from energy_transition.efs_idaho_subsector_crossyear import (
    subsector_annual_source,frozen_shift_transfer,SECTORS
)

def synthetic_original():
    hours=np.arange(1,8761)
    blocks=[]
    for year in (2030,2040,2050):
        for j,s in enumerate(SECTORS):
            v=100+10*j+2*np.sin(hours/20)
            blocks.append(pd.DataFrame({
                "Electrification":"Reference",
                "TechnologyAdvancement":"Moderate","State":"ID",
                "Year":year,"LocalHourID":hours,"Sector":s,
                "Subsector":"Fixture", "LoadMW":v}))
    return pd.concat(blocks,ignore_index=True)

def test_original_subsector_annual_source_conservation(tmp_path):
    d=synthetic_original();path=tmp_path/"efs.csv"
    d.to_csv(path,index=False)
    sums,meta=subsector_annual_source(path,chunk_size=8000)
    assert len(sums)==12
    assert meta["source_rows_selected"]==len(d)
    for year in (2030,2040,2050):
        assert sums.loc[sums.Year==year,"original_load_mwh"].sum()==pytest.approx(
            d.loc[d.Year==year,"LoadMW"].sum())
        assert sums.loc[sums.Year==year,"original_year_load_share"].sum()==pytest.approx(1.0)

def test_frozen_shift_is_not_refit_in_target_year():
    d=synthetic_original()
    sec=d.loc[d.Year==2040,["Year","Sector","LocalHourID","LoadMW"]]
    original=sec.groupby("LocalHourID").LoadMW.sum().to_numpy()
    hdf5=np.roll(original,2)
    a=frozen_shift_transfer(sec,original,hdf5,2040)
    assert a["baseline_heldout_mae_mw"]==pytest.approx(0)
    assert a["baseline_firsthalf_mae_mw"]==pytest.approx(0)
    assert a["firsthalf_hours"]+a["heldout_hours"]==8756
    assert a["heldout_improvement_mw"]<=1e-9
    assert not a["fit_selection_repeated_on_this_year"]
    assert not a["candidate_shift_physical_timezone_verified"]

def test_original_archive_disagreement_rejected():
    d=synthetic_original()
    sec=d.loc[d.Year==2030,["Year","Sector","LocalHourID","LoadMW"]]
    original=sec.groupby("LocalHourID").LoadMW.sum().to_numpy()
    original[7]+=100.
    with pytest.raises(ValueError,match="does not match"):
        frozen_shift_transfer(sec,original,np.roll(original,2),2030)

def test_missing_original_subsector_source_values_fail(tmp_path):
    d=synthetic_original()
    d.iloc[5,d.columns.get_loc("LoadMW")]=float("nan")
    p=tmp_path/"invalid.csv"
    d.to_csv(p,index=False)
    with pytest.raises(ValueError,match="Null"):
        subsector_annual_source(p)
