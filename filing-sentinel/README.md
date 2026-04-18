# Filing Sentinel

**SEC Filing Anomaly Detector** — Detect red flags in public company filings before the market does.

Filing Sentinel pulls structured and unstructured data from SEC EDGAR, runs forensic accounting analytics, and surfaces anomalies through an interactive dashboard.

---

## What It Does

| Analysis | Method | Requires API Key? |
|---|---|---|
| **Benford's Law** | Chi-squared + MAD test on all XBRL-reported financial figures | No |
| **Semantic Drift** | Embedding cosine similarity on MD&A and Risk Factor disclosures over time | Yes (OpenAI) |
| **Red Flag Report** | LLM-synthesized anomaly report combining all signals | Optional (has rule-based fallback) |

### How It Works

1. **Enter a ticker** (e.g. `NVDA`, `META`, `AAPL`)
2. Filing Sentinel fetches all XBRL-reported financial values and recent 10-K/10-Q documents from SEC EDGAR
3. **Benford's Law analysis** checks whether the distribution of leading digits in reported figures matches the expected natural distribution — deviations can indicate data manipulation
4. **Semantic drift analysis** embeds MD&A and Risk Factor sections from consecutive filings and measures how much the language changed — sudden shifts often precede earnings surprises or restatements
5. All signals feed into a **Red Flag Report** — an actionable briefing for professional investors

---

## Quick Start

```bash
# Clone and install
cd filing-sentinel
pip install -r requirements.txt

# (Optional) Set OpenAI key for semantic analysis and AI reports
export OPENAI_API_KEY=sk-...

# Run
streamlit run app.py
```

The dashboard opens at `http://localhost:8501`.

---

## Project Structure

```
filing-sentinel/
├── app.py                       # Streamlit dashboard
├── requirements.txt
├── .streamlit/config.toml       # Dark theme config
└── filing_sentinel/
    ├── __init__.py
    ├── config.py                # API keys, constants
    ├── edgar.py                 # SEC EDGAR API client
    ├── parser.py                # Filing HTML → structured text
    ├── benford.py               # Benford's Law analysis
    ├── semantic.py              # Embedding-based drift detection
    └── agent.py                 # LLM report synthesis
```

---

## Key Design Decisions

- **XBRL-first for Benford's**: Rather than regex-scraping dollar amounts, we pull every structured financial fact from the SEC's XBRL API — this gives us thousands of data points per company with zero parsing error
- **Embedding drift over keyword matching**: Keyword-based approaches miss subtle language shifts; embedding similarity catches changes in *meaning* even when vocabulary is similar
- **Graceful degradation**: The entire Benford's analysis pipeline works without any API key. Semantic drift and AI reports enhance the analysis but aren't required
- **SEC rate-limit compliance**: Built-in 120ms request throttling to stay well within the 10 req/s limit

---

## Configuration

| Environment Variable | Purpose | Required? |
|---|---|---|
| `OPENAI_API_KEY` | Embeddings + GPT report generation | No (Benford's works without it) |
| `SEC_USER_AGENT` | Custom User-Agent for SEC requests | No (has default) |

---

## Tech Stack

- **Backend**: Python, FastAPI patterns
- **Data**: SEC EDGAR XBRL API + full-text filings (free, no auth)
- **NLP**: OpenAI `text-embedding-3-small` for semantic drift
- **Analysis**: scipy (chi-squared), numpy, pandas
- **Visualization**: Plotly (dark-themed)
- **Frontend**: Streamlit
- **AI**: GPT-4o for report synthesis (with deterministic fallback)

---

*Data sourced from SEC EDGAR. Not investment advice.*
