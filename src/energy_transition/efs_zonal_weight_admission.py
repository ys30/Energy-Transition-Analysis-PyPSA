"""Strict admission gate for externally sourced state-to-ReEDS-zone demand weights.

No weights are inferred from region membership or transmission capacities.
Input CSV schema: state,zone,weight ; values are fractions, not percentages.
"""
from __future__ import annotations
import argparse,csv,io,json,math
from pathlib import Path

def validate_weights(mapping:dict, csv_bytes:bytes, *, tol:float=1e-6)->dict:
    rows=list(csv.DictReader(io.StringIO(csv_bytes.decode("utf-8-sig"))))
    if not rows or set(rows[0]) != {"state","zone","weight"}:
        raise ValueError("Expected CSV columns: state,zone,weight")
    targets={s:set(zones) for s,zones in mapping["state_to_all_membership_zones"].items()}
    if not targets or any(not zones for zones in targets.values()):
        raise ValueError("Each mapped state must have at least one target zone")
    owners={}
    for st,zones in targets.items():
        for zone in zones:
            if zone in owners and owners[zone] != st:
                raise ValueError(f"Zone assigned to multiple states: {zone}")
            owners[zone]=st
    seen=set()
    sums={s:0.0 for s in targets}
    for r in rows:
        if None in r or any(value is None for value in r.values()):
            raise ValueError("Malformed CSV row: unexpected or missing column")
        st,zone=r["state"].strip(),r["zone"].strip()
        if st not in targets or zone not in targets[st]:
            raise ValueError(f"Unknown state-zone pair: {st}/{zone}")
        if (st,zone) in seen: raise ValueError(f"Duplicate pair: {st}/{zone}")
        seen.add((st,zone))
        val=float(r["weight"])
        if not math.isfinite(val) or val<0 or val>1:
            raise ValueError(f"Invalid allocation fraction: {st}/{zone}")
        sums[st]+=val
    missing=sorted((s,z) for s,zones in targets.items() for z in zones if (s,z) not in seen)
    if missing: raise ValueError(f"Missing target state-zone weights: {missing}")
    bad={s:v for s,v in sums.items() if abs(v-1)>tol}
    if bad: raise ValueError(f"State demand fractions fail conservation: {bad}")
    expected={z for zones in targets.values() for z in zones}
    available={z for zones in mapping["state_to_network_zones"].values() for z in zones}
    missing_buses=sorted(expected-available)
    return {"validated_states":len(targets),"validated_zone_weights":len(rows),
            "per_state_fraction_sum":sums,"missing_network_buses":missing_buses,
            "weights_schema_valid":True,
            "ready_for_full_network_dispatch":not missing_buses,
            "warning":"Mapping validates mass conservation, not the empirical provenance of weights"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mapping",type=Path,required=True)
    p.add_argument("--weights",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    a=p.parse_args()
    result=validate_weights(json.loads(a.mapping.read_text()),a.weights.read_bytes())
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
    if not result["ready_for_full_network_dispatch"]:
        raise SystemExit("Weight schema valid but missing ReEDS zone buses: full model admission blocked")
if __name__=="__main__":main()
