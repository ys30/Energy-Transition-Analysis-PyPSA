"""Audit official ReEDS state-to-Western-zone membership without inventing load weights.

A state containing multiple zones needs validated allocation weights before
EFS state-level demand can enter the zonal PyPSA optimization.
"""
from __future__ import annotations
import argparse,csv,io,json,hashlib
from collections import defaultdict
from pathlib import Path
from urllib.request import urlopen
from .naris2024_western_subset import MEMBERSHIP_URL,western_region_ids

def audit_membership(data:bytes,network_buses:set[str])->dict:
    rows=list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))
    required={"ba","st","interconnect","country"}
    if not rows or not required.issubset(rows[0]): raise ValueError("Missing authoritative membership columns")
    western=western_region_ids(data)
    zones_by_state=defaultdict(list)
    for row in rows:
        if row["ba"] not in western: continue
        state=row["st"].strip()
        if not state: raise ValueError("Missing state membership")
        zones_by_state[state].append(row["ba"])
    matched={st:sorted(set(zones)&network_buses) for st,zones in zones_by_state.items()}
    unmatched=sorted(western-network_buses)
    duplicate={z for st,zones in zones_by_state.items() for z in zones if sum(z in v for v in zones_by_state.values())>1}
    if duplicate: raise ValueError(f"Zone belongs to multiple states: {sorted(duplicate)}")
    return {"source":MEMBERSHIP_URL,"sha256":hashlib.sha256(data).hexdigest(),
            "western_membership_zones":len(western),"matched_network_zones":len(western&network_buses),
            "unmatched_membership_zones":unmatched,"state_zone_counts":{k:len(v) for k,v in sorted(matched.items())},
            "multi_zone_states":[k for k,v in sorted(matched.items()) if len(v)>1],
            "state_to_zonal_demand_weights_available":False,
            "can_disaggregate_EFS_state_demand":False,
            "reason":"Membership gives categorical zones, not defensible numerical state-to-zone load shares"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--network",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    args=p.parse_args()
    import pypsa
    network=pypsa.Network(args.network)
    with urlopen(MEMBERSHIP_URL,timeout=40) as response: data=response.read(1_000_001)
    if len(data)>1_000_000: raise ValueError("Membership file exceeds safety limit")
    report=audit_membership(data,set(network.buses.index))
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
