import numpy as np
import pandas as pd
import pytest
from energy_transition.efs_source_normalized_shapes import audit_shapes

def sample():
    rows=[]
    for year in (2030,2040,2050):
        for state,zone,load in (("AZ","p28",np.array([2.,4.,3.,5.])),
                                ("AZ","p29",np.array([.2,.4,.3,.5])),
                                ("WY","p21",np.array([3.,3.,1.,1.])),
                                ("AZ","p00",np.zeros(4))):
            for h,v in enumerate(load,1):
                rows.append({"year":year,"state":state,"reeds_zone":zone,
                             "local_hour_id":h,"allocated_mw":v})
    return pd.DataFrame(rows)

def test_group_scaled_shapes_and_zero_zone_separately():
    z,s=audit_shapes(sample(),hours=4,expected_zones=4)
    assert s.unique_positive_normalized_shapes.tolist()==[2,2,2]
    assert s.zero_demand_zones.tolist()==[1,1,1]
    assert s.positive_zones_in_duplicated_shape_groups.tolist()==[2,2,2]
    year=z[z.planning_year==2030].set_index("reeds_zone")
    assert year.loc["p28","normalized_shape_group"]==year.loc["p29","normalized_shape_group"]
    assert year.loc["p21","normalized_shape_group"]!=year.loc["p28","normalized_shape_group"]
    assert year.loc["p00","normalized_shape_group"]=="zero_source"

def test_duplicate_hour_is_rejected():
    a=sample()
    with pytest.raises(ValueError,match="Duplicate"):
        audit_shapes(pd.concat([a,a.iloc[[0]]]),hours=4,expected_zones=4)
