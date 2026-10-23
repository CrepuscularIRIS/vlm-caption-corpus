"""Download arXiv PDFs for corpus papers lacking local full text (resumable, rate-limited)."""
import json
import logging
import re
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "research" / "pdf"
DELAY_S = 3.0  # arXiv asks for <=1 request / 3 s
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger(__name__)


def norm_id(raw: str) -> str:
    return re.sub(r"v\d+$", "", raw.strip())


def todo_ids() -> list[str]:
    ids: list[str] = []
    for line in open(ROOT / "research/corpus/candidates.jsonl"):
        ids.append(norm_id(json.loads(line)["arxiv"]))
    for line in open(ROOT / "inventory/C_daily_crossdomain.jsonl"):
        row = json.loads(line)
        ft = row.get("fulltext")
        if not (ft and Path(ft).exists()):
            ids.append(norm_id(row["arxiv_id"]))
    return list(dict.fromkeys(i for i in ids if i))


def fetch(aid: str) -> str:
    dest = OUT / f"{aid.replace('/', '_')}.pdf"
    if dest.exists() and dest.stat().st_size > 10_000:
        return "skip"
    req = urllib.request.Request(f"https://arxiv.org/pdf/{aid}", headers={"User-Agent": "vlm-caption-corpus/0.1"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    if not data.startswith(b"%PDF"):
        raise ValueError("not a PDF")
    dest.write_bytes(data)
    return "ok"


def main() -> None:
    ids = todo_ids()
    log.info("todo %d", len(ids))
    failed = []
    for n, aid in enumerate(ids, 1):
        try:
            status = fetch(aid)
        except Exception as e:  # noqa: BLE001 - record and continue
            status = f"fail {e}"
            failed.append(aid)
        log.info("%d/%d %s %s", n, len(ids), aid, status)
        if status != "skip":
            time.sleep(DELAY_S)
    (ROOT / "research/pdf_failed.txt").write_text("\n".join(failed))
    log.info("done, failed %d", len(failed))


if __name__ == "__main__":
    main()
