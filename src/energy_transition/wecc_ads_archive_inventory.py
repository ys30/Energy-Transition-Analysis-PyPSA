"""Inventory a legally acquired ADS archive without assuming its proprietary schema.

Does not extract, execute or convert unknown files. No source data is bundled.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import zipfile


def inventory(path: Path) -> dict:
    path=Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    data=path.read_bytes()
    result={"archive":path.name,"sha256":hashlib.sha256(data).hexdigest(),
            "size_bytes":len(data),"files":[],"ready_for_pypsa_line":False,
            "status":"file_inventory_only_no_branch_physics_verified"}
    with zipfile.ZipFile(path) as archive:
        for member in archive.infolist():
            if member.is_dir():
                continue
            name=member.filename
            if name.startswith("/") or ".." in Path(name).parts or "\\" in name:
                raise ValueError("Unsafe archive entry path")
            if member.file_size>1_000_000_000:
                raise ValueError("Unexpected oversized archive member")
            result["files"].append({"name":name,"size_bytes":member.file_size,
                                    "extension":Path(name).suffix.lower()})
    result["files"].sort(key=lambda x:x["name"])
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    report=inventory(args.archive)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2))
    print(json.dumps({"archive":report["archive"],"members":len(report["files"]),
                      "ready_for_pypsa_line":False},indent=2))


if __name__=="__main__":
    main()
