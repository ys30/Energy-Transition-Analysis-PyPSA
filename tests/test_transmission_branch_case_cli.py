import hashlib
import json
import subprocess
import sys
import pandas as pd


def test_transmission_cli_records_input_hash(tmp_path):
    raw=tmp_path/"branches.csv"
    report=tmp_path/"audit.json"
    pd.DataFrame([{
        "from_ba":"CISO","to_ba":"BPAT","capacity_mw":100.0,
        "reactance_pu":0.12,"reactance_ohm":6.0,
        "resistance_ohm":0.4,"nominal_kv":230.0,
        "source_url":"https://example.org/synthetic-only",
        "source_year":2034,"evidence_status":"independently_verified"
    }]).to_csv(raw,index=False)
    subprocess.run([sys.executable,"-m","energy_transition.transmission_branch_case_audit",
                    "--csv",str(raw),"--case-year","2034","--kind","planning",
                    "--report",str(report)],check=True,capture_output=True,text=True)
    record=json.loads(report.read_text())
    assert record["input_sha256"]==hashlib.sha256(raw.read_bytes()).hexdigest()
    assert record["input_filename"]=="branches.csv"
    assert not record["ready_for_pypsa_physical_calibration"]
