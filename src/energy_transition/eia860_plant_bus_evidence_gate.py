"""Fail-closed admission of EIA-860 plant-to-bus electrical connection evidence.

Geographic nearest-bus proposals are *never* electrical connection evidence.
Only an independently sourced, explicitly reviewed record agreeing with a
real network bus can pass this administrative gate. Physical validation,
generator-to-plant reconciliation, and dispatch readiness remain separate.
"""
import argparse
import json
from pathlib import Path

import pandas as pd
import pypsa

REQUIRED_EVIDENCE = {
    "plant_id", "verified_bus_id", "evidence_source", "reviewer",
    "evidence_status", "electrical_connection_verified",
}


def audit(candidates_path: Path, evidence_path: Path, network_path: Path, out: Path):
    candidates = pd.read_csv(
        candidates_path, dtype={"plant_id": "string", "nearest_candidate_bus": "string"}
    )
    evidence = pd.read_csv(
        evidence_path, dtype={"plant_id": "string", "verified_bus_id": "string"}
    )
    required_candidates = {
        "plant_id", "nearest_candidate_bus", "assignment_status",
        "electrical_connection_verified",
    }
    if required_candidates - set(candidates):
        raise ValueError("Missing geographic candidate columns")
    if REQUIRED_EVIDENCE - set(evidence):
        raise ValueError("Missing independent electrical evidence columns")
    if candidates.empty:
        raise ValueError("Empty geographic candidate inventory")
    if (candidates.plant_id.isna().any() or candidates.plant_id.duplicated().any()
            or candidates.nearest_candidate_bus.isna().any()):
        raise ValueError("Missing or duplicate candidate identifiers")
    if evidence.plant_id.isna().any() or evidence.plant_id.duplicated().any():
        raise ValueError("Missing or duplicate evidence plant identifiers")
    candidate_flags = candidates.electrical_connection_verified.astype("string").str.lower().str.strip()
    if (not candidates.assignment_status.eq("geographic_candidate_only").all()
            or not candidate_flags.eq("false").all()):
        raise ValueError("Candidates cannot certify electrical connectivity")
    approved = evidence.evidence_status.astype("string").str.lower().str.strip().eq("reviewed_approved")
    flags = evidence.electrical_connection_verified.astype("string").str.lower().str.strip()
    if flags.isna().any() or not flags.isin(["true", "false"]).all():
        raise ValueError("Invalid electrical verification flag")
    if (approved != flags.eq("true")).any():
        raise ValueError("Evidence status and verification flag disagree")
    network = pypsa.Network(str(network_path))
    bus_ids = set(network.buses.index.astype(str))
    result = candidates.merge(evidence, on="plant_id", how="left", validate="one_to_one", suffixes=("_candidate", "_evidence"))
    matched = result.evidence_status.astype("string").str.lower().str.strip().eq("reviewed_approved")
    known_bus = result.verified_bus_id.isin(bus_ids)
    source = result.evidence_source.astype("string").str.strip()
    reviewer = result.reviewer.astype("string").str.strip()
    # Explicit independent provenance and human review are required; a
    # candidate-generated status/nearest bus alone cannot satisfy this check.
    has_provenance = source.notna() & source.str.len().gt(0) & reviewer.notna() & reviewer.str.len().gt(0)
    verified = matched & known_bus & has_provenance & result.electrical_connection_verified_evidence.astype("string").str.lower().eq("true")
    result["candidate_matches_verified_bus"] = result.nearest_candidate_bus.eq(result.verified_bus_id).fillna(False)
    result["evidence_admitted"] = verified.fillna(False)
    result["admission_status"] = "blocked_missing_or_unapproved_evidence"
    result.loc[matched & ~known_bus, "admission_status"] = "blocked_bus_not_in_network"
    result.loc[matched & known_bus & ~has_provenance, "admission_status"] = "blocked_missing_source_or_reviewer"
    result.loc[result.evidence_admitted, "admission_status"] = "reviewed_electrical_bus_evidence"
    result["ready_for_full_western_opf"] = False
    out.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(out, index=False)
    summary = {
        "candidate_plants": int(len(result)),
        "independently_reviewed_electrical_bus_evidence_records": int(result.evidence_admitted.sum()),
        "candidate_matches_verified_bus": int((result.evidence_admitted & result.candidate_matches_verified_bus).sum()),
        "status_counts": {str(k): int(v) for k, v in result.admission_status.value_counts().items()},
        "geographic_candidates_not_electrical_proof": True,
        "generator_level_capacity_and_dispatch_verified": False,
        "full_western_opf_ready": False,
        "warning": "Reviewed evidence of a plant bus is not generator-level dispatch readiness; verify electrical POI, source version, unit capacity and operational constraints separately.",
    }
    out.with_suffix(".json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--network", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    audit(args.candidates, args.evidence, args.network, args.out)


if __name__ == "__main__":
    main()
