"""Cross-year verification of the 6-bus real-line / illustrative-generation pilot.

Never interpret the 24-hour EFS ordinal sample as a UTC-aligned full-year solve.
"""
import argparse,csv,json,math
from pathlib import Path

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--input-dir",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args()
 rows=[]
 for year in (2030,2040,2050):
  path=a.input_dir/f"real-six-bus-constrained-{year}-24h.json"
  r=json.loads(path.read_text())
  assert int(r["planning_year"])==year
  assert r["solver_status"]=="ok" and r["solver_condition"]=="optimal"
  assert r["real_lines"]==5 and r["buses"]==6
  assert int(r["binding_line_count"])>=1 and r["thermal_binding_verified"]
  assert r["max_line_thermal_utilization"]<=1.000001
  assert abs(r["actual_efs_mwh"]-r["dispatched_mwh"])<0.01
  assert r["generation_illustrative"] and not r["full_western_optimized"]
  assert r["timezone_aligned"] is False and int(r["hours"])==24
  assert r["actual_efs_mwh"]>0 and math.isfinite(float(r["actual_efs_mwh"]))
  assert math.isfinite(float(r["illustrative_cost_usd"]))
  rows.append({"year":year,"demand_mwh":r["actual_efs_mwh"],
    "illustrative_objective_usd":r["illustrative_cost_usd"],
    "illustrative_objective_per_mwh":r["illustrative_cost_usd"]/r["actual_efs_mwh"],
    "binding_lines":r["binding_line_count"],
    "max_line_utilization":r["max_line_thermal_utilization"],
    "status":r["solver_condition"]})
 if not all(b["demand_mwh"]>a["demand_mwh"] for a,b in zip(rows,rows[1:])):
  raise ValueError("Cross-year EFS demand did not increase; inspect upstream")
 a.out.parent.mkdir(parents=True,exist_ok=True)
 with a.out.open("w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 print(json.dumps({"verified_years":[r["year"] for r in rows],
  "comparison_csv":str(a.out),"source":"EFS-LAF demand and original AC line data",
  "limitations":"24h ordinal local-hour; illustrative generators/costs; not full Western OPF"},
  indent=2))
if __name__=="__main__": main()
