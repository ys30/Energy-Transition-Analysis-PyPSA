"""Source-free annual 2023 EIA930 BA coverage safeguards."""
import pandas as pd
import pytest
from energy_transition.paper_s_eia930_2023_full_year_BA_coverage import (
    EXPECTED_HOURS, START, HALF, END, annual_coverage, BAS, TECHS
)

def test_2023_annual_hour_boundary():
    assert EXPECTED_HOURS==8760
    assert (HALF-START)/pd.Timedelta(hours=1)==4344
    assert (END-HALF)/pd.Timedelta(hours=1)==4416

def test_absent_utc_hour_is_not_missing_reported_MW():
    records=[]
    for ba in BAS:
        for fuel in TECHS:
            records.append(dict(ba_code=ba,fuel=fuel,utc_hour_end=START,
                                reported_mw=3,imputed_mw=float("nan"),
                                adjusted_mw=3,source_half="half1"))
            records.append(dict(ba_code=ba,fuel=fuel,
                                utc_hour_end=START+pd.Timedelta(hours=1),
                                reported_mw=float("nan"),imputed_mw=5,
                                adjusted_mw=5,source_half="half1"))
            records.append(dict(ba_code=ba,fuel=fuel,utc_hour_end=HALF,
                                reported_mw=-1,imputed_mw=float("nan"),
                                adjusted_mw=-1,source_half="half2"))
    df=pd.DataFrame(records)
    s,m,g=annual_coverage(df)
    assert len(s)==8 and len(m)==96
    assert s.source_timestamp_count.eq(3).all()
    assert s.missing_source_hour_ending_count.eq(EXPECTED_HOURS-3).all()
    assert s.null_reported_MW_on_present_hour.eq(1).all()
    assert s.negative_reported_MW_count.eq(1).all()
    assert len(g)==8*(EXPECTED_HOURS-3)
    assert not s.BA_equals_state.any()
    with pytest.raises(ValueError,match="overlap"):
        annual_coverage(pd.concat([df,df.iloc[:1]],ignore_index=True))
