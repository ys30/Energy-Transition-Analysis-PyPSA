import numpy as np
import pandas as pd
import pytest
from energy_transition.paper_s_source_shape_independence import compare

def trace(y,rank):
    return pd.DataFrame({"planning_year":2030,"state":"AZ","reeds_zone":f"p{rank}",
        "synthetic_supply_shape":"flat_50pct","battery_duration_h":0,
        "local_hour_id":np.arange(1,8761),"demand_mwh":y})

def test_source_normalization_distinguishes_scaled_vs_genuine_hourly_shapes():
    a=10+np.cos(np.arange(8760)*2*np.pi/24)
    b=a*.13
    c=10+np.sin(np.arange(8760)*2*np.pi/24)
    z=compare({0:trace(a,0),9:trace(c,9),18:trace(b,18)})
    assert z.loc[(z.rank_a==0)&(z.rank_b==18),"normalized_profiles_equal_within_1e_10"].iloc[0]
    assert not z.loc[(z.rank_a==0)&(z.rank_b==9),"normalized_profiles_equal_within_1e_10"].iloc[0]
    assert z.loc[(z.rank_a==0)&(z.rank_b==18),"max_normalized_demand_absolute_difference"].iloc[0]<1e-10

def test_rejects_missing_source_hour():
    a=np.ones(8760)
    t={i:trace(a,i) for i in (0,9,18)}
    t[9]=t[9].iloc[:-1]
    with pytest.raises(ValueError,match="8760-hour"):
        compare(t)
