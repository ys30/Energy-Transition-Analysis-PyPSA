"""Synthetic two-bus AC Line optimization smoke test.

Synthetic topology and ratings are *not* CISO/BPAT evidence.
"""
import pypsa
import pandas as pd
from energy_transition.pypsa_line_evidence_adapter import add_screened_ba_lines


def run_synthetic_line_smoke(capacity_mw=50.):
    network=pypsa.Network()
    network.set_snapshots(pd.date_range("2024-01-01",periods=1,freq="h"))
    for ba in ("CISO","BPAT"):
        network.add("Bus",ba,v_nom=230.)
    # This is an explicitly synthetic engineering fixture. The mock evidence
    # status only permits testing the adapter API, not real-world calibration.
    fixture=pd.DataFrame([{
        "from_ba":"CISO","to_ba":"BPAT","capacity_mw":float(capacity_mw),
        "reactance_pu":0.1,"source_url":"https://example.org/synthetic-test-fixture",
        "source_year":2024,"reactance_ohm":8.,"resistance_ohm":0.1,
        "nominal_kv":230.,"evidence_status":"independently_verified"
    }])
    add_screened_ba_lines(network,fixture)
    network.add("Generator","supply",bus="CISO",p_nom=200,marginal_cost=1.)
    network.add("Generator","local_backup",bus="BPAT",p_nom=200,marginal_cost=100.)
    network.add("Load","demand",bus="BPAT",p_set=100.)
    status,condition=network.optimize(solver_name="highs")
    if status!="ok" or condition!="optimal":
        raise RuntimeError(f"PyPSA failed: {status}/{condition}")
    flow=float(network.lines_t.p0.iloc[0,0])
    backup=float(network.generators_t.p.loc[network.snapshots[0],"local_backup"])
    expected_flow=min(float(capacity_mw),100.)
    if abs(flow-expected_flow)>0.11 or abs(backup-(100.-expected_flow))>0.11:
        raise AssertionError(f"Line-capacity response failed: rating={capacity_mw}, flow={flow}, backup={backup}")
    total_cost=float(network.objective)
    expected_cost=expected_flow*1.+(100.-expected_flow)*100.
    if abs(total_cost-expected_cost)>1.:
        raise AssertionError(f"Cost response failed: expected={expected_cost}, actual={total_cost}")
    return {"synthetic_fixture":True,"line_capacity_mw":float(capacity_mw),
            "line_flow_mw":flow,"backup_mw":backup,"objective_cost":total_cost,"status":status}


if __name__=="__main__":
    import json
    outcomes=[run_synthetic_line_smoke(capacity) for capacity in (25.,50.,125.)]
    if not (outcomes[0]["objective_cost"]>outcomes[1]["objective_cost"]>outcomes[2]["objective_cost"]):
        raise AssertionError("Increasing transmission rating did not reduce synthetic dispatch cost")
    print(json.dumps({"synthetic_capacity_sweep":outcomes},indent=2))
