"""Synthetic two-bus AC Line optimization smoke test.

Synthetic topology and ratings are *not* CISO/BPAT evidence.
"""
import pypsa
import pandas as pd
from energy_transition.pypsa_line_evidence_adapter import add_screened_ba_lines


def run_synthetic_line_smoke():
    network=pypsa.Network()
    network.set_snapshots(pd.date_range("2024-01-01",periods=1,freq="h"))
    for ba in ("CISO","BPAT"):
        network.add("Bus",ba,v_nom=230.)
    # This is an explicitly synthetic engineering fixture. The mock evidence
    # status only permits testing the adapter API, not real-world calibration.
    fixture=pd.DataFrame([{
        "from_ba":"CISO","to_ba":"BPAT","capacity_mw":50.,
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
    if not 49.9<=flow<=50.1 or backup<49.9:
        raise AssertionError(f"Line constraint not binding: flow={flow}, backup={backup}")
    return {"synthetic_fixture":True,"line_capacity_mw":50.,
            "line_flow_mw":flow,"backup_mw":backup,"status":status}


if __name__=="__main__":
    import json
    print(json.dumps(run_synthetic_line_smoke(),indent=2))
