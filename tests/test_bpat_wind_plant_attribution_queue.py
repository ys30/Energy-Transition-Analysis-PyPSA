import pandas as pd
import pytest
from energy_transition.bpat_wind_plant_attribution_queue import review_queue


def test_review_queue_preserves_unknown_operational_attribution():
    plants=pd.DataFrame({"plant_id":["1","2","3"],"ba_code":["BPAT","CISO","BPAT"],
                         "net_generation_mwh":[20.0,400.0,90.0]})
    out=review_queue(plants)
    assert out.plant_id.tolist()==["3","1"]
    assert out.priority_rank.tolist()==[1,2]
    assert out.review_tier.tolist()==["first_5","first_5"]
    assert out.share_of_mapped_bpat_wind.sum()==pytest.approx(1.0)
    assert out.cumulative_share_of_mapped_bpat_wind.iloc[-1]==pytest.approx(1.0)
    assert out.net_generation_mwh.sum()==110.0
    assert not out.eia930_operational_ba_verified.any()
    assert out.eia930_plant_specific_generation_mwh.isna().all()
    assert out.status.eq("unresolved_operational_attribution").all()


def test_review_queue_rejects_no_bpat_plants():
    plants=pd.DataFrame({"plant_id":["2"],"ba_code":["CISO"],
                         "net_generation_mwh":[10.0]})
    with pytest.raises(ValueError,match="Missing or duplicate"):
        review_queue(plants)
