import pandas as pd
import pytest
from energy_transition.seasonal_storage_sensitivity import compare_seasons

def test_seasonal_comparison_keeps_weeks_separate(monkeypatch,tmp_path):
    starts={"winter":"2024-01-08T00:00:00Z","summer":"2024-07-08T00:00:00Z"}
    def fake_run(window,output):
        assert len(window)==168
        return pd.DataFrame({"duration_h":[2.,4.,6.,8.],
                             "operating_savings_usd":[1.,2.,3.,4.],
                             "discharge_mwh":[1.,2.,3.,4.],
                             "unserved_mwh":[0.,0.,0.,0.]})
    monkeypatch.setattr("energy_transition.seasonal_storage_sensitivity.run_sensitivity",fake_run)
    frames=[]
    for start in starts.values():
        ts=pd.date_range(start,periods=168,freq="h")
        frames.append(pd.DataFrame({"period":ts,"respondent":"CISO","value":100.}))
    result=compare_seasons(pd.concat(frames,ignore_index=True),tmp_path,weeks=starts)
    assert len(result)==8
    assert set(result.season)==set(starts)
    assert (tmp_path/"seasonal_storage_sensitivity.csv").is_file()
