"""Evidence gate for externally derived EFS state-to-ReEDS zonal weights.

A syntactically valid allocation is not an empirically sourced allocation.
The manifest must be supplied by the researcher alongside the actual weights.
This gate verifies provenance metadata and file integrity, not the truth of the
external geographic calculation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse

from .efs_zonal_weight_admission import validate_weights

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_METHODS = {"population_geographic_overlay", "upstream_verified_laf"}

def assess_weight_provenance(mapping: dict, weights_bytes: bytes, manifest: dict) -> dict:
    """Fail closed for dispatch admission if geographic provenance is incomplete."""
    schema = validate_weights(mapping, weights_bytes)
    required = ("weights_sha256", "source_url", "source_revision",
                "geographic_method", "geography_vintage", "population_vintage",
                "processing_script_sha256", "coverage_note")
    missing = [k for k in required if not isinstance(manifest.get(k), str) or not manifest[k].strip()]
    digest = hashlib.sha256(weights_bytes).hexdigest()
    errors = []
    if missing:
        errors.append("Missing provenance fields: " + ", ".join(missing))
    recorded = manifest.get("weights_sha256", "")
    if not isinstance(recorded, str) or not _SHA256.fullmatch(recorded):
        errors.append("weights_sha256 must be lowercase 64-character SHA-256")
    elif recorded != digest:
        errors.append("weights_sha256 does not match input bytes")
    script_digest = manifest.get("processing_script_sha256", "")
    if not isinstance(script_digest, str) or not _SHA256.fullmatch(script_digest):
        errors.append("processing_script_sha256 must be lowercase 64-character SHA-256")
    url = manifest.get("source_url", "")
    parsed = urlparse(url) if isinstance(url, str) else urlparse("")
    if parsed.scheme != "https" or not parsed.netloc:
        errors.append("source_url must be an HTTPS source URL")
    if manifest.get("geographic_method") not in _METHODS:
        errors.append("geographic_method must identify a supported geographic allocation method")
    return {
        **schema,
        "computed_weights_sha256": digest,
        "provenance_metadata_valid": not errors,
        "provenance_errors": errors,
        "ready_for_full_network_dispatch": (
            schema["ready_for_full_network_dispatch"] and not errors
        ),
        "warning": (
            "Provenance metadata and checksums verified; external geographic "
            "derivation and empirical validity still require independent review."
        ),
    }

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mapping", type=Path, required=True)
    parser.add_argument("--weights", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    result = assess_weight_provenance(
        json.loads(args.mapping.read_text(encoding="utf-8")),
        args.weights.read_bytes(),
        json.loads(args.manifest.read_text(encoding="utf-8")),
    )
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not result["ready_for_full_network_dispatch"]:
        raise SystemExit("EFS geographic allocation evidence gate failed; dispatch blocked")

if __name__ == "__main__":
    main()
