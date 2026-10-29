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
