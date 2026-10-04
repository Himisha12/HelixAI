"""
Grounded document analysis for the AI Document + Web Researcher tool.

Every answer is computed from the uploaded content (CSV, PDF text, or plain text)
and the user's actual question -- nothing is pre-written. When a real LLM backend
(Ollama / HuggingFace) is available it receives these grounded facts as context;
in local fallback mode the grounded answer is returned directly.
"""
import csv
import io
import re
from typing import Any, Dict, List, Optional, Tuple

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "what", "which", "who", "whom",
    "how", "does", "do", "did", "of", "in", "on", "at", "to", "for", "from", "by", "with",
    "and", "or", "this", "that", "these", "those", "it", "its", "across", "all", "any",
    "has", "have", "had", "me", "my", "our", "your", "tell", "give", "show", "list",
    "please", "based", "uploaded", "document", "file", "csv", "pdf", "according",
    "provided", "attached", "current", "compare", "compared", "web", "there", "can",
    "about", "into", "than", "then", "when", "where", "why", "much", "many", "per",
}

# Question words that map onto common column-name vocabulary
SYNONYMS: Dict[str, List[str]] = {
    "revenue": ["revenue", "amount", "sales", "total", "price", "value", "usd"],
    "sales": ["sales", "revenue", "amount", "total", "usd"],
    "amount": ["amount", "usd", "value", "total"],
    "spend": ["spend", "amount", "cost", "usd"],
    "spending": ["spend", "amount", "cost", "usd"],
    "cost": ["cost", "amount", "price", "spend"],
    "money": ["amount", "usd", "revenue"],
    "order": ["order", "orders", "count", "quantity", "qty"],
    "quantity": ["quantity", "qty", "count", "orders"],
}

CURRENCY_HINTS = {"usd", "amount", "revenue", "price", "cost", "sales", "spend", "value"}
LOW_WORDS = {"lowest", "least", "smallest", "minimum", "min", "worst", "bottom"}


def _stem(token: str) -> str:
    if len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
        return token[:-1]
    return token


def _tokens(text: str) -> List[str]:
    return [
        _stem(t) for t in re.findall(r"[a-z0-9]+", text.lower())
        if t not in STOPWORDS and len(t) > 1
    ]


def _money(value: float, currency: bool) -> str:
    # "\$" keeps Streamlit markdown from switching into LaTeX math mode
    return f"\\${value:,.2f}" if currency else f"{value:,.2f}"


# ---------------------------------------------------------------------------
# Text extraction
# ---------------------------------------------------------------------------
_PDF_STR = r"\(((?:\\.|[^\\()])*)\)"
_PDF_OPS = re.compile(r"(?:%s\s*Tj)|(?:\[((?:\\.|[^\]])*)\]\s*TJ)" % _PDF_STR, re.S)


def _pdf_unescape(s: str) -> str:
    return (
        s.replace("\\(", "(").replace("\\)", ")").replace("\\n", "\n").replace("\\\\", "\\")
    )


def extract_text(content: str) -> Tuple[str, str]:
    """Return (plain_text, source_format). Handles raw (uncompressed) PDF text operators."""
    stripped = content.lstrip()
    if not stripped.startswith("%PDF"):
        return content, "text"

    lines: List[str] = []
    for m in _PDF_OPS.finditer(stripped):
        if m.group(1) is not None:
            lines.append(_pdf_unescape(m.group(1)))
        else:
            lines.append("".join(_pdf_unescape(s) for s in re.findall(_PDF_STR, m.group(2))))
    return "\n".join(line for line in lines), "pdf"


def is_csv(text: str) -> bool:
    lines = [ln for ln in text.strip().splitlines() if ln.strip()]
    if len(lines) < 2 or "," not in lines[0]:
        return False
    try:
        rows = list(csv.reader(io.StringIO("\n".join(lines))))
    except csv.Error:
        return False
    width = len(rows[0])
    if width < 2:
        return False
    consistent = sum(1 for r in rows[1:] if len(r) == width)
    return consistent >= 0.8 * (len(rows) - 1)


# ---------------------------------------------------------------------------
# CSV analysis
# ---------------------------------------------------------------------------
def _num(value: str) -> Optional[float]:
    try:
        return float(value.replace("$", "").replace(",", "").strip())
    except ValueError:
        return None


def analyze_csv(text: str, question: str) -> Dict[str, Any]:
    rows = [r for r in csv.reader(io.StringIO(text.strip())) if any(c.strip() for c in r)]
    headers = [h.strip() for h in rows[0]]
    data = [(r + [""] * len(headers))[: len(headers)] for r in rows[1:]]
    # Clauses about external/web comparison describe the outside world, not the dataset,
    # so they must not create filters or groupings (e.g. "...enterprise cloud benchmarks on the web").
    clauses = [c for c in re.split(r",|;|\?", question) if c.strip()]
    data_clauses = [
        c for c in clauses
        if not re.search(r"\b(web|internet|online|benchmarks?|industry|market)\b", c.lower())
    ] or clauses
    data_question = " ".join(data_clauses)
    q_lower = data_question.lower()
    q_tokens = set(_tokens(data_question))

    numeric_idx = [
        i for i in range(len(headers))
        if any(r[i].strip() for r in data)
        and all(_num(r[i]) is not None for r in data if r[i].strip())
    ]
    categorical_idx = [i for i in range(len(headers)) if i not in numeric_idx]

    def header_tokens(i: int) -> set:
        return {_stem(t) for t in re.findall(r"[a-z0-9]+", headers[i].lower())}

    # 1. Row filters: categorical values literally mentioned in the question (e.g. "completed")
    filters: Dict[str, List[str]] = {}
    for i in categorical_idx:
        distinct = sorted({r[i].strip() for r in data if r[i].strip()})
        matched = [
            v for v in distinct
            if len(v) > 2 and re.search(r"\b%s\b" % re.escape(v.lower()), q_lower)
        ]
        if matched and len(matched) < len(distinct):
            filters[headers[i]] = matched
    filtered = [
        r for r in data
        if all(r[headers.index(col)].strip() in vals for col, vals in filters.items())
    ]

    # 2. Target numeric column: the one the question is about
    def target_score(i: int) -> int:
        ht = header_tokens(i)
        score = 2 * len(ht & q_tokens)
        for qt in q_tokens:
            if any(s in ht for s in SYNONYMS.get(qt, [])):
                score += 1
        return score

    candidates = [i for i in numeric_idx if "id" not in header_tokens(i)] or numeric_idx
    target_idx: Optional[int] = None
    if candidates:
        target_idx = max(candidates, key=lambda i: (target_score(i), -candidates.index(i)))

    # 3. Group-by columns: categorical columns named in the question (e.g. "region").
    #    Date columns are skipped unless the question is about time.
    asks_time = bool(q_tokens & {"date", "day", "daily", "month", "monthly", "week", "year"})

    def is_date_col(i: int) -> bool:
        sample = [r[i].strip() for r in data if r[i].strip()][:5]
        return bool(sample) and all(re.match(r"\d{4}-\d{2}-\d{2}", v) for v in sample)

    group_idx = [
        i for i in categorical_idx
        if header_tokens(i) & q_tokens
        and headers[i] not in filters
        and (asks_time or not is_date_col(i))
    ][:2]

    result: Dict[str, Any] = {
        "format": "csv",
        "rows_total": len(data),
        "rows_analyzed": len(filtered),
        "columns": headers,
        "filters_applied": filters,
        "target_column": headers[target_idx] if target_idx is not None else None,
        "stats": {},
        "group_breakdowns": [],
    }

    if target_idx is None:
        return result

    vals = [v for v in (_num(r[target_idx]) for r in filtered) if v is not None]
    if vals:
        result["stats"] = {
            "count": len(vals),
            "total": round(sum(vals), 2),
            "avg": round(sum(vals) / len(vals), 2),
            "min": min(vals),
            "max": max(vals),
        }

    descending = not (q_tokens & LOW_WORDS)
    for gi in group_idx:
        sums: Dict[str, List[float]] = {}
        for r in filtered:
            v = _num(r[target_idx])
            if v is not None:
                sums.setdefault(r[gi].strip() or "(blank)", []).append(v)
        ranking = sorted(
            ([k, round(sum(v), 2), len(v)] for k, v in sums.items()),
            key=lambda x: x[1],
            reverse=descending,
        )
        result["group_breakdowns"].append({
            "column": headers[gi],
            "order": "highest_first" if descending else "lowest_first",
            "ranking": ranking,
        })
    return result


# ---------------------------------------------------------------------------
# Text / PDF analysis (extractive retrieval per sub-question)
# ---------------------------------------------------------------------------
def _passages(text: str) -> List[str]:
    merged: List[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or set(line) <= set("=-_*#"):
            continue
        if merged and line[0].islower() and not merged[-1].endswith((".", ":", "!", "?")):
            merged[-1] = f"{merged[-1]} {line}"
        else:
            merged.append(line)
    out: List[str] = []
    for p in merged:
        out.extend(s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z])", p) if s.strip())
    return out


def analyze_text(text: str, question: str) -> Dict[str, Any]:
    passages = _passages(text)
    passage_tokens = [set(_tokens(p)) for p in passages]

    parts = [
        p.strip() for p in re.split(r",|;|\?|\band\b", question)
        if _tokens(p) and not re.match(r"\s*(based on|according to|from the|using the)\b", p.lower())
    ]
    if not parts:
        parts = [question]

    answers = []
    for part in parts:
        pt = set(_tokens(part))
        scored = [(len(pt & toks), idx) for idx, toks in enumerate(passage_tokens)]
        best = max((s for s, _ in scored), default=0)
        matches = [passages[idx] for s, idx in scored if s == best and s > 0][:2]
        answers.append({"sub_question": part, "matches": matches, "match_score": best})

    return {
        "format": "text",
        "passages_indexed": len(passages),
        "characters": len(text),
        "answers": answers,
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def analyze_document(content: str, question: str) -> Dict[str, Any]:
    if not content.strip():
        return {"format": "empty"}
    text, source = extract_text(content)
    if source == "pdf" and not text.strip():
        return {
            "format": "pdf_unreadable",
            "note": "No extractable text found (the PDF likely uses compressed or scanned content).",
        }
    if source != "pdf" and is_csv(text):
        return analyze_csv(text, question)
    analysis = analyze_text(text, question)
    analysis["source"] = source
    return analysis


def build_grounded_answer(
    analysis: Dict[str, Any], web_results: List[Dict[str, str]], web_enabled: bool
) -> str:
    """Render the computed analysis as Markdown. Every number/sentence comes from the file."""
    fmt = analysis.get("format")
    out: List[str] = []

    if fmt == "csv":
        target = analysis.get("target_column")
        stats = analysis.get("stats", {})
        currency = bool(target) and any(h in target.lower() for h in CURRENCY_HINTS)
        out.append("### 📊 Answer from your uploaded CSV")
        filt = analysis.get("filters_applied") or {}
        filt_txt = (
            " (filter: " + "; ".join(f"{k} = {', '.join(v)}" for k, v in filt.items()) + ")"
            if filt else ""
        )
        out.append(
            f"**Rows analysed:** {analysis['rows_analyzed']} of {analysis['rows_total']}{filt_txt}\n"
        )
        if stats:
            out.append(f"- **Total `{target}`:** {_money(stats['total'], currency)}")
            out.append(
                f"- **Average:** {_money(stats['avg'], currency)} · "
                f"**Min:** {_money(stats['min'], currency)} · "
                f"**Max:** {_money(stats['max'], currency)}"
            )
        else:
            out.append("- No numeric column could be matched to the question.")
        for gb in analysis.get("group_breakdowns", []):
            ranking = gb["ranking"]
            if not ranking:
                continue
            label = "Highest" if gb["order"] == "highest_first" else "Lowest"
            out.append(f"\n**{gb['column']} ranked by total `{target}`:**\n")
            out.append(f"| {gb['column']} | Total | Rows |\n|---|---:|---:|")
            for name, total, cnt in ranking:
                out.append(f"| {name} | {_money(total, currency)} | {cnt} |")
            out.append(
                f"\n🏆 **{label} {gb['column']}: {ranking[0][0]}** "
                f"({_money(ranking[0][1], currency)})"
            )
    elif fmt == "text":
        src = "PDF" if analysis.get("source") == "pdf" else "document"
        out.append(f"### 📄 Answer from your uploaded {src}")
        for ans in analysis.get("answers", []):
            out.append(f"\n**{ans['sub_question'].strip().capitalize()}**")
            if ans["matches"]:
                for m in ans["matches"]:
                    out.append(f"> {m.replace('$', chr(92) + '$')}")
            else:
                out.append("> _Not found in the uploaded document._")
    elif fmt == "pdf_unreadable":
        out.append(f"⚠️ {analysis['note']}")
    else:
        out.append("⚠️ No document content was provided.")

    if web_enabled:
        out.append("\n---\n**🌐 Web research**")
        if web_results:
            for w in web_results:
                out.append(f"- {w.get('snippet', '').replace('$', chr(92) + '$')}")
        else:
            out.append(
                "- No live web results were returned for this question, "
                "so the answer above is based on the document only."
            )
    return "\n".join(out)
