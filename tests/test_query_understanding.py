from app.agent.query_understanding import QueryUnderstandingService


def test_literal_bug_query_uses_ai_and_ml_not_instruction_words(monkeypatch):
    service = QueryUnderstandingService()
    monkeypatch.setattr(service.client, "generate_json", lambda **_: {"entities": ["AI", "ML"], "comparative": True, "output_format": "comparison_table"})
    result, instructions, cleaned = service.understand("What is AI and how is it different about ML. Provide me a table of disctinction")
    assert result.entities == ["AI", "ML"]
    assert result.comparative is True
    assert result.output_format == "comparison_table"
    assert "table" not in [e.lower() for e in result.entities]
    assert "distinction" not in [e.lower() for e in result.entities]
    assert instructions
    assert "table" in " ".join(instructions).lower()
    assert "ai" in cleaned.lower() and "ml" in cleaned.lower()


def test_failed_llm_does_not_use_raw_sentence_as_query(monkeypatch):
    service = QueryUnderstandingService(max_retries=0)
    monkeypatch.setattr(service.client, "generate_json", lambda **_: {"entities": []})
    result, _, cleaned = service.understand("Explain AI and ML and provide a table")
    assert result.entities == ["AI", "ML"]
    assert "table" not in cleaned.lower()
