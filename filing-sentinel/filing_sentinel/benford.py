"""Benford's Law analysis for detecting anomalies in financial figures."""

import math
from collections import Counter

import numpy as np
from scipy import stats


def expected_distribution() -> dict[int, float]:
    """Theoretical Benford's Law first-digit probabilities."""
    return {d: math.log10(1 + 1 / d) for d in range(1, 10)}


def leading_digit(n: float) -> int | None:
    """Extract the first non-zero digit from a number."""
    n = abs(n)
    if n == 0:
        return None
    s = f"{n:.10e}"
    for ch in s:
        if ch.isdigit() and ch != "0":
            return int(ch)
    return None


def actual_distribution(values: list[float]) -> dict[int, float]:
    """Compute the observed first-digit frequency distribution."""
    digits = [leading_digit(v) for v in values]
    digits = [d for d in digits if d is not None]
    if not digits:
        return {d: 0.0 for d in range(1, 10)}
    counts = Counter(digits)
    total = len(digits)
    return {d: counts.get(d, 0) / total for d in range(1, 10)}


def chi_squared_test(
    observed_freq: dict[int, float], n_samples: int
) -> tuple[float, float]:
    """Chi-squared goodness-of-fit test against Benford's distribution.

    Returns (chi2_statistic, p_value).
    """
    expected = expected_distribution()
    obs = np.array([observed_freq.get(d, 0) * n_samples for d in range(1, 10)])
    exp = np.array([expected[d] * n_samples for d in range(1, 10)])

    # Avoid division by zero
    mask = exp > 0
    chi2 = np.sum((obs[mask] - exp[mask]) ** 2 / exp[mask])
    p_value = 1 - stats.chi2.cdf(chi2, df=8)
    return float(chi2), float(p_value)


def mean_absolute_deviation(observed_freq: dict[int, float]) -> float:
    """MAD statistic — average absolute deviation from Benford's expected.

    Thresholds (Nigrini, 2012):
      MAD < 0.006  → close conformity
      MAD < 0.012  → acceptable conformity
      MAD < 0.015  → marginally acceptable
      MAD >= 0.015 → nonconformity (flag)
    """
    expected = expected_distribution()
    deviations = [abs(observed_freq.get(d, 0) - expected[d]) for d in range(1, 10)]
    return sum(deviations) / 9


def conformity_label(mad: float) -> str:
    if mad < 0.006:
        return "Close conformity"
    elif mad < 0.012:
        return "Acceptable conformity"
    elif mad < 0.015:
        return "Marginally acceptable"
    else:
        return "Nonconformity — potential anomaly"


def analyze(values: list[float]) -> dict:
    """Run full Benford's Law analysis on a set of financial values.

    Returns a dict with observed/expected distributions, test stats, and verdict.
    """
    if len(values) < 50:
        return {
            "error": f"Insufficient data ({len(values)} values). Need at least 50.",
            "n_samples": len(values),
        }

    observed = actual_distribution(values)
    expected = expected_distribution()
    chi2, p_value = chi_squared_test(observed, len(values))
    mad = mean_absolute_deviation(observed)

    digit_details = []
    for d in range(1, 10):
        obs_pct = observed[d] * 100
        exp_pct = expected[d] * 100
        deviation = obs_pct - exp_pct
        digit_details.append({
            "digit": d,
            "observed_pct": round(obs_pct, 2),
            "expected_pct": round(exp_pct, 2),
            "deviation_pct": round(deviation, 2),
        })

    return {
        "n_samples": len(values),
        "digits": digit_details,
        "chi2_statistic": round(chi2, 4),
        "chi2_p_value": round(p_value, 6),
        "mad": round(mad, 6),
        "conformity": conformity_label(mad),
        "flagged": mad >= 0.015 or p_value < 0.05,
    }
