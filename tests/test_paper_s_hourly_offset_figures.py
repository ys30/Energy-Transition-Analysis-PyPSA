import pandas as pd
import pytest
from energy_transition.paper_s_hourly_offset_figures import audit

def test_incomplete_source_hour_population_rejected():
    data=pd.DataFrame({"source_shape_group":[1],"solution":["baseline"],
       "local_hour_id":[1],"storage_discharge_to_load_mwh":[2.]})
    with pytest.raises(ValueError,match="52,560"):
        audit(data,pd.DataFrame())

def test_missing_source_fields_rejected_even_with_expected_rows():
    x=pd.DataFrame({"source_shape_group":[1]*52560,"solution":["baseline"]*52560,
         "local_hour_id":[1]*52560})
    with pytest.raises(ValueError,match="physical dispatch"):
        audit(x,pd.DataFrame())
