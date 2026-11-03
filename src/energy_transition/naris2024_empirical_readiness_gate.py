"""Fail-closed evidence matrix for Western NARIS empirical-dispatch readiness.

A successful synthetic OPF establishes numerical plumbing, never acceptance
of empirical loads, generation or transmission assumptions.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path


def evaluate(optimization: dict, membership: dict, *,
             allocation: dict | None = None,
             generation: dict | None = None) -> dict:
    if optimization.get("solver_condition") != "optimal" or optimization.get("solver_status") != "ok":
        raise ValueError("No verified optimal network solve")
    if optimization.get("zones") != membership.get("result_buses"):
        raise ValueError("Network membership and solved zone count mismatch")
    if optimization.get("directional_links") != membership.get("directed_links"):
        raise ValueError("Network membership and Link count mismatch")
    if membership.get("invented_links") != 0:
        raise ValueError("Invented interface cannot be admitted as source-backed")
    if sorted(optimization.get("isolated_zone_ids", [])) != sorted(membership.get("all_isolated_zones", [])):
        raise ValueError("Isolated zone inventory mismatch")

    real_weights = bool(allocation and
        allocation.get("allocation_weights_validated") is True and
        allocation.get("independent_source_verified") is True)
    real_generators = bool(generation and
        generation.get("actual_generator_bus_mapping_verified") is True and
        generation.get("hourly_availability_verified") is True and
        generation.get("marginal_fuel_cost_verified") is True and
        generation.get("ready_for_full_real_generation_dispatch") is True)
    empirical_load = bool(
        optimization.get("synthetic_fixture") is False
        and optimization.get("source_backed_load_report_flags_present") is True
        and optimization.get("empirical_hourly_load_source_verified") is True
        and optimization.get("hourly_load_source_conservation_verified") is True
    )
    checks = {
        "synthetic_numerical_chain_passed": True,
        "real_source_loads_admitted": empirical_load,
        "independent_allocation_factors_verified": real_weights,
        "mapped_real_fleet_availability_and_cost_verified": real_generators,
        "isolated_zone_interface_resolution_verified": not membership.get("all_isolated_zones"),
        "transmission_planning_semantics_accepted_for_research_question": False,
        "real_data_dispatch_calibrated": False,
    }
    # It is deliberate that the last two gates cannot be auto-approved from
    # a nominal synthetic solve or self-reported metadata.
    return {
        "evidence_scope": "synthetic_numerical_integration_only",
        "model_zones": optimization["zones"],
        "directional_planning_links": optimization["directional_links"],
        "isolated_zones": sorted(membership.get("all_isolated_zones", [])),
        "readiness_gates": checks,
        "verified_gates": [k for k,v in checks.items() if v],
        "blocked_gates": [k for k,v in checks.items() if not v],
        "empirical_full_network_ready": all(checks.values()),
        "paper_historical_grid_claim_allowed": False,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--optimization", type=Path, required=True)
    p.add_argument("--membership", type=Path, required=True)
    p.add_argument("--allocation", type=Path)
    p.add_argument("--generation", type=Path)
    p.add_argument("--report", type=Path, required=True)
    a = p.parse_args()
    def read(path):
        return json.loads(path.read_text(encoding="utf-8")) if path else None
    result = evaluate(read(a.optimization), read(a.membership),
                      allocation=read(a.allocation), generation=read(a.generation))
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
