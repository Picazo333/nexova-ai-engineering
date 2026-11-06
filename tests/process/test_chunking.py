"""Chunk boundaries follow the official Nexova documents."""

from collections import Counter
from pathlib import Path

from data.process.rag import CORPUS_FILES, chunk_corpus, corpus_paths

ROOT = Path(__file__).resolve().parents[2]


def test_each_official_file_yields_at_least_three_chunks_and_keeps_every_line():
    chunks = chunk_corpus()
    counts = Counter((chunk.source_file, chunk.language, chunk.source_document) for chunk in chunks)
    assert len(counts) == 8
    for path in corpus_paths():
        source_document, language = CORPUS_FILES[path.name]
        file_chunks = [chunk for chunk in chunks if chunk.source_file == path.name]
        assert len(file_chunks) >= 3
        assert all(chunk.language == language for chunk in file_chunks)
        assert all(chunk.source_document == source_document for chunk in file_chunks)
        assert all(chunk.section.strip() for chunk in file_chunks)
        source_lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        chunk_lines = []
        for chunk in file_chunks:
            assert chunk.text.rstrip()[-1] in ".?:)\""
            chunk_lines.extend(line for line in chunk.text.splitlines() if line.strip())
        assert chunk_lines == source_lines


def test_sla_list_stays_with_its_lead_in_and_the_averages_rule_stays_whole():
    chunks = [chunk for chunk in chunk_corpus() if chunk.source_file == "nexova-hiring-process-sla.en.md"]
    delivery = next(chunk for chunk in chunks if "Committed delivery times" in chunk.text)
    assert "Executive profile" in delivery.text
    assert "Specialized technical profile" in delivery.text
    averages = next(chunk for chunk in chunks if "These times are averages" in chunk.text)
    assert "strict contractual guarantee" in averages.text
    assert averages is not delivery


def test_an_objection_keeps_its_suggested_response():
    chunks = [chunk for chunk in chunk_corpus() if chunk.source_file == "nexova-objection-handling.en.md"]
    price = next(chunk for chunk in chunks if "22% seems expensive" in chunk.text)
    assert "Marcos" in price.text
    assert "6-month replacement" in price.text


def test_needles_in_test_queries_exist_in_exactly_one_chunk():
    import json

    specs = json.loads((ROOT / "data" / "eval" / "test-queries.json").read_text(encoding="utf-8"))["queries"]
    chunks = chunk_corpus()
    assert len(specs) >= 8
    objections = [spec for spec in specs if spec["kind"] == "objection"]
    assert len(objections) >= 2
    covered = {(spec["expected_source_document"], spec["language"]) for spec in specs}
    assert covered == {(source, language) for source, language in CORPUS_FILES.values()}
    for spec in specs:
        matches = [
            chunk
            for chunk in chunks
            if chunk.language == spec["language"]
            and chunk.source_document == spec["expected_source_document"]
            and spec["expected_text_contains"] in chunk.text
        ]
        assert len(matches) == 1, spec["id"]
