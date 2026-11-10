import numpy as np
import pandas as pd
import pytest
from energy_transition.paper_s_window_hourly_redistribution import reconstruct,WINDOW,DAY_BLOCK

def test_locked_source_window_and_source_block_size():
    assert WINDOW=="middle_4001_4168"
    assert DAY_BLOCK==24

def test_incomplete_archived_source_fails_closed():
    hourly=pd.DataFrame({"synthetic_supply_shape":["flat_50pct"],"battery_duration_h":[0],
                           "local_hour_id":[1],"demand_mwh":[10.]})
    with pytest.raises(ValueError,match="source-hour chronology"):
        reconstruct(hourly,pd.DataFrame(),pd.DataFrame(),1)

def test_group_summation_identity_for_paired_hourly_vectors():
    hours=np.arange(1,8761)
    a=pd.DataFrame({"local_hour_id":hours,"storage_discharge_to_load_mwh":np.full(8760,5.),
                    "storage_charge_input_mwh":np.full(8760,2.),
                    "soc_end_mwh":np.full(8760,3.),"firm_generation_mwh":np.ones(8760),
                    "unused_renewable_mwh":np.zeros(8760)}).set_index("local_hour_id")
    b=a.copy()
    b.loc[4001:4168,"storage_discharge_to_load_mwh"]+=100
    b.loc[5000:5167,"storage_discharge_to_load_mwh"]-=2
    delta=b.storage_discharge_to_load_mwh-a.storage_discharge_to_load_mwh
    window=np.logical_and(hours>=4001,hours<=4168)
    inside=float(delta.to_numpy()@window)
    outside=float(delta.sum()-inside)
    assert abs(inside+outside-delta.sum())<1e-8
    assert np.isclose(inside,16800)
    assert np.isclose(outside,-336)
