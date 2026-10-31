"""Download a pinned public PyPSA-USA archive and verify it before inspection."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request
from .pypsa_usa_zenodo_manifest import fetch_record, summarize_record, DATA_ARCHIVE

MAX_BYTES=800_000_000

def verified_download(record: dict, destination: Path) -> dict:
    meta=summarize_record(record)
    entry=next(f for f in record["files"] if f["key"]==DATA_ARCHIVE)
    url=entry.get("links",{}).get("self")
    if not isinstance(url,str) or not url.startswith("https://zenodo.org/api/records/"):
        raise ValueError("Unexpected Zenodo download URL")
    if meta["archive_size_bytes"]>MAX_BYTES:
        raise ValueError("Archive exceeds download size cap")
    destination=Path(destination)
    destination.parent.mkdir(parents=True,exist_ok=True)
    temporary=destination.with_suffix(destination.suffix+".partial")
    digest=hashlib.md5()
    count=0
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"ProjectB-PyPSA-archive/1.0"}),timeout=120) as response, temporary.open("wb") as out:
            while chunk:=response.read(1024*1024):
                count+=len(chunk)
                if count>MAX_BYTES or count>meta["archive_size_bytes"]:
                    raise ValueError("Downloaded file exceeds expected size")
                digest.update(chunk)
                out.write(chunk)
        if count!=meta["archive_size_bytes"] or "md5:"+digest.hexdigest()!=meta["published_archive_checksum"]:
            raise ValueError("Zenodo archive length/checksum mismatch")
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)
    return {"archive_name":destination.name,"bytes":count,"published_md5_verified":True,
            "network_data_parsed":False,"planning_case_solved":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    args=p.parse_args()
    result=verified_download(fetch_record(),args.archive)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))

if __name__=="__main__":
    main()
