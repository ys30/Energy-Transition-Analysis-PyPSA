"""Search an actual PyPSA network for explicit Colstrip bus identity, not proximity.

A textual name hit is a candidate; it never independently verifies the
Clearwater generation tie or the EIA generator-to-network-bus mapping.
"""
import argparse,json
from pathlib import Path

def inspect(network_path:Path,out:Path):
    import pypsa
    n=pypsa.Network(str(network_path))
    b=n.buses.copy()
    textual=[c for c in b.columns if any(k in str(c).lower() for k in
        ("name","substation","station","bus_id","sub_id"))]
    hits=[]
    for bus,row in b.iterrows():
        vals={"index":str(bus)}
        vals.update({str(c):str(row[c]) for c in textual if str(row[c]).strip() not in ("","nan","None")})
        if any("colstrip" in v.casefold() for v in vals.values()):
            hits.append({"bus_id":str(bus),"matching_fields":{k:v for k,v in vals.items() if "colstrip" in v.casefold()},
                         "v_nom_kv":None if "v_nom" not in row or str(row["v_nom"])=="nan" else str(row["v_nom"]),
                         "connected_lines":int(((n.lines.bus0.astype(str)==str(bus))|(n.lines.bus1.astype(str)==str(bus))).sum()) if len(n.lines) else 0})
    report={"network_buses":len(b),"text_columns_searched":textual,
      "explicit_colstrip_name_candidates":hits,"candidate_count":len(hits),
      "coordinate_nearest_bus_inferred":False,
      "independently_verified_eia_generator_bus_ties":0,
      "warning":"Textual bus matches alone do not establish Clearwater electrical network connectivity."}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
    return report
if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("--network",type=Path,required=True);a.add_argument("--out",type=Path,required=True)
    x=a.parse_args();inspect(x.network,x.out)
