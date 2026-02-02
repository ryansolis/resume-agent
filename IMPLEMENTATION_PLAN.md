# Resume Analyzer Agent — Implementation Plan

**Deadline:** EOD Monday, February 2, 2026  
**Goal:** Lightweight tool that evaluates plain-text resume vs. target role → JSON + human-readable assessment (keyword extraction, matching, missing, score).

---

## 1. Tech Stack

### Primary: Python

| Layer | Choice | Rationale |
|-------|--------|-----------|
| **Runtime** | Python 3.11+ | Fast to build, strong text/NLP ecosystem, easy CLI + API |
| **CLI** | `click` or `typer` | Clean subcommands, help, file inputs |
| **API** | `FastAPI` | Async, auto OpenAPI, minimal boilerplate |
| **NLP / text** | `spaCy` (optional) or regex + `nltk` | Tokenization, stopwords; keep logic simple and deterministic |
| **Synonyms** | Small curated dict or `wordnet` (nltk) | Control over “Python” ↔ “Python 3” etc. |
| **Testing** | `pytest` | Fixtures, parametrize for edge cases |
| **Packaging** | `pyproject.toml` + `uv` or `pip` | Reproducible env, easy `pip install -e .` |

**Why Python:** Quick to implement, easy for reviewers to run, and the problem is keyword/scoring-heavy rather than UI-heavy.

### Alternative Stacks (if you want to showcase other skills)

- **Node.js (TypeScript):** `commander` or `yargs` for CLI, `fastify` or `express` for API; `natural` or custom tokenizer. Good if the team is JS/TS-first.
- **Go:** `cobra` CLI, `gin` or `echo` API; no heavy NLP deps — tokenize by whitespace/punctuation + manual synonym map. Emphasizes speed and single binary.
- **Rust:** `clap` CLI, `axum` API; same idea as Go — minimal deps, fast, great for “show off systems skills.”

**Recommendation:** Stick with **Python** for this challenge unless the job description favors another stack. Ship fast and clear.

---

## 2. High-Level Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Resume (.txt)  │     │  Target (JD or   │     │                 │
│  or raw text   │────▶│  title + keywords)│────▶│  Analyzer Core  │
└─────────────────┘     └──────────────────┘     │  - normalize    │
                                                  │  - extract      │
                                                  │  - match        │
                                                  │  - score        │
                                                  └────────┬────────┘
                                                           │
                        ┌──────────────────────────────────┼──────────────────────────────────┐
                        ▼                                  ▼                                  ▼
                 ┌──────────────┐                  ┌──────────────┐                  ┌──────────────┐
                 │ JSON output  │                  │ Readable     │                  │ CLI / API    │
                 │ (structured) │                  │ summary      │                  │ (interface)  │
                 └──────────────┘                  └──────────────┘                  └──────────────┘
```

- **Single core module:** normalization → extraction → matching → scoring. No ATS; deterministic and explainable.
- **Two interfaces:** CLI (for local runs, demos) and one small API (for “deployed endpoint” requirement).

---

## 3. Step-by-Step Implementation Guide

### Implementation progress

- [x] 1. Initialize repo
- [x] 2. Define inputs/outputs
- [x] 3. Normalization spec (and first tests)
- [x] 4. Write tests first (TDD)
- [x] 5. Extraction pipeline
- [x] 6. Ranking
- [x] 7. Synonym expansion
- [x] 8. Edge-case tests
- [x] 9. Matched / missing
- [x] 10. Scoring (deterministic and explainable)
- [x] 11. Tests (scoring, matching)
- [x] 12. CLI
- [x] 13. API
- [x] 14. Readable summary
- [x] 15. README
- [ ] 16. Deploy
- [x] 17. Final checklist

### Phase 1: Project setup and core data model (Day 1 — ~2–3 hrs)

1. **Initialize repo**
   - `pyproject.toml`: name, deps (click/typer, fastapi, uvicorn, pytest, nltk or spacy optional).
   - Optional: `uv init` or `pip install -e ".[dev]"` with dev deps (pytest, ruff/black).

2. **Define inputs/outputs**
   - **Input:** Resume string (from file or stdin), target string (full JD) OR (role_title, list of keywords).
   - **Output:** Pydantic (or dataclass) model:
     - `top_keywords: list[{term, rank}]`
     - `matched_keywords: list[str]`
     - `missing_keywords: list[str]`
     - `confidence_notes: list[str]`
     - `overall_score: float` (e.g. 0–100) and optional `score_breakdown: dict`.

3. **Normalization spec (and first tests)**
   - Lowercase, strip, collapse whitespace.
   - Define tokenization: split on non-alphanumeric, keep “words” of length ≥ 2 (or configurable).
   - **Edge cases to test now:** “C++”, “Node.js”, “.NET”, “SQL”, “NoSQL” — keep as single tokens via allowlist or regex (e.g. “C++” → token “c++”, “Node.js” → “node.js”).

4. **Write tests first (TDD)**
   - `test_normalize.py`: “C++”, “Node.js”, “.NET”, “SQL”, “NoSQL”, mixed case, extra spaces.
   - `test_synonyms.py`: map “python” ↔ “python 3”, “js” ↔ “javascript” (curated list).

### Phase 2: Keyword extraction and synonym handling (Day 1–2 — ~2–3 hrs)

5. **Extraction pipeline**
   - **Resume:** Normalize → tokenize → remove stopwords (nltk or custom list) → count frequencies → optionally filter by min length / min count.
   - **Target:** Same pipeline; if input is “role title + keyword list”, treat keyword list as pre-extracted (maybe normalized only).

6. **Ranking**
   - Rank by frequency (and optionally inverse doc frequency if you add a second “corpus” later; for MVP frequency is enough).
   - Top N (e.g. 20–30) as `top_keywords` with rank.

7. **Synonym expansion**
   - Small dict: e.g. `{"python": ["python 3", "python3"], "javascript": ["js", "node.js"]}`.
   - When matching, expand both resume and target terms to a canonical set; match if any variant overlaps.
   - **Tests:** “Python” in resume, “Python 3” in JD → matched. “SQL” in JD, “NoSQL” in resume → not matched (unless you explicitly add as non-synonym in notes).

8. **Edge-case tests**
   - SQL vs NoSQL, C++ vs C, Node.js vs JavaScript (synonym), .NET vs C# (synonym if you want).

### Phase 3: Matching and scoring (Day 2 — ~2 hrs)

9. **Matched / missing**
   - **Matched:** Keywords that appear in both resume and target (after normalization and synonym expansion).
   - **Missing:** Target keywords that have no match in resume (again with synonym awareness).

10. **Scoring (deterministic and explainable)**
    - Formula example: `score = (matched_count / max(1, target_keyword_count)) * 100`, optionally capped and rounded.
    - Or: weighted by rank (e.g. top-5 target keywords count more). Keep formula in README.
    - **Confidence notes:** e.g. “Low target keyword count”, “Many missing high-rank terms”, “Strong match on core skills”.

11. **Tests**
    - `test_scoring.py`: known resume + target → expected score range; boundary (0 keywords, 100% match).
    - `test_matching.py`: synonyms, empty inputs, all missing, all matched.

### Phase 4: CLI and API (Day 2–3 — ~2 hrs)

12. **CLI**
    - Subcommands or flags: `analyze --resume path/to/resume.txt --job path/to/jd.txt` and/or `--role "Software Engineer" --keywords "python,api,sql"`.
    - Output: print JSON to stdout and/or write summary to file or stdout (e.g. `--format json|summary|both`).

13. **API**
    - One POST endpoint, e.g. `/analyze`: body `{ "resume_text": "...", "job_description": "..." }` or `{ "resume_text": "...", "role_title": "...", "keywords": ["..."] }`.
    - Response: same JSON structure + optional “readable_summary” string.

14. **Readable summary**
    - From the same result model: a short paragraph or bullet list (e.g. “Top keywords: …; Matched: …; Missing: …; Score: X/100. Confidence: …”).

### Phase 5: Polish and deploy (Day 3 — ~1–2 hrs)

15. **README**
    - How to run locally (clone, venv, `pip install -e .`, `resume-analyzer analyze ...` and/or `uvicorn api.main:app`).
    - Example inputs (snippet of resume + JD) and example JSON + summary output.
    - **Scoring logic:** formula, what “confidence notes” mean, limitations (no semantics, no ATS, plain text only).

16. **Deploy**
    - Simplest: **Railway**, **Render**, or **Fly.io** with Dockerfile or native Python; single `POST /analyze` and health check.
    - Alternative: **Vercel** serverless (single Python function) if you want minimal infra.

17. **Final checklist**
    - Unit tests: normalization, matching, synonyms, scoring, boundary cases (SQL/NoSQL, C++, Node.js, .NET).
    - CLI and API both work locally.
    - Repo link + deployed URL + short “run locally” instructions in submission.

---

## 4. Deliverables Checklist

| Deliverable | Detail |
|-------------|--------|
| **CLI or API** | Both: CLI for local demo, API for “deployed endpoint” |
| **JSON output** | top_keywords, matched_keywords, missing_keywords, confidence_notes, overall_score |
| **Readable summary** | Short human-readable summary (bullets or paragraph) |
| **Unit tests** | Normalization, matching, synonyms, scoring, edge cases (SQL/NoSQL, C++, Node.js, .NET) |
| **README** | How to run, example I/O, scoring logic, limitations |
| **Deployed endpoint** | One URL (e.g. `https://your-app.railway.app/analyze`) |

---

## 5. Scoring Logic (to document in README)

- **Proposed formula:**  
  `score = round((number_of_matched_keywords / max(1, number_of_target_keywords)) * 100)`  
  Optionally: cap at 100, or add small weight for “top-ranked target keywords” so that matching the first 5 matters more.

- **Explainable:** Score = (matched / target_total) * 100. No ML; same inputs → same output.

- **Confidence notes:** e.g. “Few target keywords provided”, “No matches”, “Strong overlap on core terms”.

- **Limitations:** Plain text only; no PDF parsing; no semantic similarity; not an ATS; keyword-based only.

---

## 6. Edge Cases (test matrix)

| Case | Resume | Target | Expected behavior |
|------|--------|--------|--------------------|
| C++ | “C++” | “C++” | Matched |
| C vs C++ | “C” | “C++” | Not matched (or note in docs) |
| Node.js | “Node.js” | “Node.js” / “JavaScript” | Matched (if synonym) |
| .NET | “.NET” | “C#” | Matched if synonym else missing |
| SQL vs NoSQL | “NoSQL” | “SQL” | Not matched |
| Empty | “” | “Python” | Score 0, all missing |
| Case | “Python” | “PYTHON” | Matched (after normalize) |

---

## 7. File Structure (suggested)

```
resume-agent/
├── pyproject.toml
├── README.md
├── IMPLEMENTATION_PLAN.md
├── src/
│   └── resume_analyzer/
│       ├── __init__.py
│       ├── normalize.py    # tokenize, normalize, special tokens (C++, .NET, …)
│       ├── extract.py      # keyword extraction, ranking
│       ├── synonyms.py     # synonym map, expansion
│       ├── match.py        # matched / missing
│       ├── score.py        # score + confidence notes
│       ├── analyzer.py     # orchestration: run pipeline, return result model
│       └── models.py       # Pydantic input/output models
├── cli.py                  # or src/resume_analyzer/cli.py
├── api/
│   └── main.py             # FastAPI app, POST /analyze
├── tests/
│   ├── test_normalize.py
│   ├── test_extract.py
│   ├── test_synonyms.py
│   ├── test_match.py
│   ├── test_score.py
│   └── test_analyzer_e2e.py
├── examples/
│   ├── sample_resume.txt
│   └── sample_jd.txt
└── Dockerfile              # for deploy
```

---

