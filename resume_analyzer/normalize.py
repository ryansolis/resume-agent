"""Text normalization and tokenization with special handling for tech terms (C++, Node.js, .NET, etc.)."""

import re
# Tokens that must be preserved as single units (lowercase for matching).
# Order matters: longer patterns first (e.g. "node.js" before "node").
SPECIAL_TOKENS = (
    "c++",
    "c#",
    ".net",
    "node.js",
    "nodejs",
    "nosql",
    "sql",
    "html",
    "css",
    "json",
    "xml",
    "api",
    "aws",
    "gcp",
    "rest",
    "graphql",
    "typescript",
    "javascript",
    "python",
    "python3",
    "react",
    "angular",
    "vue",
    "kubernetes",
    "docker",
    "terraform",
    "postgresql",
    "mongodb",
    "redis",
    "kafka",
    "elasticsearch",
    "machine-learning",
    "machinelearning",
)

# Regex to find special tokens in text (case-insensitive).
# Escape dots and plus for regex.
def _special_pattern() -> re.Pattern[str]:
    parts = []
    for t in SPECIAL_TOKENS:
        escaped = re.escape(t).replace(r"\.", r"\.").replace(r"\+", r"\+")
        parts.append(escaped)
    return re.compile("|".join(f"({p})" for p in parts), re.IGNORECASE)


_SPECIAL_RE = _special_pattern()

# Minimum token length (after normalization) to keep. Single chars are usually noise.
MIN_TOKEN_LEN = 2

# Common stopwords (lowercase). Keep list small; focus on obvious noise.
STOPWORDS = frozenset({
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with",
    "by", "from", "as", "is", "was", "are", "were", "been", "be", "have", "has", "had",
    "do", "does", "did", "will", "would", "could", "should", "may", "might", "must",
    "can", "this", "that", "these", "those", "it", "its", "i", "me", "my", "we", "our", "use",
    "you", "your", "he", "she", "they", "them", "their", "what", "which", "who",
    "when", "where", "why", "how", "all", "each", "every", "both", "few", "more",
    "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same",
    "than", "too", "very", "just", "also", "now", "here", "there", "then", "so",
})


def normalize_text(text: str) -> str:
    """Lowercase, strip, collapse whitespace."""
    if not text or not isinstance(text, str):
        return ""
    return " ".join(text.lower().strip().split())


def tokenize(text: str) -> list[str]:
    """
    Tokenize text, preserving special tech tokens (C++, Node.js, .NET, SQL, NoSQL, etc.).
    Returns lowercase tokens; filters by MIN_TOKEN_LEN and stopwords in a separate step.
    """
    if not text:
        return []
    normalized = normalize_text(text)
    if not normalized:
        return []

    tokens: list[str] = []
    last_end = 0
    found_any = False

    for m in _SPECIAL_RE.finditer(normalized):
        found_any = True
        if m.start() > last_end:
            chunk = normalized[last_end : m.start()]
            for word in re.split(r"[^a-z0-9.+#\-]+", chunk):
                w = word.strip(".-")
                if w and len(w) >= MIN_TOKEN_LEN and w not in STOPWORDS:
                    tokens.append(w)
        special = m.group(0).lower().strip()
        if special == "nodejs":
            special = "node.js"
        elif special == "python3":
            special = "python"
        tokens.append(special)
        last_end = m.end()

    if found_any and last_end < len(normalized):
        chunk = normalized[last_end:]
        for word in re.split(r"[^a-z0-9.+#\-]+", chunk):
            w = word.strip(".-")
            if w and len(w) >= MIN_TOKEN_LEN and w not in STOPWORDS:
                tokens.append(w)

    if not found_any:
        # No special tokens: tokenize whole string.
        for word in re.split(r"[^a-z0-9.+#\-]+", normalized):
            w = word.strip(".-")
            if w and len(w) >= MIN_TOKEN_LEN and w not in STOPWORDS:
                tokens.append(w)

    return tokens


def tokenize_without_stopwords(text: str) -> list[str]:
    """Tokenize and drop stopwords. Does not drop short tokens here (extract does filtering)."""
    raw = tokenize(text)
    return [t for t in raw if t not in STOPWORDS]
