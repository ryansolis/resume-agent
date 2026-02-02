"""FastAPI app: POST /analyze for resume vs. job analysis."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from resume_analyzer.analyzer import analyze_and_summary

# Limits to prevent abuse and keep responses fast (plain-text resumes/JDs rarely exceed these).
MAX_RESUME_LENGTH = 500_000
MAX_JOB_DESCRIPTION_LENGTH = 200_000
MAX_KEYWORDS_ITEMS = 1_000
MAX_KEYWORD_LENGTH = 200
MAX_ROLE_TITLE_LENGTH = 500

app = FastAPI(
    title="Resume Analyzer API",
    description="Evaluate plain-text resume against job description or keyword list. Returns JSON + readable summary.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    """Request body for POST /analyze. All text fields have max-length limits."""

    resume_text: str = Field(
        ...,
        min_length=1,
        max_length=MAX_RESUME_LENGTH,
        description="Plain text resume (required, non-empty after strip)",
    )
    job_description: str | None = Field(
        None,
        max_length=MAX_JOB_DESCRIPTION_LENGTH,
        description="Full job description text",
    )
    role_title: str | None = Field(
        None,
        max_length=MAX_ROLE_TITLE_LENGTH,
        description="Role title (optional)",
    )
    keywords: list[str] | None = Field(
        None,
        max_length=MAX_KEYWORDS_ITEMS,
        description="Target keywords (optional)",
    )

    @field_validator("resume_text")
    @classmethod
    def resume_text_not_empty_after_strip(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("resume_text is required and cannot be empty or whitespace")
        return v

    @field_validator("keywords")
    @classmethod
    def keywords_item_length(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return v
        for i, k in enumerate(v):
            if len(k) > MAX_KEYWORD_LENGTH:
                raise ValueError(
                    f"keywords[{i}] exceeds max length {MAX_KEYWORD_LENGTH}"
                )
        return v


class AnalyzeResponse(BaseModel):
    """Response: JSON result + readable summary."""

    result: dict = Field(..., description="Structured analysis (top_keywords, matched, missing, score, etc.)")
    readable_summary: str = Field(..., description="Human-readable summary")


@app.get("/")
def root() -> dict:
    """Health / info."""
    return {"service": "resume-analyzer", "version": "1.0.0", "docs": "/docs", "analyze": "POST /analyze"}


@app.get("/health")
def health() -> dict:
    """Health check for deploy."""
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_endpoint(body: AnalyzeRequest) -> AnalyzeResponse:
    """Analyze resume against job description or role + keywords."""
    # Pydantic validates min/max length and empty resume_text; ensure at least one target provided.
    has_target = (
        (body.job_description is not None and body.job_description.strip())
        or (body.keywords and len(body.keywords) > 0)
        or (body.role_title is not None and body.role_title.strip())
    )
    if not has_target:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one of: job_description, role_title, or keywords (non-empty)",
        )
    result, readable_summary = analyze_and_summary(
        resume_text=body.resume_text,
        job_description=body.job_description,
        role_title=body.role_title,
        keywords=body.keywords,
    )
    return AnalyzeResponse(
        result=result.model_dump(),
        readable_summary=readable_summary,
    )
