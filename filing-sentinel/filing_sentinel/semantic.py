"""Semantic drift analysis — track how filing language changes over time."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from .config import EMBEDDING_MODEL, OPENAI_API_KEY

CACHE_DIR = Path(__file__).parent.parent / ".cache" / "embeddings"


def _cache_key(text: str, model: str) -> str:
    h = hashlib.sha256(f"{model}:{text[:500]}:{len(text)}".encode()).hexdigest()
    return h


def _get_cached(key: str) -> list[float] | None:
    path = CACHE_DIR / f"{key}.json"
    if path.exists():
        return json.loads(path.read_text())
    return None


def _set_cached(key: str, embedding: list[float]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    (CACHE_DIR / f"{key}.json").write_text(json.dumps(embedding))


def get_embedding(text: str) -> list[float]:
    """Get OpenAI embedding for a text chunk, with disk caching."""
    if not OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY is required for semantic drift analysis. "
            "Set it in your environment or .env file."
        )

    key = _cache_key(text, EMBEDDING_MODEL)
    cached = _get_cached(key)
    if cached is not None:
        return cached

    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)

    max_chars = 30_000
    truncated = text[:max_chars] if len(text) > max_chars else text

    resp = client.embeddings.create(model=EMBEDDING_MODEL, input=truncated)
    embedding = resp.data[0].embedding
    _set_cached(key, embedding)
    return embedding


def compute_drift_matrix(
    sections: list[dict],
) -> dict:
    """Compute pairwise cosine similarity between filing sections over time.

    Args:
        sections: list of {"date": str, "text": str} dicts, sorted chronologically.

    Returns dict with:
        - dates: list of filing dates
        - similarity_matrix: 2D list of cosine similarities
        - consecutive_similarities: list of similarity between consecutive filings
        - drift_flags: list of bools where significant drift detected
    """
    if len(sections) < 2:
        return {"error": "Need at least 2 filings to compute drift."}

    embeddings = []
    dates = []
    for sec in sections:
        emb = get_embedding(sec["text"])
        embeddings.append(emb)
        dates.append(sec["date"])

    emb_matrix = np.array(embeddings)
    sim_matrix = cosine_similarity(emb_matrix)

    consecutive = []
    for i in range(1, len(embeddings)):
        consecutive.append(float(sim_matrix[i - 1, i]))

    median_sim = np.median(consecutive) if consecutive else 1.0
    std_sim = np.std(consecutive) if len(consecutive) > 2 else 0.02
    threshold = max(median_sim - 2 * std_sim, 0.85)

    drift_flags = [sim < threshold for sim in consecutive]

    return {
        "dates": dates,
        "similarity_matrix": sim_matrix.tolist(),
        "consecutive_similarities": [round(s, 4) for s in consecutive],
        "drift_flags": drift_flags,
        "threshold": round(float(threshold), 4),
        "has_significant_drift": any(drift_flags),
    }


def summarize_drift(drift_result: dict, section_name: str = "MD&A") -> str:
    """Create a human-readable summary of semantic drift findings."""
    if "error" in drift_result:
        return drift_result["error"]

    dates = drift_result["dates"]
    sims = drift_result["consecutive_similarities"]
    flags = drift_result["drift_flags"]

    lines = [f"**{section_name} Semantic Drift Analysis**\n"]

    if not drift_result["has_significant_drift"]:
        lines.append(
            "No significant language changes detected across filings. "
            "Disclosure language has remained consistent."
        )
    else:
        flagged = [(i, sims[i], dates[i], dates[i + 1])
                    for i in range(len(flags)) if flags[i]]
        lines.append(
            f"**{len(flagged)} significant language shift(s) detected:**\n"
        )
        for _, sim, d1, d2 in flagged:
            drop_pct = (1 - sim) * 100
            lines.append(
                f"- Between **{d1}** and **{d2}**: "
                f"similarity dropped to {sim:.3f} ({drop_pct:.1f}% divergence)"
            )

    lines.append(f"\nAnalyzed {len(dates)} filings from {dates[0]} to {dates[-1]}.")
    lines.append(f"Drift threshold: {drift_result['threshold']:.4f}")

    return "\n".join(lines)
