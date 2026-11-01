"""Audit EIA-860 operating fleet versus actual Western network geography.

State coincidence is NOT a valid generator-to-bus or BA-to-ReEDS-zone mapping.
Never generate plant bus assignments from this report.
"""
import argparse,json
from pathlib import Path
import pandas as pd
import pypsa
STATE_CODES={"Arizona":"AZ","California":"CA","Colorado":"CO","Idaho":"ID",
 "Montana":"MT","Nevada":"NV","New Mexico":"NM","Oregon":"OR",
 "Texas":"TX","Utah":"UT","Washington":"WA","Wyoming":"WY"}
def standardize(values):
 return values.astype("string").str.strip().replace(STATE_CODES).str.upper()

def audit(gens,network):
 df=pd.read_csv(gens,dtype={"plant_id":"string","generator_id":"string"})
 n=pypsa.Network(str(network))
 req={"state","capacity_mw","status","crosswalk_status","plant_id","generator_id","ba_code"}
 if req-set(df.columns):raise ValueError("Missing source fields")
 op=df.loc[df.status.astype(str).str.strip().eq("OP") & df.crosswalk_status.eq("matched")].copy()
 op.capacity_mw=pd.to_numeric(op.capacity_mw,errors="coerce")
 op=op.loc[op.capacity_mw.notna() & op.capacity_mw.ge(0)]
 if op.empty:raise ValueError("No operating mapped units")
 b=n.buses.copy()
 if "state" not in b:raise ValueError("Network bus state missing")
 bus_code=standardize(b.state)
 gen_code=standardize(op.state)
 bus_states=set(bus_code.dropna())
 gen_states=set(gen_code.dropna())
 unknown=sorted(bus_states-set(STATE_CODES.values()))
 if unknown:raise ValueError(f"Unmapped Western bus state labels: {unknown}")
 overlap=sorted(gen_states&bus_states)
 if not overlap:raise ValueError("Zero overlap after normalized state names: check EIA and network schemas")
 rows=[]
 for state in sorted(gen_states|bus_states):
  g=op.loc[gen_code.eq(state)]
  rows.append({"state":state,"operating_generators":len(g),
    "operating_nameplate_mw":float(g.capacity_mw.sum()),
    "actual_network_buses":int(bus_code.eq(state).sum()),
    "network_and_generator_state_overlap":state in overlap})
 return {"source":"EIA-860 official operating generators and pinned actual PyPSA-USA base network",
  "state_labels_normalized":True,
  "states_in_both":overlap,"state_comparison":rows,
  "operating_generators_total":len(op),"operating_nameplate_mw":float(op.capacity_mw.sum()),
  "generator_bus_crosswalk_verified":False,
  "generator_coordinates_verified":False,
  "ba_to_reeds_zone_mapping_verified":False,
  "real_fleet_dispatch_ready":False,
  "warning":"Only state-level coverage comparison; never assume every plant is in Western interconnection or assign plants to buses by state."}

if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--generators",required=True,type=Path)
 p.add_argument("--network",required=True,type=Path)
 p.add_argument("--out",required=True,type=Path)
 a=p.parse_args();result=audit(a.generators,a.network)
 a.out.parent.mkdir(parents=True,exist_ok=True)
 a.out.write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps({"states_in_both":result["states_in_both"],"operating_generators_total":result["operating_generators_total"],"real_fleet_dispatch_ready":False},indent=2))
