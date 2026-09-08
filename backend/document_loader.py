"""Load Markdown, CSV, and PDF corpus files with section metadata."""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
CORPUS_DIR = ROOT / "corpus"

SECTION_HEADING_RE = re.compile(
    r"^(?:#{1,6}\s+)?Section\s+(\d+(?:\.\d+)*)\s+(.+?)\s*$",
    re.IGNORECASE,
)
NUMBERED_MD_RE = re.compile(
    r"^#{1,6}\s+(\d+(?:\.\d+)*)\s+(.+?)\s*$",
)
ALT_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def _clean(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _split_markdown_sections(text: str, source: str) -> list[dict[str, Any]]:
    lines = text.split("\n")
    sections: list[dict[str, Any]] = []
    current = {
        "section": "preamble",
        "title": Path(source).stem.replace("_", " ").title(),
        "lines": [],
    }

    for line in lines:
        stripped = line.strip()
        match = SECTION_HEADING_RE.match(stripped) or NUMBERED_MD_RE.match(stripped)
        alt = ALT_HEADING_RE.match(stripped) if not match else None
        if match:
            if current["lines"] and _clean("\n".join(current["lines"])):
                sections.append(
                    {
                        "text": _clean("\n".join(current["lines"])),
                        "source": source,
                        "section": current["section"],
                        "title": current["title"],
                    }
                )
            current = {
                "section": match.group(1),
                "title": match.group(2).strip(),
                "lines": [],
            }
        elif alt and len(alt.group(1)) <= 2:
            heading = alt.group(2).strip()
            if heading.lower().startswith("nexus university") or heading.lower() in {
                "academic regulations",
                "attendance policy",
                "examination rules",
                "fee policy",
                "hostel handbook",
                "student discipline",
                "scholarship policy",
                "medical exemption rules",
            }:
                current["lines"].append(heading)
                continue
            if current["lines"] and _clean("\n".join(current["lines"])):
                sections.append(
                    {
                        "text": _clean("\n".join(current["lines"])),
                        "source": source,
                        "section": current["section"],
                        "title": current["title"],
                    }
                )
            current = {
                "section": "preamble",
                "title": heading,
                "lines": [],
            }
        else:
            current["lines"].append(line)

    if current["lines"] and _clean("\n".join(current["lines"])):
        sections.append(
            {
                "text": _clean("\n".join(current["lines"])),
                "source": source,
                "section": current["section"],
                "title": current["title"],
            }
        )
    return sections


def load_markdown(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    return _split_markdown_sections(text, path.name)


def load_csv(path: Path) -> list[dict[str, Any]]:
    docs: list[dict[str, Any]] = []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for index, row in enumerate(reader, start=1):
            parts = [f"{key}: {value}" for key, value in row.items() if value]
            text = (
                "Nexus University fee deadline record. "
                + ". ".join(parts)
                + "."
            )
            category = row.get("category") or row.get("fee_type") or f"row-{index}"
            semester = row.get("semester") or ""
            title = f"{category} deadline {semester}".strip()
            docs.append(
                {
                    "text": text,
                    "source": path.name,
                    "section": f"CSV-{index}",
                    "title": title,
                }
            )
    return docs


def load_pdf(path: Path) -> list[dict[str, Any]]:
    reader = PdfReader(str(path))
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    text = _clean("\n".join(pages))
    if not text:
        return []
    return _split_markdown_sections(text, path.name)


def load_corpus(corpus_dir: Path | None = None) -> list[dict[str, Any]]:
    directory = corpus_dir or CORPUS_DIR
    documents: list[dict[str, Any]] = []
    if not directory.exists():
        raise FileNotFoundError(f"Corpus directory not found: {directory}")

    for path in sorted(directory.rglob("*")):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        if suffix in {".md", ".markdown"}:
            documents.extend(load_markdown(path))
        elif suffix == ".csv":
            documents.extend(load_csv(path))
        elif suffix == ".pdf":
            documents.extend(load_pdf(path))
    return documents
