"""Synthetic HDF5 integration tests; no claim of publisher-byte authentication."""
import h5py
import numpy as np
import pandas as pd
import pytest

import energy_transition.reeds2022_county_original_extract as extract


def test_explicit_supply_schema_supports_separate_resource_columns():
    frame=pd.DataFrame({"cls":["1","2"],"county":["04001","08001"]})
    assert extract.assemble_capacity_keys(
        frame,class_col="cls",region_col="county")==["1|p04001","2|p08001"]
    with pytest.raises(ValueError,match="Explicit"):
        extract.assemble_capacity_keys(frame)


def test_synthetic_2012_county_source_extraction_and_manifest(tmp_path,monkeypatch):
    # The official publisher MD5 is deliberately replaced only in a synthetic test.
    monkeypatch.setattr(extract,"require_md5",lambda path,expected: expected)
    names=["1|p04001","1|p08001","1|p16001","1|p56001"]
    dates=pd.date_range("2012-01-01",periods=8760,freq="h")
    h5=tmp_path/"synthetic.h5"
    with h5py.File(h5,"w") as h:
        h.create_dataset("data",data=np.tile([0.1,0.2,0.3,0.4],(8760,1)))
        h.create_dataset("columns",data=np.asarray(names,dtype="S20"))
        h.create_dataset("index_0",data=np.asarray(dates.astype(str),dtype="S25"))
    cap=tmp_path/"capacity.csv"
    pd.DataFrame({"class":[1]*4,"county":["04001","08001","16001","56001"],
                  "available_mw":[10,20,30,40]}).to_csv(cap,index=False)
    info=extract.audit_and_extract(
        tech="wind",h5_path=h5,supply_path=cap,capacity_key_col=None,
        class_col="class",region_col="county",capacity_mw_col="available_mw",
        capacity_basis="ac",cf_encoded_scale=None,out_dir=tmp_path/"out",
        chunk_size=168)
    assert info["empirical_hour_energy_join_admitted"] is False
    assert info["state_available_capacity_mw"]=={
        "AZ":10.0,"CO":20.0,"ID":30.0,"WY":40.0}
    state=pd.read_csv(tmp_path/"out"/
        "reeds2022_wind_2012_four_state_instantaneous_cf.csv")
    assert state.shape==(8760,5)
    np.testing.assert_allclose(state[["AZ","CO","ID","WY"]].iloc[0],
                               [0.1,0.2,0.3,0.4])


def test_missing_2012_source_rows_are_rejected(tmp_path,monkeypatch):
    monkeypatch.setattr(extract,"require_md5",lambda path,expected:expected)
    h5=tmp_path/"short.h5"
    with h5py.File(h5,"w") as h:
        h.create_dataset("data",data=np.zeros((1,1)))
        h.create_dataset("columns",data=[b"1|p04001"])
        h.create_dataset("index_0",data=[b"2012-01-01 00:00:00"])
    cap=tmp_path/"capacity.csv"
    pd.DataFrame({"key":["1|p04001"],"mw":[1]}).to_csv(cap,index=False)
    with pytest.raises(ValueError,match="8760"):
        extract.audit_and_extract(
            tech="wind",h5_path=h5,supply_path=cap,capacity_key_col="key",
            class_col=None,region_col=None,capacity_mw_col="mw",
            capacity_basis="ac",cf_encoded_scale=None,out_dir=tmp_path/"out")
