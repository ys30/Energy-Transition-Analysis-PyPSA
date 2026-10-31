from energy_transition.interchange_calibration_blockers import summarize_gate


def test_bpat_balance_and_ciso_coverage_blockers_are_distinct():
    gate={"decisions":[
        {"ba_code":"BPAT","coverage_share":.9999,"months_below_99pct_coverage":0,
         "official_mae_share_of_load":.61,"months_over_10pct_residual":12,
         "interchange_calibration_eligible":False},
        {"ba_code":"CISO","coverage_share":.964,"months_below_99pct_coverage":5,
         "official_mae_share_of_load":.033,"months_over_10pct_residual":0,
         "interchange_calibration_eligible":False}]}
    result=summarize_gate(gate)
    by_ba={x["ba_code"]:x for x in result["ba_results"]}
    assert [x["code"] for x in by_ba["BPAT"]["blockers"]]==["official_balance_residual"]
    assert [x["code"] for x in by_ba["CISO"]["blockers"]]==["temporal_coverage"]
    assert not by_ba["BPAT"]["physical_calibration_verified"]
