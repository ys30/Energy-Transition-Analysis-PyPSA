import pandas as pd
import pytest
from energy_transition.observed_renewable_storage import prepare_injections
from energy_transition.seasonal_storage_sensitivity import SEASON_WEEKS

def test_signed_injections_preserved_by_hour_and_ba():
    rows=[]
    for season,start in SEASON_WEEKS.items():
        for period in pd.date_range(pd.Timestamp(start),periods=168,freq="h"):
            for ba in ("CISO","BPAT"):
                for fuel in ("SUN","WND"):
                    rows.append({"season":season,"period":period,"respondent":ba,
                                 "fueltype":fuel,"reported_signed_net_mwh":-2 if fuel=="SUN" else 9})
    frame=pd.DataFrame(rows)
    result=prepare_injections(frame)
    assert set(result)==set(SEASON_WEEKS)
    assert result["summer"].iloc[0]==14
    with pytest.raises(ValueError,match="Missing or unexpected"):
        prepare_injections(frame.iloc[1:])

def test_duplicate_renewable_hour_rejected():
    frame=pd.DataFrame([{"season":"winter","period":"2024-01-08T00:00:00Z",
      "respondent":"CISO","fueltype":"SUN","reported_signed_net_mwh":-1}])
    with pytest.raises(ValueError,match="Duplicate"):
        prepare_injections(pd.concat([frame,frame]))
