import pandas as pd
import numpy as np
import pytest
from energy_transition.reeds2022_county_potential_concentration import audit

def test_equal_potential_counties_have_effective_count_two(tmp_path):
    p=tmp_path/"fake.csv"
    pd.DataFrame({"class|region":["1|p04001","2|p04001","1|p04003","1|p08001"],
                  "MW":["10","10","20","10"]}).to_csv(p,index=False)
    with pytest.raises(ValueError,match="Missing original county classes"):
        audit(p,"wind",verify_md5=False)

def test_bad_source_capacity_rejected(tmp_path):
    p=tmp_path/"bad.csv"
    pd.DataFrame({"class|region":["1|p04001"],"MW":["-1"]}).to_csv(p,index=False)
    with pytest.raises(ValueError,match="Invalid source potential"):
        audit(p,"pv",verify_md5=False)

def test_reject_duplicate_county_resource_keys(tmp_path):
    p=tmp_path/"duplicate.csv"
    pd.DataFrame({"class|region":["1|p04001","1|p04001"],"MW":["1","1"]}).to_csv(p,index=False)
    with pytest.raises(ValueError,match="Duplicate"):
        audit(p,"wind",verify_md5=False)
