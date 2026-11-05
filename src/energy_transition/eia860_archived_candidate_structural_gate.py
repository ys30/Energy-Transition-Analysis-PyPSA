"""Evidence-only structural assessment of a candidate synthetic PyPSA bus.

Archived source-node electrical attributes are checked directly from the
network. A geographically nearest synthetic bus is never admitted as a
utility-authenticated point of interconnection.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from .eia860_spptop3_poi_evidence_gate import check_manifest

EXPECTED_ID = "2053003"
PLANT_IDS = {"63578", "56458", "2454"}


def assess(network, ledger: dict, provenance: dict) -> dict:
    summary = check_manifest(ledger)
    if provenance.get("source_bus_id_meaning") != "synthetic_source_model_bus_id":
        raise ValueError("Unexpected bus identity provenance")
    if provenance.get("utility_authenticated_electrical_facility_identities") is not False:
        raise ValueError("Unsupported authenticated source bus claim")
    if provenance.get("eia860_electrical_interconnection_approved") is not False:
        raise ValueError("Unsupported electrical approval")
    if EXPECTED_ID not in network.buses.index.astype(str):
        raise ValueError("Missing original candidate bus in archived network")
    bus = network.buses.loc[EXPECTED_ID]
    voltage = float(bus["v_nom"])
    if not math.isfinite(voltage) or voltage <= 0:
        raise ValueError("Invalid original candidate bus nominal voltage")
    if abs(voltage - 115.) > 1e-6:
        raise ValueError(f"Archived candidate voltage changed: {voltage} kV")
    def connected(frame):
        if frame is None or frame.empty:
            return [], []
        if not {"bus0", "bus1"}.issubset(frame.columns):
            raise ValueError("Incomplete archived branch topology columns")
        b0 = frame["bus0"].astype(str)
        b1 = frame["bus1"].astype(str)
        idx = (b0 == EXPECTED_ID) | (b1 == EXPECTED_ID)
        selected = frame[idx]
        endpoints = sorted({str(x) for row in selected[["bus0", "bus1"]].itertuples(index=False, name=None)
                            for x in row if str(x) != EXPECTED_ID})
        return list(selected.index.astype(str)), endpoints
    lines, line_peers = connected(network.lines)
    transformers, trans_peers = connected(network.transformers)
    links, link_peers = connected(network.links)
    if len(lines) != 2 or len(transformers) != 0 or len(line_peers) != 2:
        raise ValueError("Archived source topology differs from verified baseline")
    if set(line_peers) != {"2053019", "2053021"}:
        raise ValueError("Archived branch neighboring bus identities changed")
    rows = []
    for entry in sorted(ledger["records"], key=lambda x: str(x["eia_plant_id"])):
        pid = str(entry["eia_plant_id"])
        if pid not in PLANT_IDS or str(entry["synthetic_candidate_bus"]) != EXPECTED_ID:
            raise ValueError("Unknown EIA candidate identity")
        documented = entry.get("external_voltage_kv")
        if documented is None:
            classification = "unit_side_not_comparable_to_poi"
        elif abs(float(documented) - voltage) > 1e-6:
            classification = "named_external_voltage_differs_from_synthetic_bus"
        else:
            classification = "nominal_voltage_matches_but_no_poi_evidence"
        rows.append({
            "plant_id": pid,
            "plant_name": entry["eia_plant_name"],
            "historical_nameplate_mw": float(entry["eia_nameplate_mw"]),
            "candidate_bus_id": EXPECTED_ID,
            "archived_synthetic_bus_v_nom_kv": voltage,
            "documented_external_voltage_kv": documented,
            "comparison_class": classification,
            "electrical_identity_verified": False,
            "generator_injection_approved": False
        })
    return {
        "status": "ARCHIVED_SOURCE_TOPOLOGY_VERIFIED_NO_REAL_POI",
        "source_network_family": provenance["source_network_family"],
        "candidate_bus": EXPECTED_ID,
        "candidate_nominal_voltage_kv": voltage,
        "incident_lines": len(lines),
        "incident_transformers": len(transformers),
        "incident_links": len(links),
        "line_neighbor_ids": line_peers,
        "transformer_neighbor_ids": trans_peers,
        "link_neighbor_ids": link_peers,
        "plants": rows,
        "historical_nameplate_reviewed_mw": float(summary["documented_2024_eia_nameplate_mw"]),
        "independently_verified_electrical_poi_count": 0,
        "admitted_real_generator_mw": 0,
        "full_western_opf_admitted": False,
        "warning": "Source topology attributes cannot establish real facility identity, line ratings or plant POI."
    }


def main():
    import pypsa
    p = argparse.ArgumentParser()
    for key in ("network", "ledger", "provenance", "out"):
        p.add_argument("--" + key, type=Path, required=True)
    args = p.parse_args()
    result = assess(pypsa.Network(str(args.network)),
                    json.loads(args.ledger.read_text()),
                    json.loads(args.provenance.read_text()))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
