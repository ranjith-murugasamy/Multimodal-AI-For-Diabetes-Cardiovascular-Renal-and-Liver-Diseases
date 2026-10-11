"""Local text-overlap check of the manuscript against the supplied proposal PDF.

This is NOT a substitute for iThenticate/Turnitin: it only measures verbatim
word n-gram overlap with the local source documents. It reports the share of
manuscript n-grams that also occur in each source and lists the longest shared
word runs so that they can be paraphrased or quoted.

Usage: .venv/bin/python scripts/similarity_check.py [manuscript_text.txt]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "output" / "paper" / "final"
MANUSCRIPT = Path(sys.argv[1]) if len(sys.argv) > 1 else FINAL / "manuscript_text.txt"
SOURCES = {
    "base-paper.pdf": None,  # extracted below
    "generic-spec-template.md": ROOT / "specs" / "generic-spec-template.md",
    "01_manuscript_development_draft.md": ROOT / "output" / "paper" / "01_manuscript_development_draft.md",
}
# Boilerplate that is expected to repeat and is not counted as copying.
STOP_RUNS = [r"area under the receiver operating characteristic curve", r"mean absolute shap value"]


def words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+(?:[-'][a-z0-9]+)*", text.lower())


def pdf_text(path: Path) -> str:
    out = []
    for page in PdfReader(str(path)).pages:
        out.append(page.extract_text() or "")
    # this PDF extracts one token per line; normalise whitespace
    return re.sub(r"\s+", " ", " ".join(out))


def ngrams(ws: list[str], n: int) -> set[tuple[str, ...]]:
    return {tuple(ws[i : i + n]) for i in range(len(ws) - n + 1)}


def longest_runs(m: list[str], s: list[str], min_len: int) -> list[tuple[int, str]]:
    """Maximal word runs of the manuscript that also appear verbatim in the source."""
    s_grams = ngrams(s, min_len)
    runs, i = [], 0
    while i <= len(m) - min_len:
        if tuple(m[i : i + min_len]) in s_grams:
            j = i + min_len
            while j < len(m) and tuple(m[j - min_len + 1 : j + 1]) in s_grams:
                j += 1
            runs.append((j - i, " ".join(m[i:j])))
            i = j
        else:
            i += 1
    return sorted(runs, reverse=True)


def main() -> None:
    manuscript = words(MANUSCRIPT.read_text(encoding="utf-8"))
    report = {"manuscript_words": len(manuscript), "sources": {}}
    for name, path in SOURCES.items():
        text = pdf_text(ROOT / "input" / name) if path is None else path.read_text(encoding="utf-8")
        src = words(text)
        entry = {"source_words": len(src)}
        for n in (4, 6, 8):
            mg = ngrams(manuscript, n)
            shared = mg & ngrams(src, n)
            entry[f"{n}gram_overlap_pct"] = round(100 * len(shared) / max(1, len(mg)), 2)
        entry["longest_runs"] = [{"words": k, "text": t} for k, t in longest_runs(manuscript, src, 6)[:10]]
        report["sources"][name] = entry
    out = FINAL / "similarity_report.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    for name, e in report["sources"].items():
        print(f"{name}: 4-gram {e['4gram_overlap_pct']}%  6-gram {e['6gram_overlap_pct']}%  8-gram {e['8gram_overlap_pct']}%")
        for r in e["longest_runs"][:5]:
            print(f"   [{r['words']} words] {r['text']}")


if __name__ == "__main__":
    main()
