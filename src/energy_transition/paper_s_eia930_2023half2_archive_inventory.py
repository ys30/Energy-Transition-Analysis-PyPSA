"""Audit archived *raw* EIA-930 2023 H2 files, with publisher checksum.

No EIA API key is needed. This phase inventories file structures and
examples; it does not imply a BA-to-state mapping, measured capacity factor,
or observed-vs-modeled error calculation.

Archive mirrored from EIA by the open-data PUDL project, Zenodo record
22856870, file eia930-2023half2.zip. Exact MD5 pin is from Zenodo metadata.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,zipfile
from pathlib import Path

ZENODO_URL="https://zenodo.org/records/22856870/files/eia930-2023half2.zip?download=1"
ZENODO_RECORD="https://zenodo.org/records/22856870"
EXPECTED_MD5="1de4e47693426671123bb08ec0d33995"
TARGET_YEAR=2023


def inventory(path):
    p=Path(path)
    if p.name!="eia930-2023half2.zip":
        raise ValueError("Incorrect 2023 half-year source filename")
    h=hashlib.md5()
    sha=hashlib.sha256()
    with p.open("rb") as handle:
        for block in iter(lambda:handle.read(2**20),b""):
            h.update(block);sha.update(block)
    if h.hexdigest()!=EXPECTED_MD5:
        raise ValueError("EIA930 Zenodo mirrored archive MD5 mismatch")
    files=[]
    with zipfile.ZipFile(p) as z:
        for info in z.infolist():
            if info.is_dir():continue
            if not info.filename.lower().endswith((".csv",".txt",".json",".xlsx",".zip")):
                continue
            entry={"archive_path":info.filename,
                   "uncompressed_bytes":info.file_size,"compressed_bytes":info.compress_size}
            if info.filename.lower().endswith((".csv",".txt")):
                # Read a limited preview only. Never assume column names, ordering,
                # metadata conventions or 2023 H2 temporal coverage.
                with z.open(info) as stream:
                    preview=stream.read(32768).decode("utf-8-sig","replace")
                lines=preview.splitlines()[:5]
                entry["preview_first_five_lines"]=[x[:2500] for x in lines]
                if lines:
                    try:entry["detected_csv_header"]=next(csv.reader([lines[0]]))
                    except csv.Error:entry["detected_csv_header"]=[]
            files.append(entry)
    if not files:raise ValueError("No supported data files inside source archive")
    return {"status":"EIA930_2023H2_ARCHIVED_RAW_SOURCE_MD5_VERIFIED",
        "source_url":ZENODO_URL,"source_record":ZENODO_RECORD,
        "file_name":p.name,"md5":h.hexdigest(),"sha256":sha.hexdigest(),
        "archived_files":files,"file_count":len(files),
        "data_are_raw_EIA930":True,"archive_mirror_is_third_party":True,
        "EIA_API_key_required":False,"2023_hourly_data_parsed":False,
        "BA_to_state_aggregation_performed":False,
        "observed_vs_ReEDS_validation_performed":False}


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--archive",type=Path,required=True)
    a.add_argument("--out",type=Path,required=True)
    opts=a.parse_args()
    report=inventory(opts.archive)
    opts.out.mkdir(parents=True,exist_ok=True)
    output=opts.out/"paper_s_eia930_2023half2_zip_source_inventory.json"
    output.write_text(json.dumps(report,indent=2)+"\n")
    print("PAPER_S_EIA930_2023H2_RAW_ARCHIVE_MD5_OK",
          report["md5"],report["file_count"])
if __name__=="__main__":main()
