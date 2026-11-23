"""Synthetic diagnostics tests; no observation-accuracy claim."""
import pandas as pd
import pytest
from energy_transition.paper_s_eia930_160h_ba_diagnostics import (
    BAS,FUELS,COMMON_START,COMMON_END,source_panel,diagnostics
)

def fixture(tmp_path):
    times=pd.date_range(COMMON_START,COMMON_END,freq="h",tz="UTC")
    rows=[]
    for idx,ba in enumerate(BAS):
        for fuel in FUELS:
            for k,t in enumerate(times):
                raw=float((idx+1)*10+k%9)
                if ba=="PNM" and fuel=="solar" and k==0:raw=-2.0
                rows.append(dict(utc_hour_end=t.isoformat(),ba_code=ba,fuel=fuel,
                    reported_mw=raw,imputed_mw=None,adjusted_mw=raw))
    path=tmp_path/"synthetic.csv"
    pd.DataFrame(rows).to_csv(path,index=False)
    return path

def test_160h_common_panel_negative_values_preserved(tmp_path):
    p=fixture(tmp_path)
    d=source_panel(p,verify_hash=False)
    s,c=diagnostics(d)
    assert len(d)==1280 and len(s)==8 and len(c)==12
    assert s.negative_hours.sum()==1
    q=s.loc[(s.ba_code=="PNM")&(s.fuel=="solar")].iloc[0]
    assert q.clipping_raises_mean_mw>0
    assert (c.paired_hour_count==160).all()

def test_missing_hour_fails_closed(tmp_path):
    p=fixture(tmp_path)
    d=pd.read_csv(p).iloc[1:]
    d.to_csv(p,index=False)
    with pytest.raises(ValueError,match="Incomplete common"):
        source_panel(p,verify_hash=False)

def test_checksum_enforced(tmp_path):
    p=fixture(tmp_path)
    with pytest.raises(ValueError,match="SHA256 mismatch"):
        source_panel(p)
