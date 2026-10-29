"""Inspect the official annual EIA-923 workbook structure without assuming columns.

EIA-923 generation and fuel are reported at mixed plant/prime-mover/fuel
granularities; this command audits the source structure before any BA calibration.
"""
import argparse
import io
import json
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

URL = "https://www.eia.gov/electricity/data/eia923/archive/xls/f923_{year}.zip"


def inspect_archive(content: bytes):
    result = []
    with zipfile.ZipFile(io.BytesIO(content)) as z:
        files = [x for x in z.namelist() if x.lower().endswith((".xlsx", ".xls"))]
        if not files:
            raise ValueError("No Excel workbooks in official EIA-923 ZIP")
        for filename in files:
            workbook = pd.ExcelFile(io.BytesIO(z.read(filename)))
            for sheet in workbook.sheet_names:
                preview = {}
                for header in (0, 1, 2, 3, 4, 5):
                    frame = pd.read_excel(workbook, sheet_name=sheet, header=header, nrows=5)
                    preview[str(header)] = [str(c) for c in frame.columns]
                result.append({"filename": filename, "sheet": sheet, "headers": preview})
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, default=2024)
    parser.add_argument("--output", type=Path, default=Path("outputs/eia923_schema"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    url = URL.format(year=args.year)
    req = urllib.request.Request(url, headers={"User-Agent": "Energy-Transition-Analysis-PyPSA/0.5"})
    with urllib.request.urlopen(req, timeout=120) as response:
        content = response.read()
    report = {"year": args.year, "source_url": url, "zip_bytes": len(content),
              "workbooks": inspect_archive(content),
              "caution": "Schema inventory only. No generation or fuel totals inferred; BA crosswalk and mixed-granularity audit required."}
    (args.output / f"eia923_schema_{args.year}.json").write_text(json.dumps(report, indent=2))
    print(json.dumps({"year": args.year, "zip_bytes": len(content),
                      "sheets": [(x["filename"], x["sheet"]) for x in report["workbooks"]]}, indent=2))


if __name__ == "__main__":
    main()
