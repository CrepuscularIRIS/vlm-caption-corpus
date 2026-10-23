"""Export the redacted public literature library into library/.

Public: paper index, per-paper reading records, literature pattern cards, cross-domain
paper→problem maps (mechanism only), repo index and repo extracts (mechanism only).
Removed: full text, local paths, project experiment results, killed designs, idea cards,
project failure checks, advisor material, private repos.

Usage:
    python scripts/export_public.py
"""
import json
import logging
import re
import shutil
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "library"
logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

# Fields that carry project-internal experiments, designs or checks.
DROP_KEY = re.compile(
    r"known_failure|failed_|^I\d\d$|^KF\d$|killed|failure_check|collision|transfer_mapping|mapping_verdicts"
    r"|comparisons|mentor_|^mapping$|refute_reason|^notes$|provenance|^_meta$|^reader$|sha256|locator_local")
# Strings that leak project internals; any string matching is replaced.
PROJECT_MARK = re.compile(
    r"(?<![A-Za-z0-9])(I(0\d|1\d)|KF[1-4])(?![0-9])|PRO_RESPONSE|docs/2\d|v5\d_|v6\b|卡 ?[AB]\b|导师|飞书|mentor"
    r"|cards/idea|(?<![A-Za-z0-9])g[1-4]_|552 ?题|4,?040|(?<![A-Za-z0-9])E1(?![0-9])|库 ?[AB]\b")
LOCAL_PATH = re.compile(r"(/home/[^\s\"',;)]+|/data/[^\s\"',;)]+|/root/[^\s\"',;)]+)")
# Card sets induced from literature; the other sets are this project's own idea cards.
LITERATURE_CARD_SETS = ("forge-v1-K", "pattern-parent", "pattern-sub")
REDACTED = "[redacted: project-internal]"

PAPER_KEYS = ("paper_key", "arxiv", "title", "venue", "year", "source", "also_in", "in_domain",
              "themes", "read_priority", "problems", "decision", "github", "daily_rating", "vlm")
MAP_KEYS = ("problem", "paper_key", "title", "source_domain", "mechanism", "status", "evidence")
REPO_KEYS = ("tier", "full_name", "url", "stars", "language", "related_problems", "linked_paper",
             "priority", "github_description")
EXTRACT_KEYS = ("paper_key", "title", "source_domain", "repo", "repo_commit", "pattern_id",
                "mechanism", "code_locator", "conditions", "failure_modes", "objective",
                "engineering", "problem", "status", "evidence")


def scrub(obj: Any) -> Any:
    """Drop internal keys, strip local paths, redact project-marked strings."""
    if isinstance(obj, dict):
        return {k: scrub(v) for k, v in obj.items() if not DROP_KEY.search(k)}
    if isinstance(obj, list):
        return [scrub(v) for v in obj]
    if obj == "mentor":  # moves.vocab: keep the move id, drop the attribution
        return "M"
    if isinstance(obj, str):
        s = LOCAL_PATH.sub(lambda m: Path(m.group(1)).name, obj)
        return REDACTED if PROJECT_MARK.search(s) else s
    return obj


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in open(path) if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def pick(row: dict, keys: tuple[str, ...]) -> dict:
    return scrub({k: row[k] for k in keys if k in row})


def export() -> dict[str, int]:
    if OUT.exists():
        shutil.rmtree(OUT)
    counts: dict[str, int] = {}

    papers = [pick(r, PAPER_KEYS) for r in load_jsonl(ROOT / "papers/MANIFEST.jsonl")]
    write_jsonl(OUT / "papers.jsonl", papers)
    counts["papers"] = len(papers)

    # Titles describe this project's own experiment findings; publish the taxonomy only.
    problems = [{"id": p["id"], "category": p["category"]}
                for p in load_jsonl(ROOT / "problems/problems.jsonl")]
    write_jsonl(OUT / "problems.jsonl", problems)
    counts["problems"] = len(problems)

    cards = [scrub({k: v for k, v in c.items() if k != "path"})
             for c in load_jsonl(ROOT / "inventory/A_vlm_cards.jsonl") if c["set"] in LITERATURE_CARD_SETS]
    write_jsonl(OUT / "pattern_cards.jsonl", cards)
    counts["pattern_cards"] = len(cards)

    maps = [pick(m, MAP_KEYS) for f in sorted((ROOT / "crossdomain").glob("map_*.jsonl"))
            for m in load_jsonl(f)]
    write_jsonl(OUT / "crossdomain_map.jsonl", maps)
    counts["crossdomain_map"] = len(maps)

    repos = [pick(r, REPO_KEYS) for r in load_jsonl(ROOT / "repos/repos.jsonl")
             if r.get("tier") != "T0" and not r.get("exclude") and not r.get("private")]
    write_jsonl(OUT / "repos.jsonl", repos)
    counts["repos"] = len(repos)

    extracts = [pick(e, EXTRACT_KEYS) for f in sorted((ROOT / "repos/extracted").glob("*.jsonl"))
                for e in load_jsonl(f)]
    write_jsonl(OUT / "repo_extracts.jsonl", extracts)
    counts["repo_extracts"] = len(extracts)

    n = 0
    for f in sorted((ROOT / "readings").glob("*.json")):
        rec = json.loads(f.read_text())
        if not isinstance(rec, dict) or "paper_key" not in rec:
            continue
        dst = OUT / "readings" / f.name
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(json.dumps(scrub(rec), ensure_ascii=False, indent=1))
        n += 1
    counts["readings"] = n
    (OUT / "COUNTS.json").write_text(json.dumps(counts, indent=1))
    return counts


def leak_check() -> list[str]:
    """Return files under library/ that still contain local paths or project marks."""
    bad = []
    for f in OUT.rglob("*"):
        if f.is_file():
            text = f.read_text(errors="ignore").replace(REDACTED, "")
            if LOCAL_PATH.search(text) or PROJECT_MARK.search(text):
                bad.append(str(f.relative_to(ROOT)))
    return bad


if __name__ == "__main__":
    log.info("exported %s", export())
    leaks = leak_check()
    log.info("leak check: %s", leaks or "clean")
