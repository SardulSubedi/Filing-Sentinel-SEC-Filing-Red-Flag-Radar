# Filing Sentinel

Filing Sentinel is a **SEC EDGAR anomaly scanner** built for fundamental investors. It pulls **structured XBRL facts** and **recent 10-K/10-Q filings**, then runs:

- **Benford’s Law forensics** (MAD + chi-squared) on reported financial figures
- **Semantic drift detection** (optional) on MD&A and Risk Factors via embeddings
- **Red Flag Report synthesis** (optional) via GPT (with a deterministic fallback)

This project is intended for research and workflow acceleration — **not investment advice**.

---

## What It Does (At a Glance)

| Capability | What you see | API key required? |
|---|---|---|
| **Benford’s Law** | Expected vs observed digit distribution + deviation chart + MAD/χ² stats | No |
| **Semantic Drift** | Similarity timeline + heatmap for MD&A/Risk Factors across filings | Yes (OpenAI) |
| **Red Flag Report** | Downloadable markdown brief with risk rating + evidence summary | Optional |

---

## How It Works (Pipeline)

1. **Ticker → CIK**: Looks up the company’s CIK using the SEC’s ticker mapping.
2. **XBRL facts pull**: Downloads company facts from the SEC XBRL endpoint and flattens all numeric values.
3. **Benford’s analysis**:
   - Extracts leading digits for each numeric value.
   - Computes observed distribution (1–9) vs Benford’s expected distribution.
   - Runs:
     - **MAD** (Mean Absolute Deviation) with Nigrini-style conformity bands.
     - **Chi-squared** goodness-of-fit (p-value) against expected distribution.
4. **Filing list pull**: Fetches recent filing metadata and builds direct document URLs for the primary filing HTML.
5. **(Optional) Text extraction + drift**:
   - Downloads 10-K/10-Q HTML documents.
   - Extracts MD&A and Risk Factors using section-header regex anchors.
   - Embeds each section and computes cosine similarity across time.
6. **(Optional) Report synthesis**:
   - With OpenAI: GPT produces a concise, CFA-level “Red Flag Report”.
   - Without OpenAI: deterministic fallback generates a structured summary.

---

## Quick Start (Windows / PowerShell)

From the `filing-sentinel` directory:

```powershell
python -m pip install -r requirements.txt
streamlit run app.py
```

Streamlit will print a local URL (usually `http://localhost:8501` or the next available port).

---

## Configuration (API Keys & Compliance)

Filing Sentinel uses **two external services**:

### 1) SEC EDGAR (Required)

The SEC expects automated requests to include a descriptive `User-Agent` with contact info.

- **Variable**: `SEC_USER_AGENT`
- **Example** (placeholder):

```text
SEC_USER_AGENT=FilingSentinel yourname@email.com
```

If you don’t set it, the app uses a default string. It’s better to set your own.

### 2) OpenAI (Optional)

OpenAI is only needed for:

- semantic drift embeddings (MD&A / Risk Factors)
- AI Red Flag Report synthesis

- **Variable**: `OPENAI_API_KEY`
- **Example** (placeholder):

```text
OPENAI_API_KEY=sk-...
```

#### Recommended: use a `.env` file (local only)

1. Copy the example file:

```powershell
copy .env.example .env
```

2. Fill in your values in `.env`.

Important:
- `.env` is ignored via `.gitignore` and should **never** be committed.

---

## Project Layout

```
filing-sentinel/
├── app.py                       # Streamlit UI
├── requirements.txt
├── .env.example                 # Safe template (no real keys)
├── .gitignore                   # Blocks .env + caches
├── .streamlit/
│   └── config.toml              # Theme (navy + gold)
└── filing_sentinel/
    ├── config.py                # Constants + env var loading
    ├── edgar.py                 # SEC client: ticker→CIK, company facts, submissions, filings
    ├── parser.py                # Extract MD&A / Risk Factors from filing HTML
    ├── benford.py               # Benford expected/observed, MAD, chi-square, verdict
    ├── semantic.py              # Embeddings + cosine similarity + disk cache
    └── agent.py                 # GPT report + deterministic fallback
```

---

## Notes on Rate Limits, Caching, and Reliability

- **SEC rate limits**: requests are throttled with a small delay to stay comfortably under 10 req/s.
- **Embedding cache**: embeddings are cached on disk under `.cache/embeddings/` to avoid re-billing and speed up repeat runs.
- **Parsing reality**: SEC filing HTML is inconsistent. Section extraction is best-effort; some filings won’t yield clean MD&A/Risk Factors text.

---

## Troubleshooting

### “Semantic drift skipped: OPENAI_API_KEY is required…”
Set `OPENAI_API_KEY` in your environment or `.env`. Benford’s Law works without it.

### “Ticker not found”
The SEC ticker map only includes certain tickers. Try the company’s primary listing ticker.

### The app starts on a different port
If `8501` is in use, Streamlit will pick the next available port (e.g., `8502`, `8503`).

---

## Security / Secrets Check

This repo is designed to avoid leaking secrets:

- `.env` is in `.gitignore`
- `.env.example` and README show only placeholders (`sk-...`)

Still, before sharing publicly, you should:
- confirm there is **no** `.env` file committed
- search for `sk-` patterns (OpenAI keys) in the project

---

## Disclaimer

Data is sourced from SEC EDGAR. This software is for informational and research purposes only and does not constitute financial advice.
