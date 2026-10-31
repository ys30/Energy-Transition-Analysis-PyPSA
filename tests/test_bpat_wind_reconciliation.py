import pandas as pd
import pytest
from energy_transition.bpat_wind_reconciliation import reconcile


def fixtures():
    pm=pd.DataFrame({"plant_id":["101","102","103"],"report_year":[2024]*3,
                     "fuel":["wind"]*3,"net_generation_mwh":[100.0,20.0,30.0]})
    cw=pd.DataFrame({"plant_id":["101","102"],"ba_code":["BPAT","CISO"],
                     "mapping_year":[2024]*2})
    hours=pd.date_range("2024-01-01","2025-01-01",freq="h",inclusive="left",tz="UTC")
    h=pd.DataFrame({"period":hours,"respondent":"BPAT","fueltype":"WND","value":1.0})
    return pm,cw,h


def test_reconciliation_preserves_unmatched_and_other_ba_as_diagnostics():
    pm,cw,h=fixtures()
    result,plants=reconcile(pm,cw,h)
    assert result["eia923_bpat_wind_mwh"]==100.0
    assert result["eia923_unmatched_wind_mwh"]==30.0
    assert "NOT BPAT" in result["eia923_unmatched_scope"]
    assert "Other BAs" in result["eia923_other_ba_scope"]
    assert result["eia923_to_eia930_bpat_wind_ratio"]==pytest.approx(100.0/8784.0)
    assert result["eia923_other_ba_wind_mwh"]==20.0
    assert result["eia923_other_ba_wind_breakdown_mwh"]=={"CISO":20.0}
    assert sum(result["eia923_other_ba_wind_breakdown_mwh"].values())==result["eia923_other_ba_wind_mwh"]
    assert result["eia930_observed_hours"]==8784
    assert result["signed_difference_eia923_minus_eia930_mwh"]==100.0-8784.0
    assert len(plants)==3


def test_missing_hour_blocks_annual_comparison():
    pm,cw,h=fixtures()
    h=h.drop(index=h.index[42])
    with pytest.raises(ValueError,match="Incomplete BPAT WND coverage"):
        reconcile(pm,cw,h)


def test_crosswalk_vintage_mismatch_rejected():
    pm,cw,h=fixtures()
    cw.loc[0,"mapping_year"]=2023
    with pytest.raises(ValueError,match="vintages"):
        reconcile(pm,cw,h)


def test_duplicate_hour_rejected():
    pm,cw,h=fixtures()
    h=pd.concat([h,h.iloc[[0]]],ignore_index=True)
    with pytest.raises(ValueError,match="Duplicate"):
        reconcile(pm,cw,h)


def test_total_generation_ng_cannot_be_misrepresented_as_wind():
    pm,cw,h=fixtures()
    h=h.rename(columns={"fueltype":"type"})
    h["type"]="NG"
    with pytest.raises(ValueError,match="hourly missing columns"):
        reconcile(pm,cw,h)


def test_decimal_suffix_plant_id_matches_inventory_crosswalk():
    pm,cw,h=fixtures()
    pm.loc[0,"plant_id"]="101.0"
    result,_=reconcile(pm,cw,h)
    assert result["eia923_bpat_wind_mwh"]==100.0
    assert result["eia923_unmatched_plant_count"]==1


@pytest.mark.parametrize("column,wrong,expected", [
    ("respondent", "CISO", "non-BPAT"),
    ("fueltype", "NG", "non-WND"),
])
def test_mixed_official_hourly_source_rejected(column,wrong,expected):
    pm,cw,h=fixtures()
    h.loc[0,column]=wrong
    with pytest.raises(ValueError,match=expected):
        reconcile(pm,cw,h)


def test_bpat_plant_contributions_sum_to_verified_ba_total():
    pm,cw,h=fixtures()
    result,_=reconcile(pm,cw,h)
    assert result["eia923_bpat_wind_plant_contributions_mwh"]=={"101":100.0}
    assert sum(result["eia923_bpat_wind_plant_contributions_mwh"].values())==pytest.approx(
        result["eia923_bpat_wind_mwh"]
    )


def test_multiple_monthly_records_aggregate_to_one_bpat_plant():
    pm,cw,h=fixtures()
    pm=pd.concat([pm,pd.DataFrame([{
        "plant_id":"101","report_year":2024,"fuel":"wind","net_generation_mwh":25.0
    }])],ignore_index=True)
    result,_=reconcile(pm,cw,h)
    assert result["eia923_bpat_wind_plant_contributions_mwh"]["101"]==125.0
    assert result["eia923_bpat_plant_count"]==1


def test_out_of_year_hourly_observation_is_rejected():
    pm,cw,h=fixtures()
    extra=h.iloc[[0]].copy()
    extra["period"]=pd.Timestamp("2025-01-01T00:00:00Z")
    h=pd.concat([h,extra],ignore_index=True)
    with pytest.raises(ValueError,match="outside target year"):
        reconcile(pm,cw,h)
