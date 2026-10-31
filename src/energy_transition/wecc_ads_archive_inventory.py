"""Inventory a legally acquired ADS archive without assuming its proprietary schema.

Does not extract, execute or convert unknown files. No source data is bundled.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import zipfile


def inventory(path: Path, *, max_member_bytes: int = 1_000_000_000) -> dict:
    if not 0 < max_member_bytes <= 20_000_000_000:
        raise ValueError("max_member_bytes must be between 1 and 20 billion")
    path=Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    hasher=hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b""):
            hasher.update(chunk)
    candidates={".raw":"power_flow_raw_candidate",".sav":"power_flow_binary_candidate",
                ".m":"matpower_script_candidate",".mci":"power_flow_aux_candidate",
                ".mdb":"access_database_candidate",".accdb":"access_database_candidate",
                ".dat":"pcm_data_candidate",".csv":"tabular_data_candidate"}
    result={"archive":path.name,"sha256":hasher.hexdigest(),
            "size_bytes":path.stat().st_size,"files":[],"ready_for_pypsa_line":False,
            "status":"file_inventory_only_no_branch_physics_verified"}
    with zipfile.ZipFile(path) as archive:
        members=archive.infolist()
        if len(members)>100000:
            raise ValueError("Archive member count exceeds inspection limit")
        if sum(m.file_size for m in members)>20_000_000_000:
            raise ValueError("Archive uncompressed size exceeds inspection limit")
        for member in members:
            if member.is_dir():
                continue
            name=member.filename
            if name.startswith("/") or ".." in Path(name).parts or "\\" in name:
                raise ValueError("Unsafe archive entry path")
            if member.file_size>max_member_bytes:
                raise ValueError("Unexpected oversized archive member")
            ext=Path(name).suffix.lower()
            result["files"].append({"name":name,"size_bytes":member.file_size,
                                    "extension":ext,
                                    "candidate_type":candidates.get(ext,"unknown_or_supporting_file"),
                                    "requires_schema_inspection":ext in candidates})
    result["files"].sort(key=lambda x:x["name"])
    result["candidate_model_files"]=[f["name"] for f in result["files"]
                                      if f["requires_schema_inspection"]]
    result["candidate_count"]=len(result["candidate_model_files"])
    result["parser_selected"]=False
    result["caution"]="Extensions are hints only; no member content or electrical physics verified"
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--max-member-bytes",type=int,default=1_000_000_000)
    args=parser.parse_args()
    report=inventory(args.archive,max_member_bytes=args.max_member_bytes)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2))
    print(json.dumps({"archive":report["archive"],"members":len(report["files"]),
                      "ready_for_pypsa_line":False},indent=2))


if __name__=="__main__":
    main()
