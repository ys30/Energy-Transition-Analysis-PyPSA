"""Build text-and-table-only Paper S v2 Word review artifact.

This is intentionally a manuscript consistency draft, NOT the final illustrated
journal submission. Verified figures and final bibliography must be integrated
and visually QA'd before deposit or submission.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

DEFAULT_SOURCE = Path("docs/PAPER_S_INTEGRATED_ENGLISH_MANUSCRIPT_V2_2026-11-22.md")

def plain(s: str) -> str:
    s = re.sub(r"\[([^]]+)\]\(([^)]+)\)", r"\1 (\2)", s)
    return s.replace("**", "").replace("`", "").replace("*", "").strip()

def make(source: Path, output: Path):
    md = source.read_text(encoding="utf-8")
    required = [
        "## Abstract", "## 2. Materials and methods", "## 3. Results",
        "## 4. Discussion", "## 5. Conclusions",
        "## Data and code availability", "CO +0.410384",
        "213/1,080", "180-LP"
    ]
    missing = [item for item in required if item.casefold() not in md.casefold()]
    if missing:
        raise ValueError(f"Source is not integrated v2: missing {missing}")
    doc = Document()
    sec=doc.sections[0]
    sec.top_margin=Inches(.85);sec.bottom_margin=Inches(.8)
    sec.left_margin=Inches(.95);sec.right_margin=Inches(.95)
    style=doc.styles["Normal"]
    style.font.name="Aptos";style.font.size=Pt(10)
    style.paragraph_format.space_after=Pt(6)
    header=sec.header.paragraphs[0]
    header.text="Paper S  |  15-year source-audited review  |  NOT FOR SUBMISSION"
    header.style="Caption"
    footer=sec.footer.paragraphs[0]
    footer.text="Text-only editorial preview: figures, reference style and layout QA pending"
    footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
    footer.style="Caption"
    lines=md.splitlines()
    in_table=False
    i=0
    while i<len(lines):
        line=lines[i].strip()
        if not line or line=="---":
            i+=1;continue
        if line.startswith("# "):
            doc.add_heading(plain(line[2:]),0)
            i+=1;continue
        if line.startswith("## "):
            doc.add_heading(plain(line[3:]),1)
            i+=1;continue
        if line.startswith("### "):
            doc.add_heading(plain(line[4:]),2)
            i+=1;continue
        if line.startswith("|"):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith("|"):
                vals=[plain(s) for s in lines[i].strip().strip("|").split("|")]
                if not all(re.match(r"^:?-{3,}:?$",s) for s in vals):
                    rows.append(vals)
                i+=1
            if rows:
                t=doc.add_table(rows=1,cols=len(rows[0]))
                t.style="Light Shading Accent 1"
                for k,s in enumerate(rows[0]):t.rows[0].cells[k].text=s
                for vals in rows[1:]:
                    cells=t.add_row().cells
                    for k,s in enumerate(vals[:len(cells)]):cells[k].text=s
            continue
        doc.add_paragraph(plain(line))
        i+=1
    output.parent.mkdir(parents=True,exist_ok=True)
    doc.save(output)
    check=Document(output)
    full="\n".join(p.text for p in check.paragraphs)
    for item in ("15-weather-year", "213/1,080", "+0.410", "-2.177", "Conclusions"):
        if item.casefold() not in full.casefold():
            raise ValueError(f"Missing in Word: {item}")
    return len(full),len(check.tables)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source",type=Path,default=DEFAULT_SOURCE)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    n,t=make(args.source,args.out)
    h=hashlib.sha256(args.out.read_bytes()).hexdigest()
    manifest={"status":"TEXT_ONLY_EDITORIAL_REVIEW_NOT_SUBMISSION",
      "source":str(args.source),"word_file":str(args.out),
      "word_sha256":h,"paragraph_text_characters":n,"tables":t,
      "old_2010_2013_figures_attached":False,
      "journal_visual_and_reference_qa_completed":False}
    manifest_path=args.out.with_suffix(".manifest.json")
    manifest_path.write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print("PAPER_S_V2_TEXT_REVIEW_DOCX_PASS",json.dumps(manifest))

if __name__=="__main__":
    main()
