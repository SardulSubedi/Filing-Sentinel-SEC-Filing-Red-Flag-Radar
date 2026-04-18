"""LLM agent for synthesizing a Red Flag Report from all anomaly signals."""

from __future__ import annotations

from .config import CHAT_MODEL, OPENAI_API_KEY

SYSTEM_PROMPT = """\
You are Filing Sentinel, an expert forensic accounting analyst. You receive
anomaly detection signals from SEC filings and synthesize them into a concise,
actionable Red Flag Report.

Your report must:
1. Lead with an overall RISK RATING (Low / Moderate / Elevated / High / Critical)
2. Summarize the key findings in 3-5 bullet points
3. Provide detailed analysis for each signal type (Benford's Law, Semantic Drift,
   Footnote/Disclosure changes)
4. End with a "What to Watch" section — forward-looking items an analyst should monitor
5. Be written for a CFA-level audience — precise, quantitative, no fluff

Use markdown formatting. Be direct and evidence-driven. If signals are benign,
say so clearly — do not manufacture risk where none exists."""


def _format_benford_summary(benford: dict) -> str:
    if "error" in benford:
        return f"Benford's Law: {benford['error']}"

    lines = [
        f"Benford's Law Analysis ({benford['n_samples']:,} data points):",
        f"  - MAD: {benford['mad']} ({benford['conformity']})",
        f"  - Chi-squared: {benford['chi2_statistic']} (p={benford['chi2_p_value']})",
        f"  - Flagged: {benford['flagged']}",
        "",
        "  Digit-level deviations:",
    ]
    for d in benford.get("digits", []):
        flag = " <<<" if abs(d["deviation_pct"]) > 3 else ""
        lines.append(
            f"    Digit {d['digit']}: observed {d['observed_pct']}% "
            f"vs expected {d['expected_pct']}% (Δ{d['deviation_pct']:+.2f}%){flag}"
        )
    return "\n".join(lines)


def _format_drift_summary(drift: dict, section: str) -> str:
    if "error" in drift:
        return f"{section} Drift: {drift['error']}"

    lines = [
        f"{section} Semantic Drift ({len(drift['dates'])} filings, "
        f"{drift['dates'][0]} to {drift['dates'][-1]}):",
        f"  - Significant drift detected: {drift['has_significant_drift']}",
        f"  - Threshold: {drift['threshold']}",
        "",
        "  Consecutive similarities:",
    ]
    for i, sim in enumerate(drift.get("consecutive_similarities", [])):
        flag = " <<< FLAGGED" if drift["drift_flags"][i] else ""
        lines.append(
            f"    {drift['dates'][i]} → {drift['dates'][i+1]}: {sim}{flag}"
        )
    return "\n".join(lines)


def synthesize_report(
    ticker: str,
    company_name: str,
    benford_results: dict,
    mda_drift: dict | None = None,
    risk_drift: dict | None = None,
) -> str:
    """Generate a Red Flag Report using GPT, or a structured fallback if no API key."""
    benford_text = _format_benford_summary(benford_results)
    mda_text = _format_drift_summary(mda_drift, "MD&A") if mda_drift else "MD&A drift: not analyzed"
    risk_text = _format_drift_summary(risk_drift, "Risk Factors") if risk_drift else "Risk Factors drift: not analyzed"

    user_prompt = f"""\
Generate a Red Flag Report for **{ticker}** ({company_name}).

=== ANOMALY SIGNALS ===

{benford_text}

{mda_text}

{risk_text}

=== END SIGNALS ===

Synthesize these signals into a professional Red Flag Report following the format
in your system prompt."""

    if not OPENAI_API_KEY:
        return _fallback_report(ticker, company_name, benford_results, mda_drift, risk_drift)

    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

    resp = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=2000,
    )
    return resp.choices[0].message.content


def _fallback_report(
    ticker: str,
    company_name: str,
    benford: dict,
    mda_drift: dict | None,
    risk_drift: dict | None,
) -> str:
    """Deterministic report when no OpenAI key is available."""
    # Assess overall risk
    risk_signals = 0
    if benford.get("flagged"):
        risk_signals += 2
    if mda_drift and mda_drift.get("has_significant_drift"):
        risk_signals += 1
    if risk_drift and risk_drift.get("has_significant_drift"):
        risk_signals += 1

    levels = {0: "Low", 1: "Moderate", 2: "Elevated", 3: "High", 4: "Critical"}
    risk_level = levels.get(min(risk_signals, 4), "Moderate")

    lines = [
        f"# Red Flag Report: {ticker} ({company_name})",
        "",
        f"## Overall Risk Rating: **{risk_level}**",
        "",
        "---",
        "",
        "## Benford's Law Analysis",
        "",
    ]

    if "error" in benford:
        lines.append(f"*{benford['error']}*")
    else:
        lines.append(f"- **{benford['n_samples']:,}** financial data points analyzed")
        lines.append(f"- Mean Absolute Deviation: **{benford['mad']}** — {benford['conformity']}")
        lines.append(f"- Chi-squared statistic: {benford['chi2_statistic']} (p = {benford['chi2_p_value']})")
        if benford["flagged"]:
            lines.append("")
            lines.append("**Warning:** Distribution deviates significantly from Benford's Law. "
                         "This warrants closer inspection of reported figures.")
            worst = max(benford["digits"], key=lambda d: abs(d["deviation_pct"]))
            lines.append(f"- Largest deviation at digit **{worst['digit']}**: "
                         f"{worst['observed_pct']}% observed vs {worst['expected_pct']}% expected")
        else:
            lines.append("")
            lines.append("Financial figures conform to Benford's Law. "
                         "No statistical red flags in the reported numbers.")

    lines.extend(["", "## Semantic Drift Analysis", ""])

    for label, drift in [("MD&A", mda_drift), ("Risk Factors", risk_drift)]:
        if drift is None:
            lines.append(f"**{label}:** Not analyzed (requires OpenAI API key)")
            continue
        if "error" in drift:
            lines.append(f"**{label}:** {drift['error']}")
            continue

        n = len(drift["dates"])
        lines.append(f"**{label}** — {n} filings from {drift['dates'][0]} to {drift['dates'][-1]}")
        if drift["has_significant_drift"]:
            flagged_pairs = [
                (drift["dates"][i], drift["dates"][i + 1], drift["consecutive_similarities"][i])
                for i in range(len(drift["drift_flags"])) if drift["drift_flags"][i]
            ]
            for d1, d2, sim in flagged_pairs:
                lines.append(f"- **Significant shift** between {d1} and {d2} "
                             f"(similarity: {sim:.4f})")
        else:
            lines.append("- No significant language changes detected.")
        lines.append("")

    lines.extend([
        "---",
        "",
        "## What to Watch",
        "",
        "- Monitor next quarterly filing for continuation or reversal of flagged signals",
        "- Cross-reference any Benford's deviations with known restatements or accounting changes",
        "- Review flagged semantic shifts against earnings call commentary for consistency",
        "",
        "---",
        "*Report generated by Filing Sentinel. Set OPENAI_API_KEY for AI-powered analysis.*",
    ])

    return "\n".join(lines)
