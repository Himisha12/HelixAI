"""Tests proving document answers are computed from the uploaded file, not canned text."""
from pathlib import Path

from app.services.document_analyzer import analyze_document, build_grounded_answer

ASSETS = Path(__file__).resolve().parents[1] / "demo_assets"
CSV = (ASSETS / "sales_q3_report.csv").read_text()
PDF = (ASSETS / "ai_architecture_spec.pdf").read_bytes().decode("utf-8", errors="ignore")


def test_csv_filters_completed_and_ranks_region() -> None:
    q = (
        "What is the total sales revenue across all completed orders, which region has the "
        "highest revenue, and how does this compare with enterprise cloud benchmarks on the web?"
    )
    a = analyze_document(CSV, q)
    assert a["filters_applied"] == {"status": ["Completed"]}  # web clause must not filter
    assert a["stats"]["total"] == 117000.5  # pending order excluded
    region = a["group_breakdowns"][0]
    assert region["column"] == "region"
    assert region["ranking"][0][:2] == ["Europe", 46600.5]


def test_csv_answer_changes_with_question() -> None:
    a = analyze_document(CSV, "Which product_category has the lowest amount?")
    assert a["stats"]["total"] == 121500.5  # no filter -> all rows
    assert a["group_breakdowns"][0]["ranking"][0][0] == "Security Shield"


def test_different_csv_gives_different_answer() -> None:
    other = "city,units\nPune,5\nDelhi,9\nPune,7\n"
    a = analyze_document(other, "Which city sold the most units?")
    assert a["stats"]["total"] == 21
    assert a["group_breakdowns"][0]["ranking"][0][:2] == ["Pune", 12]


def test_pdf_answers_come_from_pdf_text() -> None:
    q = "What are the sliding window rate limits, supported open LLMs, and role access controls?"
    answer = build_grounded_answer(analyze_document(PDF, q), [], False)
    assert "20 Requests Per Minute" in answer
    assert "Llama 3 8B" in answer
    assert "Total" not in answer  # no CSV content leaking into a PDF answer


def test_missing_facts_are_reported_not_invented() -> None:
    answer = build_grounded_answer(
        analyze_document("Our team ships data pipelines.", "What is the GPU budget?"), [], True
    )
    assert "Not found in the uploaded document" in answer
    assert "No live web results" in answer
