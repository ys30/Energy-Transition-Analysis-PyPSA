"""Restore Western ReEDS membership zones absent from NARIS interface table.

An isolated zone is explicitly NOT assigned an invented transmission link.
The full-coverage topology is a separate output from the 34-node connected
network used for illustrative synthetic transmission experiments.
"""
from __future__ import annotations
import argparse,csv,io,json
from pathlib import Path
from urllib.request import urlopen
import pypsa
from .naris2024_western_subset import MEMBERSHIP_URL,western_region_ids

def complete_western_coverage(network:pypsa.Network, membership:bytes):
    required=western_region_ids(membership)
    current=set(network.buses.index)
    extra=sorted(current-required)
    if extra: raise ValueError(f"Non-Western buses present: {extra}")
    missing=sorted(required-current)
    out=network.copy()
    for zone in missing:
        out.add("Bus",zone)
    endpoints=set(out.links.bus0).union(out.links.bus1)
    isolated=sorted(required-endpoints)
    if set(out.buses.index)!=required: raise ValueError("Incomplete Western coverage")
    return out,{"required_western_zones":len(required),"result_buses":len(out.buses),
                "added_isolated_zones":missing,"all_isolated_zones":isolated,
                "directed_links":len(out.links),"invented_links":0,
                "ready_for_empirical_dispatch":False,
                "reason":"Zone coverage is complete but missing interface connectivity and empirical load weights"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--network",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    args=p.parse_args()
    with urlopen(MEMBERSHIP_URL,timeout=40) as response: data=response.read(1_000_001)
    if len(data)>1_000_000:raise ValueError("Membership file too large")
    output,report=complete_western_coverage(pypsa.Network(args.input),data)
    args.network.parent.mkdir(parents=True,exist_ok=True)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    output.export_to_netcdf(args.network)
    args.report.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
