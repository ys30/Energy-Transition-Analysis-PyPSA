import pandas as pd
from energy_transition.interchange_calibration_gate import evaluate

def test_annual_and_monthly_ba_interchange_gate():
    summary=pd.DataFrame([
        {"respondent":"BPAT","complete_triple_share":.9999,"official_balance_mae_share_of_load":.61},
        {"respondent":"CISO","complete_triple_share":.964,"official_balance_mae_share_of_load":.033},
    ])
    monthly=pd.DataFrame([
        {"respondent":ba,"month":f"2024-{m:02d}","coverage":(0.90 if ba=="CISO" and m==1 else 1.0),
         "residual_share_of_demand":(.60 if ba=="BPAT" else .02)}
        for ba in ("BPAT","CISO") for m in range(1,13)
    ])
    decisions={d["ba_code"]:d for d in evaluate(summary,monthly)}
    assert decisions["BPAT"]["months_over_10pct_residual"]==12
    assert decisions["CISO"]["months_below_99pct_coverage"]==1
    assert not decisions["BPAT"]["interchange_calibration_eligible"]
    assert not decisions["CISO"]["interchange_calibration_eligible"]


def test_interchange_gate_rejects_monthly_review_and_extreme_tail():
    summary=pd.DataFrame([{
        "respondent":"CISO","complete_triple_share":1.0,
        "official_balance_mae_share_of_load":.001,
        "annual_max_residual_share_of_load":1.0,
    }])
    monthly=pd.DataFrame([{
        "respondent":"CISO","month":f"2024-{month:02d}",
        "coverage":1.0,"residual_share_of_demand":0.0,
        "quality_flag":"review_required" if month==1 else "screening_only_not_verified",
    } for month in range(1,13)])
    assert not evaluate(summary,monthly)[0]["interchange_calibration_eligible"]
    summary.loc[0,"annual_max_residual_share_of_load"]=0.01
    assert not evaluate(summary,monthly)[0]["interchange_calibration_eligible"]
    monthly["quality_flag"]="screening_only_not_verified"
    assert evaluate(summary,monthly)[0]["interchange_calibration_eligible"]


def test_interchange_gate_rejects_nonfinite_monthly_indicators():
    summary=pd.DataFrame([{
        "respondent":"CISO","complete_triple_share":1.0,
        "official_balance_mae_share_of_load":.01,
    }])
    monthly=pd.DataFrame([{
        "respondent":"CISO","month":f"2024-{month:02d}",
        "coverage":1.0,"residual_share_of_demand":0.0,
    } for month in range(1,13)])
    monthly.loc[0,"residual_share_of_demand"]=float("nan")
    assert not evaluate(summary,monthly)[0]["interchange_calibration_eligible"]
