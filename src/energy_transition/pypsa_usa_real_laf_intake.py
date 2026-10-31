"""One-command evidence-gated intake of a built PyPSA-USA network.

Produces candidate Western weights and an intake report. Does not certify
geographic derivation or enable empirical optimization automatically.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pypsa

from .pypsa_usa_built_network_intake import inspect_built_network
from .pypsa_usa_laf_weights import derive_state_zone_weights
from .efs_zonal_weight_admission import validate_weights


def import_built_laf(network_path: Path, membership_path: Path,
                     mapping_path: Path, output_dir: Path) -> dict:
    intake = inspect_built_network(network_path, membership_path)
    mapping = json.loads(Path(mapping_path).read_text(encoding="utf-8"))
    n = pypsa.Network(network_path)
    weights = derive_state_zone_weights(n.buses, mapping)
    contents = weights.to_csv(index=False).encode("utf-8")
    admission = validate_weights(mapping, contents)
    if not admission["ready_for_full_network_dispatch"]:
        raise ValueError("Weight matrix has unrepresented or misowned Western network zones")
    # Check the two independently supplied geographic references agree.
    from .naris2024_western_subset import western_region_ids
    expected = western_region_ids(Path(membership_path).read_bytes())
    mapped = {
        z for zones in mapping["state_to_all_membership_zones"].values()
        for z in zones
    }
    if mapped != expected:
        raise ValueError("Mapping and official Western membership zones disagree")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "candidate_western_laf_weights.csv").write_bytes(contents)
    report = {
        "intake": intake,
        "weight_admission": admission,
        "candidate_weight_rows": len(weights),
        "empirical_geographic_provenance_verified": False,
        "downstream_empirical_optimization_approved": False,
        "note": "Candidate shares only: inspect source build config and geography before publication or dispatch admission.",
    }
    (output_dir / "candidate_western_laf_report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--network", type=Path, required=True)
    parser.add_argument("--membership", type=Path, required=True)
    parser.add_argument("--mapping", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    a = parser.parse_args()
    print(json.dumps(import_built_laf(a.network, a.membership, a.mapping, a.out), indent=2))


if __name__ == "__main__":
    main()
