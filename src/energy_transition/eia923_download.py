"""Download an explicitly supplied official EIA-923 XLSX with provenance.

The official EIA download layout changes across vintages. The URL is supplied
explicitly, never guessed from the year. Only eia.gov HTTPS is accepted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import urllib.parse
import urllib.request
import zipfile


def download_official_eia923(url: str, destination: Path, *, year: int):
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in ("eia.gov", "www.eia.gov"):
        raise ValueError("Official EIA-923 source must be an HTTPS eia.gov URL")
    if parsed.username or parsed.password:
        raise ValueError("Credentials are not permitted in the EIA URL")
    request = urllib.request.Request(url, headers={"User-Agent": "energy-transition-research/0.3"})
    with urllib.request.urlopen(request, timeout=120) as response:
        final = urllib.parse.urlparse(response.geturl())
        if final.scheme != "https" or final.hostname not in ("eia.gov", "www.eia.gov"):
            raise ValueError("EIA-923 download redirected outside official eia.gov")
        raw = response.read()
    if not zipfile.is_zipfile(__import__("io").BytesIO(raw)):
        raise ValueError("Downloaded EIA-923 file is not a valid XLSX/ZIP archive")
    with zipfile.ZipFile(__import__("io").BytesIO(raw)) as archive:
        names = archive.namelist()
        if "[Content_Types].xml" not in names or not any(n.startswith("xl/") for n in names):
            raise ValueError("Downloaded file is not an XLSX workbook")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(raw)
    report = {
        "source_url": url, "resolved_url": response.geturl(),
        "report_year_requested": year, "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "file": destination.name,
        "caution": "Workbook report year must still be independently checked against source metadata."
    }
    destination.with_suffix(".provenance.json").write_text(json.dumps(report, indent=2))
    return report


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--url", required=True, help="Verified official EIA-923 XLSX URL")
    p.add_argument("--year", type=int, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    print(json.dumps(download_official_eia923(args.url, args.output, year=args.year), indent=2))


if __name__ == "__main__":
    main()
