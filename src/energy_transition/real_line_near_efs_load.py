"""Choose an actual line in a load-bearing Western component for a tiny AC-line-constrained pilot.

No line reactance or rating is fabricated. This prepares real physical inputs;
a selected pair is a topology sample, not a full Western electricity model.
"""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
import pypsa


def inspect(network:Path, out:Path):
 n=pypsa.Network(str(network))
 candidate=n.lines.copy()
 for col in ("x","s_nom"):
  if col not in candidate:raise ValueError(f"Real line missing {col}")
 candidate["x"]=pd.to_numeric(candidate.x,errors="coerce")
 candidate["s_nom"]=pd.to_numeric(candidate.s_nom,errors="coerce")
 candidate=candidate.loc[np.isfinite(candidate.x)&(candidate.x>0)&np.isfinite(candidate.s_nom)&(candidate.s_nom>0)]
 with_load=set(n.loads.bus)
 candidate=candidate.loc[candidate.bus0.isin(with_load)|candidate.bus1.isin(with_load)]
 if candidate.empty: raise ValueError("No positive-reactance, rated actual line adjacent to a load bus")
 candidate=candidate.sort_values("s_nom").head(5)
 lines=[]
 for line,r in candidate.iterrows():
  lines.append({"line_id":str(line),"bus0":str(r.bus0),"bus1":str(r.bus1),"x_pu_input":float(r.x),
                "s_nom_mva_input":float(r.s_nom),
                "load_on_bus0":str(r.bus0) in with_load,"load_on_bus1":str(r.bus1) in with_load})
 result={"eligible_real_line_count_near_load":int(len(n.lines.loc[n.lines.bus0.isin(with_load)|n.lines.bus1.isin(with_load)])),
         "selected_lines":lines,"source":"actual pinned PyPSA-USA built NetCDF",
         "synthetic_line_values":False,"constrained_dispatch_solved":False}
 out.write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps(result,indent=2))
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--network",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args();inspect(a.network,a.out)
