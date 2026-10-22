# -*- coding: utf-8 -*-
"""Remove leading 4-digit line numbers from patent source docx (keeps everything else)."""
from __future__ import annotations

import re
from pathlib import Path

from docx import Document

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT.parent / "Diary_One_专利源代码_60页_3000行.docx"
OUT = ROOT.parent / "Diary_One_专利源代码_60页_3000行_无行号.docx"

LINE_PREFIX = re.compile(r"^\d{4}  ")


def strip_line_numbers(doc: Document) -> int:
    n = 0
    for para in doc.paragraphs:
        if not para.runs:
            continue
        # Merge runs text for matching; usually one run per code line
        full = "".join(r.text for r in para.runs)
        if not LINE_PREFIX.match(full):
            continue
        new_text = LINE_PREFIX.sub("", full, count=1)
        para.runs[0].text = new_text
        for r in para.runs[1:]:
            r.text = ""
        n += 1
    return n


def main() -> None:
    if not SRC.is_file():
        raise SystemExit(f"Source not found: {SRC}")
    doc = Document(str(SRC))
    count = strip_line_numbers(doc)
    doc.save(str(OUT))
    print(f"Stripped prefixes from {count} paragraphs")
    print(f"Wrote: {OUT}")


if __name__ == "__main__":
    main()
