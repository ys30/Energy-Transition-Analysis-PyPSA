import pandas as pd
from energy_transition.eia930_source_alignment_gate import assess

def test_source_alignment_gate_checks_zero_hour_without_claiming_energy_balance():
    data=pd.DataFrame([
        {"ba_code":"BPAT","stage":"reported","series":"demand","api_shift_hours":-1,"same_hour_pairs":100,"mae_mw":180},
        {"ba_code":"BPAT","stage":"reported","series":"demand","api_shift_hours":0,"same_hour_pairs":100,"mae_mw":0.02},
        {"ba_code":"BPAT","stage":"reported","series":"demand","api_shift_hours":1,"same_hour_pairs":100,"mae_mw":180}])
    row=assess(data)[0]
    assert row["best_shift_hours"]==0
    assert row["zero_shift_within_tolerance"]
    assert "does not validate physical energy balance" in row["warning"]
