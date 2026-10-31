"""Create a source-backed zonal PyPSA network from NARIS interface ratings.

Uses separate directed Links to preserve asymmetry. No physical AC power-flow
or historical 2024 demand/generation calibration is implied.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
from urllib.request import urlopen
from .naris2024_interface_intake import SOURCE, inspect_csv


def build_network(raw: bytes):
    import pypsa
    audit=inspect_csv(raw)
    data=list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    n=pypsa.Network()
    areas=sorted({x for r in data for x in (r["r"],r["rr"])})
    for ba in areas:
        n.add("Bus",ba)
    count=0
    for idx,r in enumerate(data):
        a,b=r["r"],r["rr"]
        for suffix,origin,destination,column in (
            ("forward",a,b,"MW_f0"),("reverse",b,a,"MW_r0")):
            mw=float(r[column])
            if mw>0:
                n.add("Link",f"naris_{idx}_{suffix}",bus0=origin,bus1=destination,
                      p_nom=mw,efficiency=1.0,p_min_pu=0,p_max_pu=1)
                count+=1
    assert len(n.buses)==audit["regions"]
    return n,{**audit,"bus_count":len(n.buses),"directional_link_count":count,
              "link_semantics":"independent directed zonal transfer capacity in MW",
              "physical_ac_lines":0,"historical_dispatch_calibrated":False,
              "network_solved":False}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--csv",type=Path,help="Local pinned NARIS source CSV")
    p.add_argument("--network",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    a=p.parse_args()
    if a.csv:
        raw=a.csv.read_bytes()
    else:
        with urlopen(SOURCE,timeout=40) as response:
            raw=response.read(2_000_001)
        if len(raw)>2_000_000:
            raise ValueError("Unexpectedly large source")
    n,summary=build_network(raw)
    a.network.parent.mkdir(parents=True,exist_ok=True)
    a.report.parent.mkdir(parents=True,exist_ok=True)
    n.export_to_netcdf(a.network)
    a.report.write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))


if __name__=="__main__":
    main()
