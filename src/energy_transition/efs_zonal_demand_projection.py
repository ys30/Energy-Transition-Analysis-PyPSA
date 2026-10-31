"""Project externally supplied state demand onto ReEDS zones with strict conservation.

This utility does not retrieve or invent demand or allocation weights. Both
inputs must be separately documented and validated before interpretation.
"""
from __future__ import annotations
import math
from collections import defaultdict


def allocate_state_demand(state_demand: list[dict], weights: list[dict],
                          *, tolerance: float = 1e-6) -> list[dict]:
    by_state = defaultdict(dict)
    zone_owner = {}
    for row in weights:
        state, zone = row["state"], row["zone"]
        key = (state, zone)
        if zone in zone_owner and zone_owner[zone] != state:
            raise ValueError(f"Zone assigned to multiple states: {zone}")
        zone_owner[zone] = state
        if zone in by_state[state]:
            raise ValueError(f"Duplicate zone allocation: {key}")
        value = float(row["weight"])
        if not math.isfinite(value) or not 0 <= value <= 1:
            raise ValueError(f"Invalid allocation fraction: {key}")
        by_state[state][zone] = value
    if not by_state:
        raise ValueError("No weights provided")
    for state, shares in by_state.items():
        if abs(sum(shares.values()) - 1) > tolerance:
            raise ValueError(f"Unbalanced state shares: {state}")
    output = []
    seen = set()
    snapshots_by_state = defaultdict(set)
    covered_states = set()
    for row in state_demand:
        state, snapshot = row["state"], row["snapshot"]
        key = (state, snapshot)
        if key in seen:
            raise ValueError(f"Duplicate state snapshot: {key}")
        seen.add(key)
        snapshots_by_state[state].add(snapshot)
        if state not in by_state:
            raise ValueError(f"Missing allocation for state: {state}")
        demand = float(row["demand_mw"])
        if not math.isfinite(demand) or demand < 0:
            raise ValueError(f"Invalid state demand: {key}")
        covered_states.add(state)
        for zone, fraction in sorted(by_state[state].items()):
            output.append({"state": state, "snapshot": snapshot, "zone": zone,
                           "demand_mw": demand * fraction})
    if covered_states != set(by_state):
        raise ValueError(f"State coverage mismatch: {sorted(set(by_state) - covered_states)}")
    reference = next(iter(snapshots_by_state.values()))
    for state, snapshots in snapshots_by_state.items():
        if snapshots != reference:
            raise ValueError(f"State time coverage differs for {state}: missing or extra snapshots")
    return output
