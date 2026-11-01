"""Screen actual PyPSA Western lines without assuming tiny ratings are usable.

Network units and source ratings must be reviewed before physical claims.
"""
import argparse,json
from pathlib import Path
import numpy as np,pandas as pd,pypsa

def audit(path):
 n=pypsa.Network(str(path)); l=n.lines.copy()
 l["x"]=pd.to_numeric(l.x,errors="coerce")
 l["s_nom"]=pd.to_numeric(l.s_nom,errors="coerce")
 nearby=l.loc[l.bus0.isin(n.loads.bus)|l.bus1.isin(n.loads.bus)].copy()
 valid=nearby.loc[np.isfinite(nearby.x)&(nearby.x>0)&np.isfinite(nearby.s_nom)&(nearby.s_nom>0)].copy()
 thresholds=[0.01,1,10,100,500]
 candidates=valid.loc[valid.s_nom>=100].sort_values("s_nom",ascending=False).head(10)
 return {"lines_adjacent_to_loaded_buses":len(nearby),
         "positive_reactance_rating_lines":len(valid),
         "line_capacity_mva_at_least":{str(t):int((valid.s_nom>=t).sum()) for t in thresholds},
         "tiny_at_or_below_0_01_mva":int((valid.s_nom<=0.01+1e-10).sum()),
         "candidate_real_lines":[{"line_id":str(i),"bus0":str(r.bus0),"bus1":str(r.bus1),
           "x":float(r.x),"s_nom_mva":float(r.s_nom)} for i,r in candidates.iterrows()],
         "real_efs_load_used_in_optimization":False,
         "physical_units_independently_verified":False,
         "source_rating_adequacy_verified":False,
         "constrained_optimization_complete":False}

if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--network",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args(); result=audit(a.network);a.out.write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result,indent=2))
