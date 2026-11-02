"""Compare verified 24h and 168h two-load pilot windows without annualizing."""
import argparse,json,math,csv
from pathlib import Path

def compare(folder):
 rows=[]
 for year in (2030,2040,2050):
  metrics={}
  for hours in (24,168):
   d=json.loads((folder/f"two-load-ac-path-{year}-{hours}h.json").read_text())
   if d.get("planning_year")!=year or d.get("snapshot_hours")!=hours:
    raise ValueError("Wrong year/window")
   if d.get("solver_status")!="ok" or d.get("solver_condition")!="optimal":
    raise ValueError("Nonoptimal solve")
   if not(d.get("generation_illustrative") is True and d.get("timezone_aligned") is False
          and d.get("full_western_optimized") is False):
    raise ValueError("Provenance or calibration claims changed")
   load=float(d["efs_load_mwh_total"]);gen=float(d["dispatch_mwh_total"])
   objective=float(d["objective_illustrative_usd"])
   if not all(map(math.isfinite,(load,gen,objective))) or load<=0 or abs(load-gen)>max(0.01,load*1e-8):
    raise ValueError("Invalid dispatch balance")
   if float(d["maximum_nodal_residual_mw"])>1e-3:
    raise ValueError("Nodal balance failed")
   if set(d["peak_abs_line_flow_mw"])!={"97145","97156","97159"}:
    raise ValueError("Source-line scope changed")
   if not all(0<=float(v)<=1.000001 for v in d["max_line_utilization"].values()):
    raise ValueError("Thermal violation")
   metrics[hours]={"load":load,"gen":gen,"objective":objective,
                    "unit_objective":objective/load,
                    "binding":d["binding_line_ids"]}
  if metrics[168]["load"]<=metrics[24]["load"]:
   raise ValueError("Extended window has no additional positive load")
  rows.append({"year":year,"load_24h_mwh":metrics[24]["load"],
    "load_168h_mwh":metrics[168]["load"],
    "mean_load_24h_mw":metrics[24]["load"]/24,
    "mean_load_168h_mw":metrics[168]["load"]/168,
    "illustrative_objective_per_mwh_24h":metrics[24]["unit_objective"],
    "illustrative_objective_per_mwh_168h":metrics[168]["unit_objective"],
    "binding_24h":",".join(metrics[24]["binding"]),
    "binding_168h":",".join(metrics[168]["binding"])})
 return rows

def main():
 p=argparse.ArgumentParser();p.add_argument("--input-dir",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True);a=p.parse_args()
 rows=compare(a.input_dir)
 a.out.parent.mkdir(parents=True,exist_ok=True)
 with a.out.open("w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 print(json.dumps({"verified_years":[r["year"] for r in rows],
  "comparison":rows,"annualized":False,"real_generation_calibrated":False},indent=2))

if __name__=="__main__":main()
