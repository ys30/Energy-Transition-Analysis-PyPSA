"""Fail-closed acceptance of the three-year two-load illustrative AC-path results."""
import argparse
import json
import math
from pathlib import Path

YEARS=(2030,2040,2050)
BUSES={"2040602","2040645"}
LINES={"97145","97156","97159"}


def validate(folder, hours=24):
    if hours not in (24,168):
        raise ValueError('Unsupported scenario window')
    rows=[]
    for year in YEARS:
        d=json.loads((folder/f"two-load-ac-path-{year}-{hours}h.json").read_text())
        if d.get("planning_year")!=year or d.get("snapshot_hours")!=hours:
            raise ValueError(f"{year}: time scope mismatch")
        if set(d.get("actual_efs_load_buses",[]))!=BUSES or set(d.get("lines",[]))!=LINES:
            raise ValueError(f"{year}: source network scope mismatch")
        if d.get("solver_status")!="ok" or d.get("solver_condition")!="optimal":
            raise ValueError(f"{year}: solver not optimal")
        if not (d.get("source_real_ac_line_parameters") is True and
                d.get("source_real_efs_loads") is True and
                d.get("generation_illustrative") is True and
                d.get("timezone_aligned") is False and
                d.get("full_western_optimized") is False and
                d.get("network_boundary_injections_verified") is False):
            raise ValueError(f"{year}: provenance/readiness flags changed")
        demand=float(d["efs_load_mwh_total"])
        dispatch=float(d["dispatch_mwh_total"])
        residual=float(d["maximum_nodal_residual_mw"])
        if not all(math.isfinite(x) for x in [demand,dispatch,residual,float(d["objective_illustrative_usd"])]):
            raise ValueError(f"{year}: non-finite metric")
        if demand<=0 or abs(demand-dispatch)>max(0.01,demand*1e-8) or residual>1e-3 or residual<0:
            raise ValueError(f"{year}: load balance failed")
        loads=d["efs_load_mwh_by_bus"]
        if set(loads)!=BUSES or any(float(x)<=0 for x in loads.values()) or abs(sum(loads.values())-demand)>0.01:
            raise ValueError(f"{year}: incomplete dual-load energy")
        flow=d["peak_abs_line_flow_mw"]
        util=d["max_line_utilization"]
        if set(flow)!=LINES or set(util)!=LINES:
            raise ValueError(f"{year}: line result missing")
        if any(not math.isfinite(float(x)) or float(x)<=0 for x in flow.values()):
            raise ValueError(f"{year}: missing positive path flow")
        if any(not math.isfinite(float(x)) or not 0<float(x)<=1.000001 for x in util.values()):
            raise ValueError(f"{year}: invalid thermal utilization")
        rows.append({"year":year,"window_load_mwh":demand,"max_nodal_residual_mw":residual,
                     "binding_line_ids":d["binding_line_ids"],
                     "illustrative_objective_usd":float(d["objective_illustrative_usd"])})
    if not all(b["window_load_mwh"]>a["window_load_mwh"] for a,b in zip(rows,rows[1:])):
        raise ValueError("Cross-year sample loads not increasing")
    return {"acceptance_passed":True,"snapshot_hours":hours,"years":list(YEARS),"results":rows,
            "actual_generation_calibrated":False,"annual_western_opf_verified":False}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input-dir",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--hours",type=int,choices=(24,168),default=24)
    a=p.parse_args()
    result=validate(a.input_dir,a.hours)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
