import pandas as pd
from energy_transition.eia930_triple_missingness import summarize


def test_missingness_tracks_separate_and_joint_fields():
    h=pd.DataFrame({
       "respondent":["CISO"]*4,
       "period":pd.date_range("2024-11-02",periods=4,freq="h",tz="UTC"),
       "demand":[1.0,None,1.0,None],
       "generation":[1.0,1.0,None,None],
       "interchange":[0.0,0.0,0.0,None],
    })
    out=summarize(h)
    counts=dict(zip(out.missing_fields,out.hour_count))
    assert counts=={"complete":1,"demand":1,"generation":1,"demand+generation+interchange":1}
    assert out.month_utc.eq("2024-11").all()
