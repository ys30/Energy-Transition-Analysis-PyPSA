"""Export the original numbered Paper S bibliography to RIS and audit CSV.

These are IMPORT CANDIDATES, NOT 74 independently publisher-verified records.
Authors with 'et al.' and corporate names may need manual correction.
"""
from pathlib import Path
import re,csv
src=Path("docs/PAPER_S_74_BIBLIOGRAPHY_SOURCE_EXTRACT_2026-11-23.md").read_text()
records=[]
for m in re.finditer(r"(?m)^\[(\d+)\] (.+)$",src):
    n=int(m.group(1)); raw=m.group(2).strip()
    yy=re.search(r"\((20\d{2}|19\d{2})\)\.",raw)
    if yy:
        authors=raw[:yy.start()].strip(" ,")
        year=yy.group(1)
        tail=raw[yy.end():].strip()
    else:
        authors="";year="";tail=raw
    doi=re.search(r"https?://(?:dx\.)?doi\.org/([^\s)]+)",raw)
    url=re.search(r"https?://[^\s)]+",raw)
    d=(doi.group(1).rstrip(".,;") if doi else "")
    title=tail.split(". ")[0].rstrip(".") if tail else raw
    if n==41:
        title="Geographical balancing of wind power decreases storage needs in a 100% renewable European power sector"
        d="10.1016/j.isci.2023.107074"
        tail="iScience 26(7), 107074. DOI 10.1016/j.isci.2023.107074"
    if n==69:
        authors="Obika, K., & Cole, W.";year="2026"
        title="ReEDS: Historical electricity demand profiles (v1)"
        d="10.5281/zenodo.18462671"
    if n==17:
        title="2025 Annual Technology Baseline (ATB) Cost and Performance Data for Electricity Generation Technologies"
        tail+="; 2025_v2_Workbook_11-11-2026.xlsx (source file version, NOT a new publication year)"
    records.append(dict(number=n,year=year,authors=authors,title=title,doi=d,url=("https://doi.org/"+d if d else (url.group(0).rstrip(".,;") if url else "")),original_citation=raw,external_verified=("source_record_check" if n in (17,41,69) else "not_independently_verified")))
assert len(records)==74 and [r["number"] for r in records]==list(range(1,75))
out=Path("outputs");out.mkdir(exist_ok=True)
with (out/"Paper_S_74_Reference_Audit.csv").open("w",newline="",encoding="utf-8-sig") as f:
    w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
ris=[]
for r in records:
    ris.extend(["TY  - DATA" if r["number"] in (17,69) else "TY  - GEN",
    "ID  - PaperS-"+str(r["number"]),"TI  - "+r["title"]])
    if r["year"]:ris.append("PY  - "+r["year"])
    if r["authors"]:
        ris.append("N1  - Original author string: "+r["authors"])
    if r["doi"]:ris.append("DO  - "+r["doi"])
    if r["url"]:ris.append("UR  - "+r["url"])
    ris+=["N1  - Original reference: "+r["original_citation"],
          "N1  - Verification: "+r["external_verified"],
          "ER  - ",""]
(out/"Paper_S_74_References_Import_Candidates.ris").write_text("\n".join(ris),encoding="utf-8")
(out/"README_Reference_Import.txt").write_text(
    "74 records transcribed from Paper_S_Main_2026-11-20.docx. This RIS is a provisional reference-manager import; only #17, #41 and #69 were specifically source-checked. "
    "Other entries require Crossref/DOI metadata synchronization after import. "
    "The raw original citation is retained in N1; author strings are deliberately not converted to unreliable AU fields. "
    "Roth & Schill: iScience 26(7), article 107074 DOI 10.1016/j.isci.2023.107074. "
    "ATB 2025 v2: same 2025 ATB collection, workbook dated 11-11-2026. "
    "#69 historical demand: Obika and Cole (not the separate 2026 county-profile paper with Rivers).\n")
print("PAPER_S_REFERENCES_74_TRANSCRIPTION_EXPORT_PASS",len(records))
