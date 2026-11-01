"""Preflight a locally checked-out, pinned PyPSA-USA v0.8.0 build.

Does not download raw inputs, launch Snakemake, or claim empirical readiness.
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

PIN = "338af9912addbaf038c6098fe27e1e6ef099d8aa"
EXPECTED = {
    "interconnect": ["western"],
    "planning_horizons": [2030, 2040, 2050],
    "transmission_network": "reeds",
    "topological_boundaries": "reeds_zone",
}


def preflight(root: Path) -> dict:
    import yaml
    if not (root / "workflow" / "Snakefile").is_file():
        raise ValueError("PyPSA-USA workflow/Snakefile missing")
    actual = subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
    ).strip()
    if actual != PIN:
        raise ValueError(f"PyPSA-USA commit mismatch: {actual}; expected {PIN}")
    config_file = root / "workflow" / "config" / "config.default.yaml"
    if not config_file.is_file():
        raise ValueError("Copied workflow/config/config.default.yaml is missing; run init_pypsa_usa.sh")
    cfg = yaml.safe_load(config_file.read_text(encoding="utf-8"))
    actual_config = {**cfg.get("scenario", {}), **cfg.get("model_topology", {})}
    mismatch = {
        key: (actual_config.get(key), value)
        for key, value in EXPECTED.items() if actual_config.get(key) != value
    }
    if mismatch:
        raise ValueError(f"Pinned Western ReEDS run config mismatch: {mismatch}")
    demand = cfg.get("electricity", {}).get("demand", {})
    demand_expected = {"profile": "efs"}
    scenario_expected = {"efs_case": "reference", "efs_speed": "moderate"}
    if any(demand.get(k) != v for k, v in demand_expected.items()):
        raise ValueError("Pinned PyPSA-USA EFS demand profile mismatch")
    if any(demand.get("scenario", {}).get(k) != v
           for k, v in scenario_expected.items()):
        raise ValueError("Pinned PyPSA-USA EFS demand scenario mismatch")
    snakefile = (root / "workflow" / "Snakefile").read_text(encoding="utf-8")
    merged = ("config.cluster.yaml", "config.common.yaml",
              "config.plotting.yaml", "config.api.yaml", "config.sector.yaml")
    missing = [name for name in merged if f'configfile: "config/{name}"' not in snakefile]
    if missing:
        raise ValueError(f"Unexpected upstream Snakefile config merge: {missing}")
    config_files = [config_file] + [
        root / "workflow" / "config" / name for name in merged
    ]
    absent = [str(path) for path in config_files if not path.is_file()]
    if absent:
        raise ValueError(f"Missing merged upstream config files: {absent}")
    # Parse every merged YAML file instead of only confirming its existence.
    # Reject configs whose data structure cannot safely participate in merge.
    for path in config_files:
        parsed = yaml.safe_load(path.read_text(encoding="utf-8"))
        if parsed is not None and not isinstance(parsed, dict):
            raise ValueError(f"Upstream configuration must be a YAML mapping: {path.name}")
    # The cloned repository must be clean: uncommitted edits invalidate the
    # meaning of the pinned SHA even if git rev-parse still reports the pin.
    dirty = subprocess.check_output(
        ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=no"],
        text=True,
    ).strip()
    if dirty:
        raise ValueError("Pinned PyPSA-USA tracked working tree has modifications")
    digests = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in config_files
    }
    return {
        "upstream_sha": actual,
        "verified_default_config": EXPECTED,
        "verified_efs_demand": {**demand_expected, **scenario_expected},
        "other_configs_merged": list(merged),
        "config_file_sha256": digests,
        "snakefile_sha256": hashlib.sha256(snakefile.encode()).hexdigest(),
        "dry_run_required": True,
        "real_network_built": False,
        "laf_weights_extracted": False,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--checkout", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    a = p.parse_args()
    result = preflight(a.checkout)
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
