"""Summarize a genuine upstream Snakemake data_model dry-run log."""
import argparse
import json
import re
from pathlib import Path

REQUIRED = {
    "retrieve_zenodo_databundles",
    "retrieve_nrel_efs_data",
    "build_base_network",
    "build_electrical_demand",
    "build_renewable_profiles",
    "add_demand",
    "cluster_network",
    "add_extra_components",
    "prepare_network",
    "add_sectors",
    "data_model",
}
EXPECTED_TARGET = "resources/Default/western/elec_s75_c33_ec_lv1.0_REM-3h_E.nc"


def summarize(log: str) -> dict:
    rules = sorted(set(re.findall(r"(?m)^\s*(?:localrule|rule)\s+([A-Za-z_][\w]*):", log)))
    match = re.search(r"(?m)^\s*total\s+(\d+)\s*$", log)
    target = re.search(r"(?m)^\s*(?:localrule|rule) data_model:\s*\n\s*input:\s*(\S+)", log)
    missing = sorted(REQUIRED - set(rules))
    if not match or not target or missing:
        raise ValueError(f"Incomplete data_model DAG evidence: missing rules={missing}")
    if target.group(1) != EXPECTED_TARGET:
        raise ValueError(f"Unexpected data_model target: {target.group(1)}")
    return {
        "dag_parsed": True,
        "jobs_total": int(match.group(1)),
        "rules_seen": rules,
        "data_model_input_network": target.group(1),
        "true_network_built": False,
        "efs_data_downloaded": False,
        "western_laf_empirically_verified": False,
        "note": "Snakemake dry-run topology only; no real network output produced.",
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--log", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    data = summarize(a.log.read_text(encoding="utf-8"))
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
