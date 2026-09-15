from app.evidence.full_text import FullTextIngestor, PdfTextParser, _detect_section
from app.models.schemas import Paper


def test_detect_common_sections():
    assert _detect_section("2. Methods") == "methods"
    assert _detect_section("3 Results") == "results"
    assert _detect_section("5. Limitations") == "limitations"


def test_chunk_sections_only_target_sections():
    ingestor = FullTextIngestor(chunk_chars=120, overlap_chars=20)
    sections = [
        ("body", 1, 1, "ignored " * 100),
        ("methods", 2, 3, "The method uses a controlled protocol and a baseline comparison. " * 8),
        ("results", 4, 5, "Results show improved accuracy under the reported evaluation setting. " * 8),
    ]
    paper = Paper(internal_id="P01", title="Test")
    chunks = ingestor._chunk_sections(sections, paper)
    assert chunks
    assert {c.section for c in chunks} == {"methods", "results"}
    assert all(c.paper_id == "P01" for c in chunks)
    assert all(c.source_url is None for c in chunks)


def test_pdf_parser_requires_available_backend(monkeypatch):
    parser = PdfTextParser()
    monkeypatch.setattr("app.evidence.full_text.fitz", None)
    monkeypatch.setattr("app.evidence.full_text.pdfplumber", None)
    try:
        parser.parse(b"not a pdf")
    except RuntimeError as exc:
        assert "PDF parser" in str(exc)
    else:
        raise AssertionError("Expected missing-parser RuntimeError")
