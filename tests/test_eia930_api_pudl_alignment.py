import pandas as pd
from energy_transition.eia930_api_pudl_alignment import compare

def test_alignment_detects_hour_offset_without_mixing_samples():
    t=pd.to_datetime(["2024-01-01T00:00:00Z","2024-01-01T01:00:00Z"])
    api=pd.DataFrame({"respondent":["BPAT"]*2,"period":t,
       "demand":[100.,200.],"generation":[90.,180.],"interchange":[-10.,-20.]})
    pudl=pd.DataFrame({"balancing_authority_code_eia":["BPAT"]*2,
       "datetime_utc":t+pd.Timedelta(hours=1)})
    for stage in ("reported","adjusted"):
        for field,values in (("demand",[100.,200.]),("net_generation",[90.,180.]),("interchange",[-10.,-20.])):
            pudl[f"{field}_{stage}_mwh"]=values
    result=compare(api,pudl)
    aligned=result[(result.stage=="reported")&(result.series=="demand")&(result.api_shift_hours==1)].iloc[0]
    assert aligned.same_hour_pairs==2
    assert aligned.mae_mw==0
    zero=result[(result.stage=="reported")&(result.series=="demand")&(result.api_shift_hours==0)].iloc[0]
    assert zero.same_hour_pairs==1
    assert zero.mae_mw==100
