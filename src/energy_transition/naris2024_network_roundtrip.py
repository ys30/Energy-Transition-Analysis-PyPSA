"""Independent NetCDF round-trip checks against the published NARIS interface table."""
from __future__ import annotations
import argparse
import csv
import io
import json
from pathlib import Path
from urllib.request import urlopen

from .naris2024_interface_intake import SOURCE, inspect_csv


def verify(network_path: Path, source: bytes) -> dict:
    import pypsa
    audit = inspect_csv(source)
    rows = list(csv.DictReader(io.StringIO(source.decode("utf-8-sig"))))
    network = pypsa.Network(str(network_path))
    expected_buses = {v for row in rows for v in (row["r"], row["rr"])}
    if set(network.buses.index) != expected_buses:
        raise ValueError("Exported buses do not match source regions")
    expected = {}
    for idx, row in enumerate(rows):
        for suffix, a, b, key in (
            ("forward", row["r"], row["rr"], "MW_f0"),
            ("reverse", row["rr"], row["r"], "MW_r0"),
        ):
            mw = float(row[key])
            if mw > 0:
                expected[f"naris_{idx}_{suffix}"] = (a, b, mw)
    if set(network.links.index) != set(expected):
        raise ValueError("Exported Link identifiers differ from source")
    for name, (a, b, mw) in expected.items():
        link = network.links.loc[name]
        if link.bus0 != a or link.bus1 != b or abs(float(link.p_nom) - mw) > 1e-6:
            raise ValueError(f"Incorrect direction or capacity: {name}")
        if abs(float(link.p_min_pu)) > 1e-9 or abs(float(link.p_max_pu) - 1) > 1e-9:
            raise ValueError(f"Invalid directed Link flow bounds: {name}")
    if len(network.lines) != 0:
        raise ValueError("Zonal Link model must not imply physical AC lines")
    return {**audit, "roundtrip_verified": True,
            "bus_count": len(network.buses), "link_count": len(network.links),
            "source_capacity_verified": True, "solved": False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--network", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with urlopen(SOURCE, timeout=40) as response:
        raw = response.read(2_000_001)
    if len(raw) > 2_000_000:
        raise ValueError("Source exceeds download bound")
    result = verify(args.network, raw)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
