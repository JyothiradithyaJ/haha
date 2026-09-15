"""Full-text PDF ingestion and section-aware chunking.

PDFs are fetched only from URLs already supplied by trusted academic source
adapters (for example OpenAlex or arXiv) or explicit Unpaywall/CORE URLs.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Iterable

import httpx

try:
    import fitz  # PyMuPDF
except ImportError:  # pragma: no cover
    fitz = None

try:
    import pdfplumber
except ImportError:  # pragma: no cover
    pdfplumber = None

from app.models.schemas import Paper


TARGET_SECTIONS = (
    "abstract",
    "introduction",
    "methods",
    "methodology",
    "materials and methods",
    "experiments",
    "results",
    "discussion",
    "limitations",
    "conclusion",
)


@dataclass(frozen=True)
class FullTextChunk:
    """A grounded text chunk with section/page provenance."""

    chunk_id: str
    paper_id: str
    section: str
    text: str
    page_start: int | None = None
    page_end: int | None = None
    source_url: str | None = None


def _canonical_section(raw: str) -> str:
    cleaned = re.sub(r"[^a-z0-9 ]+", " ", raw.lower())
    cleaned = " ".join(cleaned.split())
    aliases = {
        "materials methods": "methods",
        "material methods": "methods",
        "methodology": "methods",
        "experimental setup": "experiments",
        "experimental evaluation": "experiments",
        "empirical evaluation": "experiments",
        "findings": "results",
        "results and discussion": "results",
        "discussion conclusions": "discussion",
        "conclusions": "conclusion",
    }
    return aliases.get(cleaned, cleaned)


def _detect_section(line: str) -> str | None:
    """Detect common numbered/un-numbered academic section headings."""
    normalized = re.sub(r"\s+", " ", line.strip())
    normalized = re.sub(r"^[0-9ivxIVX]+(?:\.[0-9ivxIVX]+)*\s*", "", normalized)
    canonical = _canonical_section(normalized)
    if canonical in TARGET_SECTIONS:
        return canonical
    for target in TARGET_SECTIONS:
        if canonical.startswith(target + " ") and len(canonical) < len(target) + 40:
            return target
    return None


def _clean_text(text: str) -> str:
    text = text.replace("\u00ad", "")
    text = re.sub(r"-\n(?=[a-z])", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


class PdfTextParser:
    """Parse a PDF using PyMuPDF, falling back to pdfplumber."""

    def parse(self, pdf_bytes: bytes) -> list[tuple[int, str]]:
        if fitz is not None:
            try:
                with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
                    pages = [(idx + 1, _clean_text(page.get_text("text"))) for idx, page in enumerate(doc)]
                    if any(text for _, text in pages):
                        return pages
            except Exception:
                pass

        if pdfplumber is not None:
            with NamedTemporaryFile(suffix=".pdf") as tmp:
                tmp.write(pdf_bytes)
                tmp.flush()
                with pdfplumber.open(tmp.name) as pdf:
                    return [(idx + 1, _clean_text(page.extract_text() or "")) for idx, page in enumerate(pdf.pages)]

        raise RuntimeError("No PDF parser installed. Install PyMuPDF or pdfplumber.")


class FullTextIngestor:
    """Download, parse and section-chunk open-access full text."""

    def __init__(self, cache_dir: Path | None = None, timeout: float = 30.0, chunk_chars: int = 3500, overlap_chars: int = 350):
        self.cache_dir = cache_dir or Path(".cache/full_text")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
        self.chunk_chars = chunk_chars
        self.overlap_chars = overlap_chars
        self.parser = PdfTextParser()

    def fetch_pdf(self, url: str) -> bytes:
        headers = {
            "User-Agent": "AcademicResearchAgent/1.0 full-text-ingestor",
            "Accept": "application/pdf,application/octet-stream;q=0.9,*/*;q=0.1",
        }
        with httpx.Client(timeout=self.timeout, follow_redirects=True, headers=headers) as client:
            response = client.get(url)
            response.raise_for_status()
            content_type = response.headers.get("content-type", "").lower()
            if "pdf" not in content_type and not response.content.startswith(b"%PDF"):
                raise ValueError(f"URL did not return a PDF: {url}")
            return response.content

    def ingest(self, paper: Paper) -> list[FullTextChunk]:
        if not paper.pdf_url:
            return []
        cache_key = hashlib.sha256(paper.pdf_url.encode("utf-8")).hexdigest()
        cache_path = self.cache_dir / f"{cache_key}.pdf"
        if cache_path.exists():
            pdf_bytes = cache_path.read_bytes()
        else:
            pdf_bytes = self.fetch_pdf(paper.pdf_url)
            cache_path.write_bytes(pdf_bytes)

        pages = self.parser.parse(pdf_bytes)
        sections = self._segment_sections(pages)
        return self._chunk_sections(paper, sections)

    def _segment_sections(self, pages: Iterable[tuple[int, str]]) -> list[tuple[str, int, int, str]]:
        sections: list[tuple[str, int, int, str]] = []
        current_section = "body"
        start_page = 1
        current_pages: list[str] = []

        for page_num, text in pages:
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            for line in lines:
                detected = _detect_section(line)
                if detected:
                    if current_pages:
                        sections.append((current_section, start_page, page_num, " ".join(current_pages)))
                    current_section = detected
                    current_pages = []
                    start_page = page_num
                else:
                    current_pages.append(line)

        if current_pages:
            sections.append((current_section, start_page, start_page, " ".join(current_pages)))

        return sections

    def _chunk_sections(self, paper: Paper, sections: list[tuple[str, int, int, str]]) -> list[FullTextChunk]:
        chunks: list[FullTextChunk] = []
        counter = 1
        for section, page_start, page_end, text in sections:
            text = _clean_text(text)
            if len(text) < 100 or section not in TARGET_SECTIONS:
                continue
            start = 0
            while start < len(text):
                end = min(start + self.chunk_chars, len(text))
                piece = text[start:end].strip()
                if len(piece) >= 100:
                    chunks.append(
                        FullTextChunk(
                            chunk_id=f"{paper.internal_id}-FT-{counter:03d}",
                            paper_id=paper.internal_id,
                            section=section,
                            text=piece,
                            page_start=page_start,
                            page_end=page_end,
                            source_url=paper.pdf_url,
                        )
                    )
                    counter += 1
                if end >= len(text):
                    break
                start = max(end - self.overlap_chars, start + 1)
        return chunks
