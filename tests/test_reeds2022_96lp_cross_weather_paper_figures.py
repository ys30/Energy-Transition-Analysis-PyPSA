import numpy as np
import pandas as pd
import pytest
from energy_transition.reeds2022_96lp_cross_weather_paper_figures import validate,STATES,YEARS,REEDS_COLUMN,EIA_COLUMN

def frozen_fixture():
    az0=[11.067844,12.016612,10.955400,12.821096]
    az1=[10.726983,11.421001,9.868276,12.842341]
    rows=[]
    for st in STATES:
        for i,year in enumerate(YEARS):
            a,b=(az0[i],az1[i]) if st=="AZ" else (5.5,6.5)
            rows.append({"state":st,"weather_year":year,REEDS_COLUMN:a,EIA_COLUMN:b,
                         "spatial_weight_10usd_screen_flips":(a>=10)!=(b>=10)})
    return pd.DataFrame(rows)

def test_exact_96lp_16_pair_az2012_screen_gate():
    df=frozen_fixture()
    s,a,b,flips=validate(df.sample(frac=1,random_state=5))
    assert len(a)==16 and flips.sum()==1
    assert s.loc[("AZ",2012),EIA_COLUMN]==pytest.approx(9.868276)

def test_duplicate_year_state_fail():
    df=frozen_fixture()
    df.loc[1,"weather_year"]=df.loc[0,"weather_year"]
    with pytest.raises(ValueError,match="unique"):
        validate(df)

def test_changed_az_original_anchor_rejected():
    df=frozen_fixture()
    df.loc[2,EIA_COLUMN]=11.2
    df.loc[2,"spatial_weight_10usd_screen_flips"]=False
    with pytest.raises(ValueError,match="only AZ 2012"):
        validate(df)
