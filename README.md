# Resume Analyzer Agent

Lightweight tool that evaluates a plain-text resume against a target role by extracting keywords and producing an actionable, human-readable assessment. **Not an ATS clone** — a fast signal generator with deterministic, explainable scoring.

**Deadline:** EOD Monday, February 2, 2026.

---

## Features

- **Inputs:** Resume text (`.txt` or raw), job description text **or** role title + keyword list
- **Outputs:** JSON (top keywords, matched, missing, score, confidence notes) + readable summary
- **Scoring:** Simple, deterministic, explainable (see [Scoring logic](#scoring-logic))
- **Edge handling:** C++, Node.js, .NET, SQL vs NoSQL, Python/Python3, JS/JavaScript (synonyms)

---

## Quick start

### Install and run locally

```bash
# Clone and install (Python 3.11+)
cd resume-agent
pip install -e .

# CLI: analyze resume vs job description
resume-analyzer analyze --resume examples/sample_resume.txt --job examples/sample_jd.txt

# CLI: resume vs role + keywords
resume-analyzer analyze --resume examples/sample_resume.txt --role "Backend Engineer" --keywords "Python,API,PostgreSQL,Docker"

# Output: JSON + summary (default). Use --format json or --format summary for one only.
# Optional: --output result.json to write to file
```

### API (local)

```bash
uvicorn api.main:app --reload
# POST http://localhost:8000/analyze
# GET  http://localhost:8000/docs
```

**Request body (JSON):**

```json
{
  "resume_text": "Plain text resume...",
  "job_description": "Full job description text...",
  "role_title": "Optional role title",
  "keywords": ["python", "api", "sql"]
}
```

Provide at least one of: `job_description`, or `role_title`/`keywords`.

---

## Example output

**CLI (summary):**

```
=== Resume Analysis Summary ===

Overall score: 85/100

Top keywords (resume):
  1. python
  2. api
  3. sql
  ...

Matched (12): api, docker, javascript, node.js, postgresql, python, rest, sql, ...

Missing (2): gcp, kubernetes

Confidence notes:
  • Strong overlap with target keywords.
```

**JSON (excerpt):**

```json
{
  "top_keywords": [{"term": "python", "rank": 1}, ...],
  "matched_keywords": ["api", "docker", "python", "rest", "sql", ...],
  "missing_keywords": ["gcp", "kubernetes"],
  "confidence_notes": ["Strong overlap with target keywords."],
  "overall_score": 85.0,
  "score_breakdown": {
    "matched_count": 12,
    "target_count": 14,
    "formula": "score = (matched_count / max(1, target_count)) * 100, capped at 100"
  }
}
```

---

## Scoring logic

- **Formula:** `score = (matched_count / max(1, target_keyword_count)) * 100`, capped at 100.
- **Interpretation:** Percentage of target keywords that appear in the resume (after normalization and synonym expansion).
- **Deterministic:** Same inputs → same score. No ML; keyword-based only.
- **Confidence notes:** Added when score is very low, very high, or when few target keywords were provided.

### Limitations

- **Plain text only** — no PDF/Word parsing.
- **Keyword-based** — no semantic similarity or embeddings.
- **Not an ATS** — use as a fast signal, not a hiring gate.
- **English-oriented** — stopwords and tokenization tuned for English.

---

## Tests

```bash
pip install -e ".[dev]"
pytest tests -v
```

Covers: normalization (C++, Node.js, .NET, SQL/NoSQL), synonyms (Python/Python3, JS/JavaScript, .NET/C#), matching, scoring, and end-to-end analyzer.

---

## Deploy

A `Dockerfile` is provided for deployment (e.g. Railway, Render, Fly.io).

```bash
docker build -t resume-analyzer .
docker run -p 8000:8000 resume-analyzer
# POST http://localhost:8000/analyze
```

---

## Project layout

```
resume-agent/
├── pyproject.toml
├── README.md
├── resume_analyzer/       # core package
│   ├── normalize.py       # tokenization, special tokens (C++, .NET, etc.)
│   ├── synonyms.py        # Python/Python3, JS/Node.js, .NET/C#, etc.
│   ├── extract.py         # keyword extraction and ranking
│   ├── match.py           # matched/missing (synonym-aware)
│   ├── score.py           # deterministic score + confidence notes
│   ├── analyzer.py        # orchestration
│   ├── models.py          # Pydantic I/O + readable summary
│   └── cli.py             # Typer CLI
├── api/
│   └── main.py            # FastAPI POST /analyze
├── tests/
├── examples/
│   ├── sample_resume.txt
│   └── sample_jd.txt
└── Dockerfile
```

---

## Submission

- **Repo:** [your-repo-link]
- **Deployed endpoint:** `POST https://your-app.up.railway.app/analyze` (or equivalent)
- **Run locally:** `pip install -e .` then `resume-analyzer analyze -r examples/sample_resume.txt -j examples/sample_jd.txt`
