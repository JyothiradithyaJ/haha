"""Full-text PDF ingestion and section-aware chunking."""
from __future__ import annotations
import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Iterable
import httpx
from app.config import config
from app.models.schemas import Paper
try:
    import fitz
except ImportError:
    fitz = None
try:
    import pdfplumber
except ImportError:
    pdfplumber = None

TARGET_SECTIONS = ("abstract", "introduction", "methods", "methodology", "materials and methods", "experiments", "results", "discussion", "limitations", "conclusion")

@dataclass(frozen=True)
class FullTextChunk:
    chunk_id: str
    paper_id: str
    section: str
    text: str
    page_start: int | None = None
    page_end: int | None = None
    source_url: str | None = None

def _canonical_section(raw: str) -> str:
    cleaned = " ".join(re.sub(r"[^a-z0-9 ]+", " ", raw.lower()).split())
    return {"materials methods":"methods", "material methods":"methods", "methodology":"methods", "experimental setup":"experiments", "experimental evaluation":"experiments", "empirical evaluation":"experiments", "findings":"results", "results and discussion":"results", "discussion conclusions":"discussion", "conclusions":"conclusion"}.get(cleaned, cleaned)

def _detect_section(line: str) -> str | None:
    normalized = re.sub(r"\s+", " ", line.strip())
    normalized = re.sub(r"^[0-9ivxIVX]+(?:\.[0-9ivxIVX]+)*\s*", "", normalized)
    canonical = _canonical_section(normalized)
    if canonical in TARGET_SECTIONS:
        return canonical
    return next((target for target in TARGET_SECTIONS if canonical.startswith(target + " ") and len(canonical) < len(target) + 40), None)

def _clean_text(text: str) -> str:
    text = text.replace("\u00ad", "")
    text = re.sub(r"-\n(?=[a-z])", "", text)
    return re.sub(r"\s+", " ", text).strip()

class PdfTextParser:
    def parse(self, pdf_bytes: bytes) -> list[tuple[int, str]]:
        if fitz is not None:
            try:
                with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
                    pages = [(i + 1, _clean_text(p.get_text("text"))) for i, p in enumerate(doc)]
                    if any(text for _, text in pages):
                        return pages
            except Exception:
                pass
        if pdfplumber is not None:
            with NamedTemporaryFile(suffix=".pdf") as tmp:
                tmp.write(pdf_bytes); tmp.flush()
                with pdfplumber.open(tmp.name) as pdf:
                    return [(i + 1, _clean_text(p.extract_text() or "")) for i, p in enumerate(pdf.pages)]
        raise RuntimeError("No PDF parser installed. Install PyMuPDF or pdfplumber.")

class FullTextIngestor:
    """Resolve, download, parse and section-chunk open-access full text."""
    def __init__(self, cache_dir: Path | None = None, timeout: float | None = None, chunk_chars: int | None = None, overlap_chars: int | None = None):
        self.cache_dir = cache_dir or config.FULL_TEXT_CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout or config.FULL_TEXT_TIMEOUT_SECONDS
        self.chunk_chars = chunk_chars or config.FULL_TEXT_CHUNK_CHARS
        self.overlap_chars = overlap_chars or config.FULL_TEXT_OVERLAP_CHARS
        self.parser = PdfTextParser()

    def resolve_pdf_url(self, paper: Paper) -> tuple[str | None, str | None]:
        """Prefer OpenAlex/CORE/arXiv supplied links; use Unpaywall only when absent."""
        if paper.pdf_url:
            return paper.pdf_url, paper.sources[0] if paper.sources else "source_adapter"
        if not paper.doi:
            return None, None
        try:
            email = config.OPENALEX_EMAIL or "academic-research-agent@example.com"
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.get(f"https://api.unpaywall.org/v2/{paper.doi}", params={"email": email})
                if response.status_code == 200:
                    location = response.json().get("best_oa_location") or {}
                    url = location.get("url_for_pdf") or location.get("url")
                    if url:
                        return url, "unpaywall"
        except Exception:
            pass
        return None, None

    def fetch_pdf(self, url: str) -> bytes:
        headers = {"User-Agent": "AcademicResearchAgent/1.0 full-text-ingestor", "Accept": "application/pdf,application/octet-stream;q=0.9,*/*;q=0.1"}
        with httpx.Client(timeout=self.timeout, follow_redirects=True, headers=headers) as client:
            response = client.get(url); response.raise_for_status()
            if "pdf" not in response.headers.get("content-type", "").lower() and not response.content.startswith(b"%PDF"):
                raise ValueError(f"URL did not return a PDF: {url}")
            return response.content

    def ingest(self, paper: Paper) -> list[FullTextChunk]:
        pdf_url, source = self.resolve_pdf_url(paper)
        if not pdf_url:
            paper.full_text_status = "unavailable"
            return []
        paper.pdf_url, paper.full_text_source = pdf_url, source
        cache_path = self.cache_dir / f"{hashlib.sha256(pdf_url.encode()).hexdigest()}.pdf"
        pdf_bytes = cache_path.read_bytes() if cache_path.exists() else self.fetch_pdf(pdf_url)
        if not cache_path.exists(): cache_path.write_bytes(pdf_bytes)
        chunks = self._chunk_sections(self._segment_sections(self.parser.parse(pdf_bytes)), paper)
        paper.full_text_status = "available" if chunks else "failed"
        return chunks

    def _segment_sections(self, pages: Iterable[tuple[int, str]]) -> list[tuple[str, int, int, str]]:
        sections, current, start, lines = [], "body", 1, []
        for page_num, text in pages:
            for line in [x.strip() for x in text.splitlines() if x.strip()]:
                detected = _detect_section(line)
                if detected:
                    if lines: sections.append((current, start, page_num, " ".join(lines)))
                    current, start, lines = detected, page_num, []
                else: lines.append(line)
        if lines: sections.append((current, start, start, " ".join(lines)))
        return sections

    def _chunk_sections(self, sections: list[tuple[str, int, int, str]], paper: Paper) -> list[FullTextChunk]:
        chunks, counter = [], 1
        for section, page_start, page_end, text in sections:
            text = _clean_text(text)
            if len(text) < 100 or section not in TARGET_SECTIONS: continue
            start = 0
            while start < len(text):
                end = min(start + self.chunk_chars, len(text)); piece = text[start:end].strip()
                if len(piece) >= 100:
                    chunks.append(FullTextChunk(f"{paper.internal_id}-FT-{counter:03d}", paper.internal_id, section, piece, page_start, page_end, paper.pdf_url)); counter += 1
                if end >= len(text): break
                start = max(end - self.overlap_chars, start + 1)
        return chunks
