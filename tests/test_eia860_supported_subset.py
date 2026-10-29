import pandas as pd
import pytest
from energy_transition.eia860_supported_subset import subset

def test_eia860_storage_excluded_and_audited_not_counted_as_generator():
    frame=pd.DataFrame({"ba_code":["CISO","CISO","BPAT","OTHER"],"fuel":["NG","MWH","WAT","NG"],
                        "capacity_mw":[100.,12.,100.,10000.]})
    known,unknown,report=subset(frame,["CISO","BPAT"])
    assert set(known.fuel)=={"NG","WAT"}
    assert unknown.fuel.tolist()==["MWH"]
    assert report["source_total_mw"]==212
    assert report["model_excluded_mw"]==12
    assert report["model_supported_fraction"]==200/212

def test_eia860_subset_rejects_excess_unmodeled_share():
    df=pd.DataFrame({"ba_code":["CISO","CISO"],"fuel":["NG","MWH"],"capacity_mw":[1.,10.]})
    with pytest.raises(ValueError,match="Insufficient"):
        subset(df,["CISO"])
