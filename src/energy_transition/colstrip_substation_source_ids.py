"""Inspect source-network substation identifiers near the documented Colstrip POI.

This is an inventory for research; never promote geographic or numeric
substation candidates into validated Clearwater electrical ties.
"""
import argparse,json
from pathlib import Path
import pandas as pd
import pypsa

def inspect(path,out):
    n=pypsa.Network(str(path))
    b=n.buses
    cols=[c for c in ("sub_id","substation_off","v_nom","x","y","state","country","carrier") if c in b.columns]
    if "sub_id" not in b.columns:
        raise ValueError("Source network has no sub_id; investigate upstream bus schema")
    target=b.loc[b.get("state",pd.Series(index=b.index,dtype="object")).astype("string").str.upper().eq("MT").fillna(False)].copy()
    voltage=pd.to_numeric(b["v_nom"],errors="coerce") if "v_nom" in b.columns else pd.Series(index=b.index,dtype=float)
    mt=target
    entries=[]
    for bus,row in target.iterrows():
        if "v_nom" in row and pd.to_numeric(pd.Series([row["v_nom"]]),errors="coerce").iloc[0]!=500:
            continue
        entries.append({"bus_id":str(bus),**{str(c):(None if pd.isna(row[c]) else str(row[c])) for c in cols},
            "lines_incident":int(((n.lines.bus0.astype(str)==str(bus))|(n.lines.bus1.astype(str)==str(bus))).sum()) if len(n.lines) else 0})
    report={"source_bus_count":len(b),
            "state_label_counts":b["state"].astype("string").fillna("<missing>").value_counts().head(30).to_dict() if "state" in b.columns else {},
            "montana_bus_count":len(mt),
            "montana_voltage_kv_counts":pd.to_numeric(mt["v_nom"],errors="coerce").value_counts().head(30).rename_axis("voltage").to_dict() if "v_nom" in mt.columns else {},
            "all_network_500kv_bus_count":int(voltage.eq(500).sum()),
            "montana_500kv_bus_candidates":len(entries),
            "candidate_rows":entries,"field_inventory":cols,
            "documentary_substation_name_crosswalk_available":False,
            "independently_verified_clearwater_bus_ties":0,
            "caution":"These are Montana 500-kV candidates, NOT identified Colstrip buses."}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"source_bus_count":len(b),"montana_500kv_bus_candidates":len(entries),
         "field_inventory":cols,"montana_bus_count":len(mt),
         "montana_voltage_kv_counts":report["montana_voltage_kv_counts"],
         "all_network_500kv_bus_count":report["all_network_500kv_bus_count"],
         "state_label_counts":report["state_label_counts"],"verified_ties":0},indent=2))
if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--network",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args();inspect(a.network,a.out)
