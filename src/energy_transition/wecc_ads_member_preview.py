"""Preview safe text-like members of an authorized grid-model ZIP.

This is byte inspection, not a WECC electrical-model decoder. Binary database
and saved-case files are intentionally not opened or interpreted.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import zipfile
from .wecc_ads_archive_inventory import inventory

TEXT_SUFFIXES={".csv",".txt",".dat",".raw",".m"}
MAX_PREVIEW=4096
MAX_MEMBER=50_000_000


def preview_archive(path: Path) -> dict:
    manifest=inventory(path)
    previews=[]
    with zipfile.ZipFile(path) as z:
        for item in manifest["files"]:
            name=item["name"]
            ext=item["extension"]
            record={"name":name,"extension":ext,"size_bytes":item["size_bytes"]}
            if ext not in TEXT_SUFFIXES:
                record["status"]="not_text_previewed"
            elif item["size_bytes"]>MAX_MEMBER:
                record["status"]="oversized_not_previewed"
            else:
                with z.open(name) as stream:
                    raw=stream.read(MAX_PREVIEW+1)
                if b"\\x00" in raw:
                    record["status"]="binary_content_not_previewed"
                else:
                    record["status"]="text_sample_only"
                    record["sample_utf8"]=raw[:MAX_PREVIEW].decode("utf-8",errors="replace")
                    record["sample_truncated"]=len(raw)>MAX_PREVIEW or item["size_bytes"]>MAX_PREVIEW
            previews.append(record)
    return {"archive":manifest["archive"],"archive_sha256":manifest["sha256"],
            "ready_for_pypsa_line":False,"source_authenticity_confirmed":False,
            "caution":"Content previews are untrusted and do not establish electrical branch data",
            "members":previews}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    a=p.parse_args()
    result=preview_archive(a.archive)
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(result,indent=2)+"\\n")
    print(json.dumps({"archive":result["archive"],"members":len(result["members"]),
                      "ready_for_pypsa_line":False}))


if __name__=="__main__":
    main()
