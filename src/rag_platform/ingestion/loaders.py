"""Raw text extraction from source files.

PDF support exists mainly as an existence proof (PRD FR-004 lists PDF as a
required input type) — mock documents in this practice build are mostly
born-digital Markdown. See enterprise-rag-platform/CLAUDE.md for why this
vendors a tiny pypdf-based extractor instead of depending on tools/pdf_to_md
(that tool is summary-oriented, not raw-text-oriented).
"""

from pathlib import Path

_TEXT_SUFFIXES = {".md", ".txt"}


def load_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in _TEXT_SUFFIXES:
        return path.read_text(encoding="utf-8")
    if suffix == ".pdf":
        return _load_pdf(path)
    raise ValueError(f"Unsupported document type: {suffix}")


def _load_pdf(path: Path) -> str:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    return "\n\n".join(page.extract_text() or "" for page in reader.pages)
