"""Inspect the model's actual edges and transformers at source sub_id 39703.

Documented Colstrip POI is 500 kV. An observed 345-kV source bus is
not an electrical crosswalk to the POI absent transformer/source evidence.
"""
import argparse,json
from pathlib import Path
import pypsa
import pandas as pd

def audit(network_path,out):
    n=pypsa.Network(str(network_path))
    buses=n.buses.loc[n.buses.sub_id.astype("string").str.replace(r"\\.0$","",regex=True).eq("39703")]
    target=set(map(str,buses.index))
    def incident(table):
        if table.empty or not {"bus0","bus1"}.issubset(table.columns):return []
        selected=table.loc[table.bus0.astype(str).isin(target)|table.bus1.astype(str).isin(target)]
        result=[]
        for i,row in selected.iterrows():
            result.append({"id":str(i),"bus0":str(row["bus0"]),"bus1":str(row["bus1"]),
              "bus0_kv":None if str(row["bus0"]) not in n.buses.index.astype(str) else str(n.buses.loc[str(row["bus0"]),"v_nom"]),
              "bus1_kv":None if str(row["bus1"]) not in n.buses.index.astype(str) else str(n.buses.loc[str(row["bus1"]),"v_nom"])})
        return result
    report={"source_sub_id":"39703","bus_ids":sorted(target),
       "bus_nominal_kv":{str(i):str(r["v_nom"]) for i,r in buses.iterrows()},
       "lines":incident(n.lines),"transformers":incident(n.transformers),"links":incident(n.links),
       "physical_colstrip_500kv_poi_supported_by_this_audit":False,
       "verified_generator_to_network_bus_links":0}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("--network",type=Path,required=True);a.add_argument("--out",type=Path,required=True)
    x=a.parse_args();audit(x.network,x.out)
