"""Check that every quote in deepread signature records appears in the paper's full text.

Usage:
    python deepread/verify_quotes.py <records.jsonl or dir of *.json> <fulltext_dir>

The full-text directory must hold ``<paper_key>.txt`` (pdftotext output). Quotes are
matched after normalising whitespace, ligatures, hyphenated line breaks and case.
A quote that fails exact matching is accepted as fuzzy if a window of the text has
a SequenceMatcher ratio >= 0.9.
"""
from __future__ import annotations

import difflib
import json
import re
import sys
from pathlib import Path
from typing import Iterator

LIGATURES = {"ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬃ": "ffi", "ﬄ": "ffl"}
FUZZY_THRESHOLD = 0.9


def normalise(text: str) -> str:
    """Lower-case, undo ligatures and line-break hyphenation, collapse whitespace."""
    for src, dst in LIGATURES.items():
        text = text.replace(src, dst)
    text = re.sub(r"-\s*\n\s*", "", text)
    text = text.replace("’", "'").replace("‘", "'")
    text = text.replace("“", '"').replace("”", '"').replace("−", "-")
    return re.sub(r"\s+", " ", text).strip().lower()


def iter_quotes(record: object, path: str = "") -> Iterator[tuple[str, str]]:
    """Yield (field_path, quote) for every non-empty ``quote`` key at any depth."""
    if isinstance(record, dict):
        for k, v in record.items():
            sub = f"{path}.{k}" if path else k
            if k == "quote" and isinstance(v, str) and v.strip():
                yield path, v
            else:
                yield from iter_quotes(v, sub)
    elif isinstance(record, list):
        for i, v in enumerate(record):
            yield from iter_quotes(v, f"{path}[{i}]")


def fuzzy_found(quote: str, text: str) -> bool:
    """Slide a quote-sized window over candidate anchors and test similarity."""
    anchor = quote[:20]
    starts = [m.start() for m in re.finditer(re.escape(anchor), text)] or range(0, max(1, len(text) - len(quote)), max(1, len(quote) // 2))
    for start in starts:
        window = text[start : start + len(quote) + 10]
        if difflib.SequenceMatcher(None, quote, window).ratio() >= FUZZY_THRESHOLD:
            return True
    return False


def safe_name(paper_key: str) -> str:
    """File stem for a paper key: ``litscan:abc`` -> ``litscan_abc``."""
    return paper_key.replace("/", "_").replace(":", "_")


def load_records(path: Path) -> list[dict]:
    if path.is_dir():
        return [json.loads(p.read_text()) for p in sorted(path.glob("*.json"))]
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def main() -> int:
    records_path, text_dir = Path(sys.argv[1]), Path(sys.argv[2])
    total = exact = fuzzy = 0
    failures: list[str] = []
    for rec in load_records(records_path):
        key = rec.get("paper_key")
        if not key:
            continue
        text_file = text_dir / f"{safe_name(key)}.txt"
        if not text_file.exists():
            failures.append(f"{key}: no full text at {text_file}")
            continue
        text = normalise(text_file.read_text(errors="ignore"))
        for field, quote in iter_quotes(rec):
            if "review" in field:  # quotes from OpenReview, not from the paper
                continue
            total += 1
            q = normalise(quote)
            if q and q in text:
                exact += 1
            elif q and fuzzy_found(q, text):
                fuzzy += 1
            else:
                failures.append(f"{key} [{field}]: {quote[:100]!r}")
    print(f"quotes={total} exact={exact} fuzzy={fuzzy} missing={total - exact - fuzzy}")
    for line in failures:
        print("MISSING", line)
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
