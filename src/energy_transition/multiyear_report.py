"""Validate and summarize seven independently solved historical EIA-930 years.

This is a descriptive historical dispatch comparison, NOT an investment model.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def aggregate(root: Path, output: Path, years=range(2019, 2026)):
    rows, audits, energy_audits = [], [], []
    for year in years:
        folder = root / f"eia930-west-{year}"
        metrics_path = folder / str(year) / "metrics.json"
        audit_path = folder / f"ba_audit_{year}.csv"
        energy_path = folder / f"energy_audit_{year}.json"
        for path in (metrics_path, audit_path, energy_path):
            if not path.is_file():
                raise FileNotFoundError(f"Required verified artifact missing: {path}")
        metrics = json.loads(metrics_path.read_text())
        energy = json.loads(energy_path.read_text())
        if metrics.get("solve_status") != "optimal":
            raise ValueError(f"Non-optimal solve for {year}: {metrics.get('solve_status')}")
        if energy.get("year") != year:
            raise ValueError(f"Wrong year in energy audit: {year}")
        if energy.get("relative_energy_difference", 1) > 1e-10:
            raise ValueError(f"Representative energy mismatch in {year}")
        if metrics.get("observed_demand_mwh", -1) <= 0:
            raise ValueError(f"Invalid demand in {year}")
        if abs(metrics["observed_demand_mwh"] - energy["raw_demand_mwh_after_qc"]) > max(
            1e-5, metrics["observed_demand_mwh"] * 1e-10
        ):
            raise ValueError(f"Dispatch and input audit disagree for {year}")
        with audit_path.open(newline="") as f:
            ba_rows = list(csv.DictReader(f))
        if not ba_rows or len(ba_rows) != len(energy["balancing_authorities"]):
            raise ValueError(f"BA audit count mismatch in {year}")
        if {r["respondent"] for r in ba_rows} != set(energy["balancing_authorities"]):
            raise ValueError(f"BA audit identity mismatch in {year}")
        for r in ba_rows:
            if int(r["observations"]) != int(r["expected_hours"]):
                raise ValueError(f"Incomplete BA input: {year} {r['respondent']}")
            if float(r.get("imputation_share", 0)) > 0.01:
                raise ValueError(f"BA imputation exceeds threshold: {year} {r['respondent']}")
            audits.append({"year": year, **r})
        generation = metrics.get("dispatch_mwh_by_carrier", {})
        rows.append({
            "year": year,
            "observed_demand_mwh": metrics["observed_demand_mwh"],
            "unserved_mwh": metrics["unserved_mwh"],
            "unserved_share": metrics["unserved_share"],
            "assumed_operational_tco2": metrics["operational_tco2_assumed"],
            "assumed_objective_usd": metrics["objective_usd_assumed"],
            **{f"dispatch_{k}_mwh": v for k, v in sorted(generation.items())},
        })
        energy_audits.append(energy)
    output.mkdir(parents=True, exist_ok=True)
    for filename, data in (("yearly_summary.csv", rows), ("ba_audit_all_years.csv", audits)):
        with (output / filename).open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for r in data for k in r)))
            writer.writeheader()
            writer.writerows(data)
    (output / "energy_audit_all_years.json").write_text(json.dumps(energy_audits, indent=2))
    (output / "README.txt").write_text(
        "Observed input: EIA-930 hourly BA demand, 2019-2025. "
        "Generator fleet, costs and emissions are scenario assumptions. "
        "Annual dispatch is independent, not multi-investment-period optimization. "
        "Representative hours lose peak and chronological information.\n"
    )
    return rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--artifacts", type=Path, default=Path("yearly_artifacts"))
    p.add_argument("--output", type=Path, default=Path("multi_year_summary"))
    args = p.parse_args()
    aggregate(args.artifacts, args.output)


if __name__ == "__main__":
    main()
