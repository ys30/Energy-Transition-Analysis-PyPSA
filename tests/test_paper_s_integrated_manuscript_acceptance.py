"""Paper S editorial QA: source evidence and actual solver model claims.

No external files/network. Guards accidental manuscript changes that reverse
source-authenticated source-year/calendar and numeric interpretation.
"""
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
MANUSCRIPT=ROOT/"docs/PAPER_S_INTEGRATED_ENGLISH_MANUSCRIPT_V1_2026-11-12.md"
LIBRARY=ROOT/"docs/PAPER_S_VERIFIED_REFERENCE_LIBRARY_AND_METHOD_ATTRIBUTION_2026-11-12.md"
ARCHITECTURE=ROOT/"docs/PAPER_S_INTEGRATED_SUBMISSION_ARCHITECTURE_EVIDENCE_AUDIT_2026-11-12.md"

def text(path):
    assert path.is_file(),f"Missing audited source {path.name}"
    return path.read_text(encoding="utf-8")

def test_integrated_paper_all_primary_sections_and_real_refs():
    s=text(MANUSCRIPT)
    for heading in ("## Abstract","## 1. Introduction","## 2. Materials and methods",
                    "## 3. Results","## 4. Discussion","## 5. Conclusions",
                    "## Data and code availability","## References and original data sources"):
        assert heading in s,heading
    for ref in ("R1","R2","R3","R4","R5","D1","D2","D3"):
        assert re.search(r"\["+ref+r"\]",s),ref
    for doi in ("10.1016/j.euroecorev.2018.07.004","10.1016/j.joule.2018.08.006",
                "10.1038/s41592-019-0686-2","10.5334/jors.188"):
        assert doi in s
    assert "authentic" in s.lower()
    assert len(s)>13000

def test_experimental_source_year_sample_and_no_2014_imputation():
    s=text(MANUSCRIPT)
    assert "2007–2013 and 2016–2023" in s
    assert "2010, 2011, 2012 and 2013" in s
    assert "2014" in s
    assert "96" in s and "24" in s and "16" in s
    assert "43281182390" in s and "43281182402" in s
    assert "Feb" in s and "December 31" in s
    assert "$0.004863" in s

def test_solver_and_terminal_conditions_are_not_misattributed():
    s=text(MANUSCRIPT)
    solver=text(ROOT/"src/energy_transition/efs_cyclic_storage_lp.py")
    assert "linprog(objective" in solver and 'method="highs"' in solver
    assert "firm_peak_ratio=1.2" in solver
    assert "add(3*n,n-1,5,1.)" in solver
    assert "firm generation power bound is 1.2 times" in s
    assert "initial SOC is zero" in s and "terminal SOC is also constrained to zero" in s
    assert "not solved as PyPSA networks" in s
    assert "SciPy" in s
    assert "R4" in text(LIBRARY)

def test_weather_conditioned_economic_claim_and_figure_admission():
    s=text(MANUSCRIPT)
    assert "Only 2012" in s
    assert "one of 16" in s
    assert "9.868" in s and "10.955" in s
    assert "43288856607" in s
    assert "13976367223" in s
    assert "climate-change" in s
    assert "not a statistical" not in s or "probability" in s
    assert "four main figures" in text(ARCHITECTURE) or "four primary" in text(ARCHITECTURE).lower()
