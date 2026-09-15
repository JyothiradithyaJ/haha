"""Unit tests for academic source adapters with mocked API responses."""
from unittest.mock import patch, MagicMock
from app.sources.openalex import OpenAlexSource, reconstruct_inverted_index
from app.sources.semantic_scholar import SemanticScholarSource
from app.sources.crossref import CrossrefSource, strip_jats_tags
from app.sources.pubmed import PubMedSource
from app.sources.arxiv import ArxivSource
from app.sources.core import CoreSource


def test_reconstruct_inverted_index():
    inv_index = {
        "Defect": [0],
        "detection": [1],
        "is": [2],
        "critical": [3],
    }
    reconstructed = reconstruct_inverted_index(inv_index)
    assert reconstructed == "Defect detection is critical"


def test_strip_jats_tags():
    raw = "<jats:p>We propose a <jats:italic>novel</jats:italic> approach.</jats:p>"
    assert strip_jats_tags(raw) == "We propose a novel approach."


@patch("httpx.Client.get")
def test_openalex_search_parsing(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "results": [
            {
                "id": "https://openalex.org/W123456",
                "title": "Open-Vocabulary Defect Detection",
                "publication_year": 2024,
                "doi": "https://doi.org/10.1016/j.eng.2024.01.002",
                "authorships": [
                    {"author": {"display_name": "Alice Smith"}},
                    {"author": {"display_name": "Bob Jones"}},
                ],
                "abstract_inverted_index": {
                    "An": [0], "accurate": [1], "inspection": [2], "method": [3]
                },
                "cited_by_count": 14,
                "primary_location": {"source": {"display_name": "Engineering Journal"}},
            }
        ]
    }
    mock_get.return_value = mock_resp

    source = OpenAlexSource()
    papers = source.search("defect detection", limit=5)
    assert len(papers) == 1
    p = papers[0]
    assert p.title == "Open-Vocabulary Defect Detection"
    assert p.doi == "10.1016/j.eng.2024.01.002"
    assert p.abstract == "An accurate inspection method"
    assert len(p.authors) == 2


@patch("httpx.Client.get")
def test_semantic_scholar_search_parsing(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "data": [
            {
                "paperId": "s2_987654",
                "title": "Self-Supervised Visual Inspection",
                "year": 2023,
                "venue": "CVPR",
                "authors": [{"name": "Charlie Day"}],
                "abstract": "We evaluate self-supervised learning on industrial textures.",
                "externalIds": {"DOI": "10.1109/CVPR.2023.9999", "ArXiv": "2303.11111"},
                "citationCount": 45,
            }
        ]
    }
    mock_get.return_value = mock_resp

    source = SemanticScholarSource()
    papers = source.search("visual inspection", limit=5)
    assert len(papers) == 1
    p = papers[0]
    assert p.semantic_scholar_id == "s2_987654"
    assert p.doi == "10.1109/cvpr.2023.9999"
    assert p.arxiv_id == "2303.11111"


@patch("httpx.Client.get")
def test_crossref_search_parsing(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "message": {
            "items": [
                {
                    "title": ["Automated Defect Recognition in Radiography"],
                    "author": [{"given": "Dana", "family": "Scully"}],
                    "issued": {"date-parts": [[2022, 5, 10]]},
                    "container-title": ["NDT & E International"],
                    "DOI": "10.1016/j.ndteint.2022.102654",
                    "abstract": "<jats:p>Radiographic inspection of welds.</jats:p>",
                    "is-referenced-by-count": 30,
                }
            ]
        }
    }
    mock_get.return_value = mock_resp

    source = CrossrefSource()
    papers = source.search("radiography weld", limit=5)
    assert len(papers) == 1
    p = papers[0]
    assert p.title == "Automated Defect Recognition in Radiography"
    assert p.year == 2022
    assert p.doi == "10.1016/j.ndteint.2022.102654"
    assert p.abstract == "Radiographic inspection of welds."


@patch("httpx.Client.get")
def test_pubmed_search_and_efetch_parsing(mock_get):
    # ESearch response
    esearch_resp = MagicMock()
    esearch_resp.status_code = 200
    esearch_resp.json.return_value = {
        "esearchresult": {"idlist": ["38123456"]}
    }

    # EFetch XML response
    efetch_resp = MagicMock()
    efetch_resp.status_code = 200
    efetch_resp.text = """<?xml version="1.0"?>
    <PubmedArticleSet>
      <PubmedArticle>
        <MedlineCitation>
          <PMID>38123456</PMID>
          <Article>
            <ArticleTitle>Deep Learning in Medical Stent Defect Detection</ArticleTitle>
            <Journal>
              <Title>Medical Engineering Journal</Title>
              <JournalIssue><PubDate><Year>2023</Year></PubDate></JournalIssue>
            </Journal>
            <Abstract>
              <AbstractText>Automated micro-surface inspection of stents.</AbstractText>
            </Abstract>
            <AuthorList>
              <Author><LastName>Taylor</LastName><ForeName>Evan</ForeName></Author>
            </AuthorList>
          </Article>
        </MedlineCitation>
        <PubmedData>
          <ArticleIdList>
            <ArticleId IdType="doi">10.1016/j.medeng.2023.1001</ArticleId>
          </ArticleIdList>
        </PubmedData>
      </PubmedArticle>
    </PubmedArticleSet>"""

    mock_get.side_effect = [esearch_resp, efetch_resp]

    source = PubMedSource()
    papers = source.search("stent defect", limit=5)
    assert len(papers) == 1
    p = papers[0]
    assert p.pubmed_id == "38123456"
    assert p.title == "Deep Learning in Medical Stent Defect Detection"
    assert p.authors == ["Evan Taylor"]
    assert p.year == 2023


@patch("httpx.Client.get")
def test_arxiv_search_parsing(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = """<?xml version="1.0" encoding="utf-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
      <entry>
        <id>http://arxiv.org/abs/2401.05432v1</id>
        <title>FastAnomaly: Real-time Defect Localization</title>
        <summary>We propose a lightweight feature pyramid network.</summary>
        <published>2024-01-10T12:00:00Z</published>
        <author><name>Frank Miller</name></author>
        <link href="http://arxiv.org/pdf/2401.05432v1" title="pdf" type="application/pdf"/>
      </entry>
    </feed>"""
    mock_get.return_value = mock_resp

    source = ArxivSource()
    papers = source.search("fast defect", limit=5)
    assert len(papers) == 1
    p = papers[0]
    assert p.arxiv_id == "2401.05432"
    assert p.title == "FastAnomaly: Real-time Defect Localization"
    assert p.year == 2024
    assert p.is_open_access is True


def test_core_fallback_without_api_key():
    source = CoreSource()
    # When CORE_API_KEY is unset, search gracefully returns []
    assert source.search("anything") == []
    assert source.health_check() is False

