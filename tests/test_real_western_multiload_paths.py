"""Tests for distinguishing static loads from admitted EFS hourly profiles."""
import numpy as np
import pandas as pd
import pypsa
import pytest
from energy_transition.real_western_multiload_paths import audit


def make_network(path, bad_profile=False):
    n=pypsa.Network()
    n.set_snapshots(pd.date_range("2030-01-01",periods=2,freq="h"))
    for b in ("a","b","c"):
        n.add("Bus",b,v_nom=230)
    for name,u,v in (("l1","a","b"),("l2","b","c")):
        n.add("Line",name,bus0=u,bus1=v,r=0.1,x=0.2,s_nom=200)
    n.add("Load","static_source",bus="c",p_set=0)
    n.add("Load","EFS_2030_alpha",bus="a",p_set=[10.0, 11.0])
    n.add("Load","EFS_2030_beta",bus="b",p_set=[5.0, float("nan") if bad_profile else 6.0])
    n.export_to_netcdf(str(path))


def test_static_source_without_dynamic_profile_is_ignored(tmp_path):
    path=tmp_path/"network.nc"
    make_network(path)
    result=audit(path)
    assert result["positive_efs_load_buses"]==2
    assert result["admissible_ac_line_path_pairs"]==1
    assert result["top_candidate_paths"][0]["line_ids"]==["l1"]


def test_bad_dynamic_efs_profile_rejected(tmp_path):
    path=tmp_path/"network.nc"
    make_network(path,bad_profile=True)
    with pytest.raises(ValueError,match="Invalid EFS hourly"):
        audit(path)
