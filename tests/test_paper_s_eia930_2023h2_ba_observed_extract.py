"""Synthetic raw CSV tests; real historical data verified separately by pinned MD5."""
import hashlib
import io
import zipfile
import pandas as pd
import pytest
from energy_transition import paper_s_eia930_2023h2_ba_observed_extract as target

def test_source_MW_and_distinct_adjusted_values(tmp_path,monkeypatch):
    cols={
        "Balancing Authority":["PNM","PNM","PNM"],
        "UTC Time at End of Hour":[
            "07/01/2023 12:00:00 AM","07/01/2023 1:00:00 AM",
            "07/01/2023 2:00:00 AM"],
        "Net Generation (MW) from Wind":[25.0,None,-1.0],
        "Net Generation (MW) from Wind (Imputed)":[None,33.0,None],
        "Net Generation (MW) from Wind (Adjusted)":[25.0,33.0,-1.0],
        "Net Generation (MW) from Solar":[0.0,0.0,12.0],
        "Net Generation (MW) from Solar (Imputed)":[None,None,None],
        "Net Generation (MW) from Solar (Adjusted)":[0.0,0.0,12.0],
    }
    p=tmp_path/"eia930-2023half2.zip"
    with zipfile.ZipFile(p,"w",compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("eia930-2023half2-balance.csv",pd.DataFrame(cols).to_csv(index=False))
    monkeypatch.setattr(target,"EXPECTED_MD5",hashlib.md5(p.read_bytes()).hexdigest())
    a,b=target.extract(p,
        start=pd.Timestamp("2023-07-01T00:00:00Z"),
        stop=pd.Timestamp("2023-07-01T03:00:00Z"))
    wind=a.loc[(a.ba_code=="PNM")&(a.fuel=="wind")].sort_values("utc_hour_end")
    assert len(a)==6 and len(b)==8
    assert wind.reported_mw.isna().sum()==1
    assert wind.imputed_mw.notna().sum()==1
    assert wind.adjusted_mw.tolist()==[25.0,33.0,-1.0]
    assert int(b.loc[(b.ba_code=="PNM")&(b.fuel=="wind"),"missing_source_hours"].iloc[0])==0
    assert int(b.loc[(b.ba_code=="PSCO")&(b.fuel=="solar"),"missing_source_hours"].iloc[0])==3

def test_mismatched_checksum_is_rejected(tmp_path):
    p=tmp_path/"eia930-2023half2.zip"
    p.write_bytes(b"not a valid publisher archive")
    with pytest.raises(ValueError,match="checksum"):
        target.extract(p)
