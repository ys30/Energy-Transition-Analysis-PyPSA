"""Preflight a locally checked-out, pinned PyPSA-USA v0.8.0 build.

Does not download raw inputs, launch Snakemake, or claim empirical readiness.
"""
import argparse
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
    run = cfg.get("run", {})
    mismatch = {
        key: (run.get(key), value)
        for key, value in EXPECTED.items() if run.get(key) != value
    }
    if mismatch:
        raise ValueError(f"Pinned Western ReEDS run config mismatch: {mismatch}")
    snakefile = (root / "workflow" / "Snakefile").read_text(encoding="utf-8")
    merged = ("config.cluster.yaml", "config.common.yaml",
              "config.plotting.yaml", "config.api.yaml", "config.sector.yaml")
    missing = [name for name in merged if f'configfile: "config/{name}"' not in snakefile]
    if missing:
        raise ValueError(f"Unexpected upstream Snakefile config merge: {missing}")
    return {
        "upstream_sha": actual,
        "verified_default_config": EXPECTED,
        "other_configs_merged": list(merged),
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
