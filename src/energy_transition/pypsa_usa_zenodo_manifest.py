"""Verify public PyPSA-USA dataset metadata without downloading 567 MB.

Only checks Zenodo record metadata and presence of the advertised archive.
Does not authenticate network topology or run a model.
"""
from __future__ import annotations
import argparse
import json
import urllib.request
from pathlib import Path

ZENODO_API="https://zenodo.org/api/records/14611937"
DATA_ARCHIVE="pypsa_usa_data.zip"


def summarize_record(record: dict) -> dict:
    files=record.get("files",[])
    candidates=[f for f in files if f.get("key")==DATA_ARCHIVE]
    if len(candidates)!=1:
        raise ValueError("Expected exactly one PyPSA-USA data archive in record")
    f=candidates[0]
    checksum=f.get("checksum","")
    if not checksum.startswith("md5:") or len(checksum)!=36:
        raise ValueError("Missing or malformed Zenodo MD5 metadata")
    size=f.get("size")
    if type(size) is not int or size<=0:
        raise ValueError("Invalid Zenodo file size")
    return {
        "zenodo_record_id":record.get("id"),"doi":record.get("doi"),
        "archive_name":DATA_ARCHIVE,"archive_size_bytes":size,
        "published_archive_checksum":checksum,
        "archive_downloaded":False,"network_data_parsed":False,
        "planning_case_solved":False,
        "warning":"Publisher metadata only; checksum not independently validated until download",
    }


def fetch_record(url: str = ZENODO_API) -> dict:
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"ProjectB-PyPSA-source-audit/1.0"}),timeout=30) as response:
        return json.load(response)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--record-json",type=Path,help="Use saved official Zenodo API JSON for deterministic tests")
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    record=json.loads(a.record_json.read_text()) if a.record_json else fetch_record()
    summary=summarize_record(record)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))


if __name__=="__main__":
    main()
