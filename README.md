# VLM Caption Corpus

A literature library for **multi-turn visual tool use in VLMs**. The setting: a model first writes a caption, then either answers directly or calls a crop/zoom tool. It is trained with SFT and then RL (GRPO/RLOO). The question the library serves is how to keep accuracy while calling the tool only when it is needed.

The papers are organised by research problem rather than by date. Each relevant paper gets a structured reading record. Cross-domain work (trajectory-level RL, GRPO variants, credit assignment, advantage estimation, process reward models, latent reasoning, stopping and budgets) is mapped onto the same problem taxonomy.

## Contents (`library/`)

| File | Rows | What it is |
|---|---:|---|
| `papers.jsonl` | 3,453 | Paper index: arXiv id or venue, title, source, themes, `read_priority` (1 = in-domain … 5 = loosely related), mapped problem ids, venue decision when known |
| `readings/*.json` | 226 (growing) | Per-paper reading records for priority 1–2 papers (370 in scope) |
| `problems.jsonl` | 69 | Problem taxonomy: id `P01`–`P69` and category (objective, advantage, credit, decision, coverage, exploration, stopping, trajectory, captioning, perception, evaluation, engineering, forgetting, data, measurement) |
| `crossdomain_map.jsonl` | 327 | Paper → problem mappings with the transferable mechanism and the evidence read; status `proposed` 175 / `checked` 125 / `refuted` 27 |
| `pattern_cards.jsonl` | 91 | Mechanism pattern cards induced from the literature (58 operation-level cards, 14 parent and 19 sub patterns) |
| `repos.jsonl` | 168 | Code repositories: awesome lists (T1), method code (T2a–c), frameworks (T3) |
| `repo_extracts.jsonl` | 136 | Mechanisms located in repository code (`code_locator` = file:lines), with conditions and failure modes |

Paper sources: a venue-paper scan (952), targeted arXiv/GitHub search (247), and three daily arXiv radars (2,254: [HarnessRSI-Daily](https://github.com/CrepuscularIRIS/HarnessRSI-Daily) 1,044, [CUA-Daily](https://github.com/CrepuscularIRIS/CUA-Daily) 840, [Embodied-Harness-Daily](https://github.com/CrepuscularIRIS/Embodied-Harness-Daily) 370).

No full text or PDFs are redistributed. Reading records contain only short verbatim quotes that anchor specific claims (equations, table numbers, stated limitations).

## Reading record

Each record (`readings/<paper_key>.json`) has three blocks. The method follows [ResearchStudio](https://arxiv.org/abs/2607.04439) idea extraction and the Open Scientist reading protocol (read before citing; one claim, one source location).

- **Idea extraction:** `innovation_approach`, `key_step`, `why_non_obvious`, `trigger_condition` ("When X, apply Y to achieve Z"), `contribution_type`, plus domain-stripped `abstract_*` fields for clustering.
- **Operation signatures:** `object`, `information` (what the operation can and cannot see), `operation`, `claimed_effect` (with numbers), `conditions`, `evidence` (kind, location, verbatim quote), `failure_boundary`.
- **Research-question and objective analysis:**
  - `question` and `question_quality`: observed failure, broken assumption, scope, success criterion, why prior work stopped short;
  - `moves`: research moves, as RS ideation patterns and M-coded moves;
  - `objective`: equations, which tokens/turns receive which signal, normalisation, invariance, baseline or potential, degenerate cases at p≈0/1 and in all-correct/all-wrong groups;
  - `evidence_design`, `engineering` (setup, cost, pitfalls, lesson), and `relevance` (problem id + strength 0–3).

Records are tiered `full` or `lite`. Lite records keep the idea fields, 1–2 signatures and relevance. Every quote is checked against the paper text with `deepread/verify_quotes.py`.

## Scripts

- `scripts/fetch_pdfs.py`: resumable arXiv PDF downloader (3 s between requests).
- `deepread/verify_quotes.py`: checks that every `quote` in a record appears in the paper text.
- `scripts/export_public.py`: builds `library/` from the working corpus.

## Caveats

- Reading records report what each paper claims and where. They are not replications.
- `relevance` and the cross-domain maps are hypotheses about transfer, not results.
- Records and mappings were produced with LLM assistance and spot-checked. Errors are possible; issues are welcome.
